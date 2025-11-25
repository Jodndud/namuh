#pragma once

// ===== WiFi =====
#define WIFI_SSID        "E108"
#define WIFI_PASS        "08080808"

// ===== MQTT =====
// SSL 브로커 사용 예:
//   mqtt_broken_url: ssl://buriburi.monster:8883
//   mqtt_username:   buriburi
//   mqtt_password:   
#define MQTT_HOST        "buriburi.monster"   // 브로커 호스트명/IP
#define MQTT_PORT        8883                  // SSL MQTT 포트
#define MQTT_TLS         1                     // 1=TLS 사용, 0=비활성
#define MQTT_TLS_INSECURE 1                    // 1=서버 인증서 검증 생략(개발용)
#define MQTT_USERNAME    "buriburi"
#define MQTT_PASSWORD    ""
#define BASE_TOPIC       "buriburi"           // 프론트/로봇과 동일한 base

// 로봇 명령을 그대로 듣고 싶으면 ROBOT_RX 를 사용합니다.
#define SUB_TOPIC_ROBOT  BASE_TOPIC "/robot/rx"
// 얼굴 전용 토픽을 쓰고 싶으면 FACE_RX 를 사용하고, 코드에서 선택하세요.
#define SUB_TOPIC_FACE   BASE_TOPIC "/face/rx"

// ===== LED(MATRIX) =====
#define LED_PIN          5
#define LED_CHIPSET      WS2812B
#define LED_COLOR_ORDER  GRB
#define LED_BRIGHTNESS   25
#define MATRIX_W         16
#define MATRIX_H         16
#define SERPENTINE       1   // 1: 지그재그, 0: 고정 방향
