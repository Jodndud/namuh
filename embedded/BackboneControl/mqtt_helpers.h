#pragma once 

// NTP 시간 동기화를 위한 설정
const long gmtOffset_sec = 9 * 3600;
const int daylightOffset_sec = 0;

// ===== WiFi 및 MQTT 함수 =====

// WiFi에 연결하는 함수
void connectWiFi() {
  // 이미 연결되어 있다면 즉시 리턴
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }

  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.disconnect(); 
  WiFi.mode(WIFI_OFF); 
  delay(100);
  WiFi.mode(WIFI_STA);
  
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  
  // 타임아웃 체크 (약 10초)
  int attempt = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    attempt++;
    
    if (attempt > 20) { // 10초 경과
      Serial.println("\nWiFi connection failed (Timeout). Will retry later.");
      return; // 루프를 빠져나가서 메인 루프가 다른 일(재시도 타이머 등)을 하게 해줌
    }
  }
  
  Serial.println("\nWiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // NTP 시간 동기화
  configTime(gmtOffset_sec, daylightOffset_sec, "pool.ntp.org");
  struct tm timeinfo;
  if (getLocalTime(&timeinfo)) {
    Serial.println("Time synchronized");
  }
}

// 주기적 상태 발행 함수 (loop에서 호출됨)
void publishStatus() {
  unsigned long now = millis();
  if (now - lastStatusPublishTime > statusPublishInterval) {
    // 현재 서보 각도 읽기
    int currentNeckYaw = neckYawServo.read();
    int currentNeckPitch = neckPitchServo.read();
    int currentWaistYaw = waistYawServo.read();

    static int prevNeckYaw = -1;
    static int prevNeckPitch = -1;
    static int prevWaistYaw = -1;

    // 각도가 변했을 때만 MQTT 서보 각도 전송
    bool isChanged = (currentNeckYaw != prevNeckYaw) || 
                     (currentNeckPitch != prevNeckPitch) || 
                     (currentWaistYaw != prevWaistYaw);
    
    if (isChanged) {
      lastStatusPublishTime = now;  // 전송 시간 갱신

      // 이전 서보 각도 값 업데이트
      prevNeckYaw = currentNeckYaw;
      prevNeckPitch = currentNeckPitch;
      prevWaistYaw = currentWaistYaw;

      StaticJsonDocument<200> doc;
      doc["type"] = "joint_state"; 
      doc["robot_id"] = "robot_backbone"; // HTML에서 사용할 ID
      JsonArray angles = doc.createNestedArray("angles");
      angles.add(neckYawServo.read());
      angles.add(neckPitchServo.read());
      angles.add(waistYawServo.read());

      char buffer[128];
      serializeJson(doc, buffer);

      mqttClient.publish(PUB_TOPIC_JOINT, buffer);
    }
  }
}

// MQTT 메시지 수신 시 호출될 콜백 함수
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  // payload를 문자열로 복사 (로그 출력보다 먼저 수행되어야 함)
  char msg[length + 1];
  memcpy(msg, payload, length);
  msg[length] = '\0';

  // JSON 파싱
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, msg);

  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    return;
  }

  // MQTT SPEC에 따라 type과 command를 확인
  const char* type = doc["type"] | "";
  if (strcmp(type, "command") != 0) {
    return; // "command" 타입이 아니면 무시
  }
  
  const char* cmd = doc["command"] | "";

  if (strcmp(cmd, "set_joint") == 0) {
    if (doc.containsKey("id") && doc.containsKey("angle") && doc.containsKey("time_ms")) {
      targetServoId = doc["id"];
      targetAngle = doc["angle"];
      moveTimeMs = doc["time_ms"];
    }
  }

  // track_face 또는 track_lost 명령이 아닐 때만 전체 메시지 로그를 출력
  if (strcmp(cmd, "track_face") != 0 && strcmp(cmd, "track_lost") != 0) {
    Serial.print("Message arrived [");
    Serial.print(topic);
    Serial.print("] ");
    Serial.println(msg);
  }

  // ============================================================
  // 트래킹 관련 분기 처리
  // ============================================================
  
  // Case A: 얼굴 추적 (track_face)
  // 매우 자주 오므로 moveInitPose() 호출 금지
  if (strcmp(cmd, "track_face") == 0) {
    isIdle = false;             
    lastCommandTime = millis(); 
    currentAction = ACTION_TRACKING; 
    actionStep = 0; // 트래킹 중에는 다른 액션 step이 간섭하지 않도록 초기화

    if (doc.containsKey("x") && doc.containsKey("y")) {
      trackingTargetX = doc["x"];
      trackingTargetY = doc["y"];
    }
    return; // 바로 리턴
  }

  // Case B: 얼굴 놓침 (track_lost)
  if (strcmp(cmd, "track_lost") == 0) {
    if (currentAction == ACTION_TRACKING) {
      Serial.println("Target lost. Stopping at current pose.");
      detachWaistServo(); // 허리 서보 전원 차단
      currentAction = ACTION_NONE; 
      isIdle = true;            
    }
    return;
  }
  // Case C: 일반 명령어
  
  // 어떤 액션을 시작하기 전에는, 진행중인 모든 애니메이션을 멈춤
  for (int i=0; i<3; i++) {
    servoAnims[i].isMoving = false;
  }
  
  // 현재 어떤 액션을 하고 있었는지 기록 (이전 액션 저장)
  ActionType previousAction = currentAction;

  Serial.println("Received normal command. Stopping idle mode...");
  attachAllServos(); // 명령 수행 전 서보 전원 인가
  isIdle = false;
  lastCommandTime = millis();   

  // 실제 명령을 바로 실행하는 대신, '선-정렬' 동작을 실행하도록 설정
  strncpy(pendingCommandPayload, msg, sizeof(pendingCommandPayload) - 1);
  pendingCommandPayload[sizeof(pendingCommandPayload) - 1] = '\0';
  hasPendingCommand = true;
  
  currentAction = ACTION_ALIGN_THEN_EXECUTE;
  actionStep = 0;
}


// MQTT 브로커에 연결하고 토픽을 구독하는 함수
void ensureMqttConnected() {
  if (mqttClient.connected()) {
    return;
  }

  // MQTT 연결 시도 전에 WiFi 연결 상태 확인
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected. Skipping MQTT connection attempt.");
    return;
  }
  
  Serial.print("Attempting MQTT connection...");

  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  mqttClient.setCallback(mqttCallback); // 이 파일 안에 있는 mqttCallback 지정

  // TLS 설정
  #if defined(MQTT_TLS) && MQTT_TLS && defined(MQTT_TLS_INSECURE) && MQTT_TLS_INSECURE
    espClient.setInsecure(); // 개발용: 서버 인증서 검증 안함
  #endif

  // 클라이언트 ID를 ESP32의 MAC 주소 기반으로 생성
  String clientId = "servo-esp32-";
  clientId += String((uint32_t)ESP.getEfuseMac(), HEX);

  // 현재 시간을 Last Will and Testament(LWT) 메시지에 사용 (필요하다면 활성화)
  /*
  char lastWillMessage[64];
  struct tm timeinfo;
  if (getLocalTime(&timeinfo)) {
    strftime(lastWillMessage, sizeof(lastWillMessage), "Disconnected at %H:%M:%S", &timeinfo);
  } else {
    strcpy(lastWillMessage, "Disconnected (time sync failed)");
  }
  */

  Serial.printf("\nConnecting to MQTT broker: %s:%d\n", MQTT_HOST, MQTT_PORT);
  if (mqttClient.connect(clientId.c_str(), MQTT_USERNAME, MQTT_PASSWORD /*, LWT_TOPIC, LWT_QOS, LWT_RETAIN, lastWillMessage */ )) {
    Serial.println("connected");
    // 구독할 토픽 설정
    mqttClient.subscribe(SUB_TOPIC); // 공용 토픽
    mqttClient.subscribe(SUB_TOPIC_BACKBONE); // 백본 전용 토픽(얼굴 추적)
    Serial.print("Subscribed to: ");
    Serial.println(SUB_TOPIC);
    Serial.print("Subscribed to: ");
    Serial.println(SUB_TOPIC_BACKBONE);
  } else {
    Serial.print("failed, rc=");
    Serial.print(mqttClient.state());
    if (mqttClient.state() == -2) {
      Serial.println(" (MQTT_CONNECT_FAILED). Please check MQTT broker address, port, and network connectivity.");
    } else {
      Serial.println(" try again in 5 seconds");
    }
    // 5초 후 재시도 (loop()에서 재시도 타이머가 관리함)
  }
}