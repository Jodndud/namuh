#pragma once

// ===== Private Credentials =====
#include "secrets.h"
// #define WIFI_SSID        // WiFi 네트워크 이름
// #define WIFI_PASS        // WiFi 비밀번호
// #define MQTT_HOST        // 브로커 호스트명/IP
// #define MQTT_PORT        // SSL MQTT 포트
// #define MQTT_USERNAME    // 브로커 사용자 이름
// #define MQTT_PASSWORD    // 브로커 사용자 비밀번호

// ===== MQTT =====
#define MQTT_TLS            1                           // 1=TLS 사용, 0=비활성
#define MQTT_TLS_INSECURE   1                           // 1=서버 인증서 검증 생략(개발용)
#define BASE_TOPIC          "buriburi"                  // 기본 토픽
// 구독할 토픽 (로봇 명령 채널)
#define SUB_TOPIC           BASE_TOPIC "/robot/all/command"
#define SUB_TOPIC_BACKBONE  BASE_TOPIC "/robot/robot_backbone/command" // 백본 전용 명령 토픽
#define PUB_TOPIC_JOINT     BASE_TOPIC "/robot/joint"   // 상태 발행(Publish) 토픽(수동 제어 시 사용)

// ===== Servo Motors =====
// 서보모터를 연결한 ESP32의 GPIO 핀 번호

// --- 목 제어 ---
#define SERVO_PIN_NECK_YAW   16     // 목 좌우 회전 (Pan)
#define SERVO_PIN_NECK_PITCH 17     // 목 상하 끄덕임 (Tilt)
// --- 몸통 제어 ---
#define SERVO_PIN_WAIST_YAW  18     // 허리 좌우 회전 (Pan)

// ===== Servo Physical Limits =====
// 로봇의 물리적 파손을 막기 위한 서보 각도 제한
#define SERVO_NECK_YAW_MIN   10     // 목 좌우 최소 각도
#define SERVO_NECK_YAW_MAX   170    // 목 좌우 최대 각도
#define SERVO_NECK_PITCH_MIN 45     // 목 상하 최소 각도 (너무 높이 들면 부딪힘)
#define SERVO_NECK_PITCH_MAX 110    // 목 상하 최대 각도 (너무 숙이면 부딪힘)

// --- 허리 제어 ---
#define SERVO_WAIST_YAW_MIN  60     // 허리 좌우 최소 각도
#define SERVO_WAIST_YAW_MAX  120    // 허리 좌우 최대 각도

// ===== Initial Pose =====
#define SERVO_NECK_YAW_INIT   90
#define SERVO_NECK_PITCH_INIT 75
#define SERVO_WAIST_YAW_INIT  90

// ===== Actions =====
#define MEDIAPIPE_ACTION_DELAY 7000  // 포즈 인식 액션 시작 전 지연 시간 (ms)