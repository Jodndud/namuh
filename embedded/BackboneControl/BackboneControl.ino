#include <Arduino.h>
#include "config.h" 
#include "globals.h" // 모든 전역 변수 선언을 포함

#include <WiFi.h>
#if defined(MQTT_TLS) && MQTT_TLS
#include <WiFiClientSecure.h>
#else
#include <WiFiClient.h>
#endif
#include <PubSubClient.h>
#include <ArduinoJson.h>

// MQTT 클라이언트 객체
#if defined(MQTT_TLS) && MQTT_TLS
WiFiClientSecure espClient;
#else
WiFiClient espClient;
#endif
PubSubClient mqttClient(espClient);

// 상태 발행 타이머
unsigned long lastStatusPublishTime = 0;
const long statusPublishInterval = 250; // 0.25초

// 서보모터 객체
Servo neckYawServo;
Servo neckPitchServo;
Servo waistYawServo;

// IDLE/COMMAND 상태 관리
bool isIdle = true;
unsigned long lastIdleMoveTime = 0;
unsigned long lastCommandTime = 0;
unsigned long nextIdleMoveInterval = 5000;
const long idleMinInterval = 3000;
const long idleMaxInterval = 8000;
const long commandTimeoutInterval = 10000;

// 비동기 액션(동작) 관리
ActionType currentAction = ACTION_NONE;
int actionStep = 0;
unsigned long actionLastStepTime = 0;

// set_joint 액션을 위한 전역 변수 정의
int targetServoId = 0;
int targetAngle = 90;
int moveTimeMs = 0;

// 트래킹 변수 초기화
float trackingTargetX = 0.5;
float trackingTargetY = 0.5;

// ===== 정렬을 위한 명령 대기 변수 =====
char pendingCommandPayload[256];
bool hasPendingCommand = false;

// ===== 애니메이션 엔진 상태 변수 =====
ServoAnimation servoAnims[3];

// ===== 로직 파일 =====
#include "Animation.h"
#include "servo_actions.h"
#include "command_mapper.h"
#include "mqtt_helpers.h"

// ===== setup() 및 loop() =====

void setup() {
  Serial.begin(115200);
  delay(100);

  randomSeed(analogRead(36)); // 랜덤 시드 초기화

  Serial.println("ESP32 Neck Servo Control via MQTT (Multi-File)");

  delay(100);
  // 서보모터 초기화 (servo_actions.h)
  initServos();

  // WiFi 및 MQTT 연결 (mqtt_helpers.h)
  connectWiFi();

  // 첫 IDLE 타이머 시작
  lastIdleMoveTime = millis();
}

void loop() {
  // WiFi 끊김 체크
  if (WiFi.status() != WL_CONNECTED) {
    // 10초마다 재연결 시도
    static unsigned long lastWifiReconnectAttempt = 0;
    if (millis() - lastWifiReconnectAttempt > 10000) {
      lastWifiReconnectAttempt = millis();
      connectWiFi(); // mqtt_helpers.h 에 있는 함수
    }
    return; // WiFi 없으면 동작 중지
  }

  // MQTT 연결 확인
  if (!mqttClient.connected()) {
    static unsigned long lastMqttReconnectAttempt = 0;
    if (millis() - lastMqttReconnectAttempt > 5000) {
      lastMqttReconnectAttempt = millis();
      ensureMqttConnected(); // WiFi가 연결된 상태에서만 호출됨
    }
  } else {
    // 연결된 경우 메시지 루프 처리 및 상태 발행
    mqttClient.loop();
    publishStatus();
  }

  // ===== 애니메이션 및 상태 업데이트 =====
  updateServoAnimations();

  // ===== 메인 상태 머신 로직 =====
  // (로직은 servo_actions.h의 함수들을 호출)
  if (isIdle) { // IDLE 모드
    if (millis() - lastIdleMoveTime > nextIdleMoveInterval) {
      performIdleMove();
    }
  } else { // COMMAND 모드
    // 현재 진행 중인 액션(동작)이 있는지 확인
    if (currentAction != ACTION_NONE) {
      handleCommand();
    }
    
    // 타임아웃 체크
    if (millis() - lastCommandTime > commandTimeoutInterval) {
      Serial.println("Command timeout. Stopping at current pose.");
      detachWaistServo(); // 허리 서보 전원 차단
      isIdle = true;
      currentAction = ACTION_NONE; // 액션 강제 중지
      actionStep = 0;
      lastIdleMoveTime = millis();
      nextIdleMoveInterval = random(idleMinInterval, idleMaxInterval + 1);
    }
  }
}