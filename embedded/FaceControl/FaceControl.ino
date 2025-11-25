#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
// FastLED가 ESP32에서 기본 RMT 백엔드를 쓰다가 RMT 인터럽트 자원 부족 에러가 날 수 있어
// I2S 백엔드로 강제 전환합니다. (RMT 충돌 회피)
#define FASTLED_ESP32_I2S 1
#define FASTLED_RMT_MAX_CHANNELS 1
#include <FastLED.h>
#include <ArduinoJson.h>

#include "config.h" // 사용자 설정 (config.example.h를 복사해 config.h로 사용)
#include "expressions.h"

// ===== LED setup =====
#ifndef MATRIX_W
#define MATRIX_W 16
#endif
#ifndef MATRIX_H
#define MATRIX_H 16
#endif
#ifndef LED_PIN
#define LED_PIN 5
#endif
#ifndef LED_CHIPSET
#define LED_CHIPSET WS2812B
#endif
#ifndef LED_COLOR_ORDER
#define LED_COLOR_ORDER GRB
#endif
#ifndef LED_BRIGHTNESS
#define LED_BRIGHTNESS 10
#endif

#ifndef FPS
#define FPS 30  // 안정적 표현을 위해 기본 30fps 권장
#endif

#define NUM_LEDS (MATRIX_W * MATRIX_H)
CRGB leds[NUM_LEDS];
CRGB *getLedsPtr() { return leds; }
CRGB ledsAlias[1]; // dummy to silence -Wweak-vtables on some toolchains
CRGB * __attribute__((weak)) ledsExtern = leds; // referenced by expressions.h via extern

// ===== WiFi/MQTT =====
#if defined(MQTT_TLS) && MQTT_TLS
WiFiClientSecure espClient;
#else
WiFiClient espClient;
#endif
PubSubClient mqttClient(espClient);

// 구독 토픽: 기본은 로봇 명령 채널 사용
static const char *kSubTopic = SUB_TOPIC_ROBOT; // 필요 시 SUB_TOPIC_FACE로 교체

// 상태/표정 관리
volatile uint8_t gExpr = EXPR_NEUTRAL;
uint32_t gLastExprAt = 0;
uint32_t gFrame = 0;

// 눈 깜빡임(blink) 상태
static uint32_t gNextBlinkAt = 0;     // 다음 깜빡임 시작 시각(ms)
static uint8_t  gBlinkStep = 0;       // 0: 비활성, 1~3: 단계 애니메이션
static uint32_t gBlinkLastStepAt = 0; // 최근 단계 전환 시각(ms)
static const uint16_t BLINK_STEP_MS = 60; // 각 단계 지속 시간

static inline bool isBlinkingExpr(uint8_t expr) {
  // 초기화 이후의 기본 표정에서만 깜빡임 반복 (NEUTRAL/HAPPY)
  return (expr == EXPR_NEUTRAL) || (expr == EXPR_HAPPY);
}

static void scheduleNextBlink() {
  // 2.0s ~ 6.0s 사이 랜덤 간격
  gNextBlinkAt = millis() + random(2000, 6001);
}

static void overlayBlink(uint8_t step) {
  // 눈 좌표 기준: drawEye가 사용하는 4x4 박스의 중앙 부근에 검은 선을 그려 닫히는 느낌 구현
  // 좌안(4..7, 5..8), 우안(10..13, 5..8)
  // step 1: 반쯤, step 2: 완전 닫힘, step 3: 반쯤 (열림)
  if (step == 0) return;
  uint8_t y1 = 7; // 중앙 라인
  uint8_t y0 = 6; // 한 줄 위
  // 왼쪽 눈
  for (uint8_t x = 4; x <= 7; ++x) {
    if (step >= 1) setPixel(x, y1, CRGB::Black);
    if (step >= 2) setPixel(x, y0, CRGB::Black);
  }
  // 오른쪽 눈
  for (uint8_t x = 10; x <= 13; ++x) {
    if (step >= 1) setPixel(x, y1, CRGB::Black);
    if (step >= 2) setPixel(x, y0, CRGB::Black);
  }
}

// ===== Helpers =====
void setExpression(uint8_t expr) {
  gExpr = expr;
  gLastExprAt = millis();
  // 깜빡임 상태 초기화/스케줄링
  if (isBlinkingExpr(gExpr)) {
    gBlinkStep = 0;
    scheduleNextBlink();
  } else {
    gBlinkStep = 0;
    gNextBlinkAt = 0;
  }
}

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("WiFi connecting");
  uint32_t start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(200);
    Serial.print(".");
    if (millis() - start > 15000) break;
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("WiFi OK: "); Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi FAILED");
  }
}

void ensureMqttConnected() {
  if (mqttClient.connected()) return;
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  // TLS 보안 설정 (ESP32)
#if defined(MQTT_TLS) && MQTT_TLS
  #if defined(MQTT_TLS_INSECURE) && MQTT_TLS_INSECURE
    espClient.setInsecure(); // 개발/테스트용. 운영환경에선 CA를 설정하세요.
  #elif defined(MQTT_CA_CERT)
    espClient.setCACert(MQTT_CA_CERT);
  #endif
#endif
  mqttClient.setCallback([](char *topic, byte *payload, unsigned int length){
    // MQTT message handler
    StaticJsonDocument<512> doc;
    DeserializationError err = deserializeJson(doc, payload, length);
    if (err) {
      // ignore non-json
      return;
    }
    const char* type = doc["type"] | "";
    if (strcmp(type, "command") != 0) return;
    const char* cmd = doc["command"] | "";

    if (strcmp(cmd, "start_face_tracking") == 0) {
      setExpression(EXPR_TRACKING);
    } else if (strcmp(cmd, "stop_face_tracking") == 0) {
      setExpression(EXPR_NEUTRAL);
    } else if (strcmp(cmd, "init_pose") == 0) {
      setExpression(EXPR_HAPPY);
    } else if (strcmp(cmd, "make_heart") == 0) {
      setExpression(EXPR_HEART);
    } else if (strcmp(cmd, "make_hug") == 0) {
      setExpression(EXPR_HUG);
    } else if (strcmp(cmd, "hello") == 0 || strcmp(cmd, "make_hello") == 0) {
      setExpression(EXPR_HELLO);
    } else if (strcmp(cmd, "scissors") == 0) {
      setExpression(EXPR_SCISSORS);
    } else if (strcmp(cmd, "rock") == 0) {
      setExpression(EXPR_ROCK);
    } else if (strcmp(cmd, "paper") == 0) {
      setExpression(EXPR_PAPER);
    } else if (strcmp(cmd, "good_morning") == 0) {
      setExpression(EXPR_GOOD_MORNING);
    } else if (strcmp(cmd, "good_night") == 0) {
      setExpression(EXPR_GOOD_NIGHT);
    } else if (strcmp(cmd, "hungry") == 0) {
      setExpression(EXPR_HUNGRY);
    } else if (strcmp(cmd, "ate_all") == 0) {
      setExpression(EXPR_ATE_ALL);
    } else if (strcmp(cmd, "set_joint") == 0 || strcmp(cmd, "set_joints") == 0 || strcmp(cmd, "nudge_joint") == 0) {
      setExpression(EXPR_THINKING);
    } else if (strcmp(cmd, "start_follow") == 0) {
      setExpression(EXPR_FOLLOW_ON);
    } else if (strcmp(cmd, "end_follow") == 0) {
      setExpression(EXPR_NEUTRAL);
    }
  });

  Serial.print("MQTT connecting");
  while (!mqttClient.connected()) {
    String cid = String("face-esp32-") + String((uint32_t)ESP.getEfuseMac(), HEX);
    bool ok = false;
#if defined(MQTT_USERNAME)
    ok = mqttClient.connect(cid.c_str(), MQTT_USERNAME, MQTT_PASSWORD);
#else
    ok = mqttClient.connect(cid.c_str());
#endif
    if (ok) {
      mqttClient.subscribe(kSubTopic);
      Serial.print("\nsubscribed: "); Serial.println(kSubTopic);
      break;
    } else {
      Serial.print("."); delay(1000);
      if (WiFi.status() != WL_CONNECTED) break;
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(100);
  FastLED.addLeds<LED_CHIPSET, LED_PIN, LED_COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(LED_BRIGHTNESS);
  // WS2812B 저밝기에서 보이는 반짝임(시간적 디더링)을 줄이기 위해 디더링 비활성화
  FastLED.setDither(false);
  // 과도한 갱신으로 인한 잔상/깜빡임 방지를 위해 최대 리프레시 제한(Hz)
  FastLED.setMaxRefreshRate(100);
  clearAll(); FastLED.show();

  connectWiFi();
  ensureMqttConnected();

  // 랜덤 시드 초기화 (ESP32 하드웨어 난수)
  randomSeed(esp_random());
  if (isBlinkingExpr(gExpr)) scheduleNextBlink();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }
  if (!mqttClient.connected()) {
    ensureMqttConnected();
  }
  mqttClient.loop();

  // 애니메이션 렌더링
  renderExpression(gExpr, gFrame++);
  // 깜빡임 오버레이: NEUTRAL/HAPPY에서만 동작
  if (isBlinkingExpr(gExpr)) {
    uint32_t now = millis();
    if (gBlinkStep == 0) {
      if (gNextBlinkAt != 0 && now >= gNextBlinkAt) {
        gBlinkStep = 1;
        gBlinkLastStepAt = now;
      }
    } else {
      if (now - gBlinkLastStepAt >= BLINK_STEP_MS) {
        gBlinkLastStepAt = now;
        gBlinkStep++;
        if (gBlinkStep > 3) {
          gBlinkStep = 0;
          scheduleNextBlink();
        }
      }
    }
    if (gBlinkStep > 0) overlayBlink(gBlinkStep);
  }
  FastLED.show();
  FastLED.delay(1000 / FPS);

  // 연결 상태 경고: 오래 끊겨 있으면 에러 표정으로 전환
  static uint32_t lastCheck = 0;
  if (millis() - lastCheck > 2000) {
    lastCheck = millis();
    if (WiFi.status() != WL_CONNECTED || !mqttClient.connected()) {
      setExpression(EXPR_ERROR);
    }
  }
}
