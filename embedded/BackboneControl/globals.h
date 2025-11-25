#pragma once

// ===== 공용으로 사용되는 전역 변수 및 타입 정의 =====

// 비동기 액션(동작) 관리
enum ActionType {
  ACTION_NONE,
  ACTION_HELLO,
  ACTION_NOD,
  ACTION_SHAKE,
  ACTION_MAKE_HEART,
  ACTION_MAKE_HUG,
  ACTION_SCISSORS,
  ACTION_ROCK,
  ACTION_PAPER,
  ACTION_ATE_ALL,
  ACTION_SET_JOINT,
  ACTION_CALL_TORI,
  ACTION_ALIGN_THEN_EXECUTE, // 정렬 후 다음 명령을 실행하는 메타 액션
  ACTION_TRACKING,   // 얼굴 트래킹 모드
  ACTION_LOOKING_CENTER, // 중앙 응시 모드
  ACTION_STOP // 현재 액션 중지
};

extern ActionType currentAction;
extern int actionStep;
extern unsigned long actionLastStepTime;

// IDLE/COMMAND 상태 관리 변수
extern bool isIdle;
extern unsigned long lastIdleMoveTime;
extern unsigned long lastCommandTime;
extern unsigned long nextIdleMoveInterval;
extern const long idleMinInterval;
extern const long idleMaxInterval;
extern const long commandTimeoutInterval;

// set_joint 액션을 위한 전역 변수
extern int targetServoId;
extern int targetAngle;
extern int moveTimeMs;

// 트래킹을 위한 전역 변수
extern float trackingTargetX; // 0.0 ~ 1.0
extern float trackingTargetY; // 0.0 ~ 1.0

// ===== 정렬을 위한 명령 대기 =====
extern char pendingCommandPayload[256];
extern bool hasPendingCommand;

// ===== 애니메이션 엔진 =====
struct ServoAnimation {
  bool isMoving;
  float currentAngle;
  float startAngle;
  float targetAngle;
  unsigned long startTime;
  unsigned long duration;
};

extern ServoAnimation servoAnims[3]; // 0: Neck Yaw, 1: Neck Pitch, 2: Waist Yaw

#include <ESP32Servo.h>
extern Servo neckYawServo;
extern Servo neckPitchServo;
extern Servo waistYawServo;