#pragma once
#include <ArduinoJson.h>

// 다른 파일에 정의된 함수를 사용하기 위한 전방 선언
void executeCommand(const char* cmd, const JsonDocument& doc);


#include "globals.h" // 전역 변수 사용을 위해 포함
#include "config.h"

// ===== 함수 전방 선언 (Forward Declarations) =====
void moveInitPoseWithDuration(unsigned long duration);
void moveInitPose();
void handleCommand();
void initServos();
void attachAllServos();
void detachWaistServo();
void safeWriteNeckPitch(int angle);
void safeWriteNeckYaw(int angle);
void safeWriteWaistYaw(int angle);
void handleHelloAction();
void handleNodAction();
void handleShakeHeadAction();
void handleMakeHeartAction();
void handleMakeHugAction();
void handleScissorsAction();
void handleRockAction();
void handlePaperAction();
void handleAteAllAction();
void handleSetJointAction();
void handleCallToriAction();
void handleTrackingAction();
void handleAlignThenExecuteAction();
void stopCurrentAction(bool moveToInit = true);
void handleLookingCenterAction();

// ===== 애니메이션 엔진 함수 =====
void moveTo(int servoIndex, float targetAngle, unsigned long duration) {
  if (servoIndex < 0 || servoIndex > 2) return;

  servoAnims[servoIndex].startAngle = servoAnims[servoIndex].currentAngle;
  servoAnims[servoIndex].targetAngle = targetAngle;
  servoAnims[servoIndex].startTime = millis();
  servoAnims[servoIndex].duration = duration;
  servoAnims[servoIndex].isMoving = true;
}

bool isMoving() {
  return servoAnims[0].isMoving || servoAnims[1].isMoving || servoAnims[2].isMoving;
}

void updateServoAnimations() {
  unsigned long now = millis();
  for (int i = 0; i < 3; i++) {
    if (!servoAnims[i].isMoving) continue;

    float progress = (float)(now - servoAnims[i].startTime) / servoAnims[i].duration;
    
    if (progress >= 1.0) {
      progress = 1.0;
      servoAnims[i].isMoving = false;
    }

    float easedProgress = easeInOutCubic(progress);
    servoAnims[i].currentAngle = servoAnims[i].startAngle + (servoAnims[i].targetAngle - servoAnims[i].startAngle) * easedProgress;

    if (i == 0) safeWriteNeckYaw(servoAnims[i].currentAngle);
    else if (i == 1) safeWriteNeckPitch(servoAnims[i].currentAngle);
    else if (i == 2) safeWriteWaistYaw(servoAnims[i].currentAngle);
  }
}

// ===== 핵심 서보 유틸리티 함수 =====

// setup()에서 호출할 서보 초기화 함수
void initServos() {
  Serial.println("[INIT] Attaching all servos...");
  attachAllServos();
  
  // Move to initial pose synchronously for the first time
  safeWriteNeckYaw(SERVO_NECK_YAW_INIT);
  safeWriteNeckPitch(SERVO_NECK_PITCH_INIT);
  safeWriteWaistYaw(SERVO_WAIST_YAW_INIT);

  // Set initial angles for animation engine state
  servoAnims[0].currentAngle = SERVO_NECK_YAW_INIT;
  servoAnims[1].currentAngle = SERVO_NECK_PITCH_INIT;
  servoAnims[2].currentAngle = SERVO_WAIST_YAW_INIT;
  
  delay(500); // Give time for servos to move

  Serial.println("[INIT] Detaching waist servo to prevent overheating...");
  detachWaistServo();
}

// 모든 서보의 전원을 인가하는 함수
void attachAllServos() {
  if (!neckYawServo.attached()) neckYawServo.attach(SERVO_PIN_NECK_YAW);
  if (!neckPitchServo.attached()) neckPitchServo.attach(SERVO_PIN_NECK_PITCH);
  if (!waistYawServo.attached()) waistYawServo.attach(SERVO_PIN_WAIST_YAW);
}

// 허리 서보의 전원만 차단하는 함수
void detachWaistServo() {
  if (waistYawServo.attached()) waistYawServo.detach();
}

void moveInitPose() {
  moveInitPoseWithDuration(1000); // 기본 시간으로 duration 버전 호출
}

// 초기 자세로 이동
void moveInitPoseWithDuration(unsigned long duration) {
  attachAllServos(); // 움직이기 전에 항상 서보 전원을 확인하고 인가합니다.
  Serial.println("[INIT] Moving to initial pose...");
  moveTo(0, SERVO_NECK_YAW_INIT, duration); // 하드코딩된 값 대신 duration 변수 사용
  moveTo(1, SERVO_NECK_PITCH_INIT, duration);
  moveTo(2, SERVO_WAIST_YAW_INIT, duration + 200); // 허리는 조금 더 느리게
}

// ===== 안전 장치(Safety Features) =====
// 서보의 물리적 한계를 넘어선 명령을 막는 함수
void safeWriteNeckPitch(int angle) {
  // config.h에 정의된 최소/최대 각도로 값을 제한
  int constrainedAngle = constrain(angle, SERVO_NECK_PITCH_MIN, SERVO_NECK_PITCH_MAX);
  
  // 만약 요청된 각도가 제한 범위를 벗어났다면, 경고 로그를 출력
  if (angle != constrainedAngle) {
    Serial.printf("[SAFETY] Neck Pitch angle %d was constrained to %d (valid range: %d-%d)\n", angle, constrainedAngle, SERVO_NECK_PITCH_MIN, SERVO_NECK_PITCH_MAX);
  }
  
  neckPitchServo.write(constrainedAngle);
}

// Yaw 서보를 위한 안전 장치
void safeWriteNeckYaw(int angle) {
  int constrainedAngle = constrain(angle, SERVO_NECK_YAW_MIN, SERVO_NECK_YAW_MAX);
  if (angle != constrainedAngle) {
    Serial.printf("[SAFETY] Neck Yaw angle %d was constrained to %d (valid range: %d-%d)\n", angle, constrainedAngle, SERVO_NECK_YAW_MIN, SERVO_NECK_YAW_MAX);
  }
  neckYawServo.write(constrainedAngle);
}

// Waist 서보를 위한 안전 장치
void safeWriteWaistYaw(int angle) {
  int constrainedAngle = constrain(angle, SERVO_WAIST_YAW_MIN, SERVO_WAIST_YAW_MAX);
  if (angle != constrainedAngle) {
    Serial.printf("[SAFETY] Waist Yaw angle %d was constrained to %d (valid range: %d-%d)\n", angle, constrainedAngle, SERVO_WAIST_YAW_MIN, SERVO_WAIST_YAW_MAX);
  }
  waistYawServo.write(constrainedAngle);
}

// ===== 액션 중지 유틸리티 =====
void stopCurrentAction(bool moveToInit) {
  if (currentAction != ACTION_NONE) {
    currentAction = ACTION_NONE;
    actionStep = 0;
    
    if (moveToInit) {
      Serial.printf("[ACTION] Stopping action. Returning to init pose.\n");
      moveInitPose();
    } else {
      Serial.printf("[ACTION] Ignoring command and continuing idle.\n");
      // moveInitPose()를 호출하지 않아 현재 자세에서 바로 다음 idle 동작으로 넘어감
    }
  }
}

// ===== 액션 라우터 =====
// loop()에서 호출되며, 현재 액션에 따라 분기
void handleCommand() {
  lastCommandTime = millis(); // 타임아웃 갱신

  switch (currentAction) {
    case ACTION_HELLO:
      handleHelloAction();
      break;
    case ACTION_NOD:
      handleNodAction();
      break;
    case ACTION_SHAKE:
      handleShakeHeadAction();
      break;
    case ACTION_MAKE_HEART:
      handleMakeHeartAction();
      break;
    case ACTION_MAKE_HUG:
      handleMakeHugAction();
      break;
    case ACTION_SCISSORS:
      handleScissorsAction();
      break;
    case ACTION_ROCK:
      handleRockAction();
      break;
    case ACTION_PAPER:
      handlePaperAction();
      break;
    case ACTION_ATE_ALL:
      handleAteAllAction();
      break;
    case ACTION_CALL_TORI: 
      handleCallToriAction();
      break;
    case ACTION_ALIGN_THEN_EXECUTE:
      handleAlignThenExecuteAction();
      break;
    case ACTION_TRACKING: 
      handleTrackingAction();
      break;
    case ACTION_LOOKING_CENTER:
      handleLookingCenterAction();
      break;
    case ACTION_STOP:
      stopCurrentAction(true); // 즉시 모든 동작을 멈추고 init pose로 복귀
      break;
    case ACTION_NONE:
    default:
      break;
  }
}

// ===== 선-정렬, 후-동작 처리 =====
void handleAlignThenExecuteAction() {
    switch(actionStep) {
        case 0:
            if (!hasPendingCommand) {
                currentAction = ACTION_NONE;
                return;
            }
            Serial.println("[PRE-ACTION] Aligning neck to waist...");
            moveTo(0, servoAnims[2].currentAngle, 300); // 목(0)을 허리(2) 각도로 정렬
            actionStep = 1;
            break;
        case 1:
            if (!isMoving()) {
                if (hasPendingCommand) {
                    hasPendingCommand = false; // 대기 명령 소비
                    
                    StaticJsonDocument<256> doc;
                    if (deserializeJson(doc, pendingCommandPayload).code() == DeserializationError::Ok) {
                        const char* cmd = doc["command"] | "";
                        actionStep = 0; 
                        executeCommand(cmd, doc); // 저장해둔 실제 명령 실행
                    } else {
                        Serial.println("Failed to parse pending command.");
                        currentAction = ACTION_NONE;
                    }
                } else {
                    currentAction = ACTION_NONE;
                }
            }
            break;
    }
}


// ===== 개별 동작 구현부 =====
#include "actions/action_idle_move.h"

#include "actions/action_hello.h"
#include "actions/action_nod.h"
#include "actions/action_shake.h"
#include "actions/action_make_heart.h"
#include "actions/action_make_hug.h"
#include "actions/action_scissors.h"
#include "actions/action_rock.h"
#include "actions/action_paper.h"
#include "actions/action_ate_all.h"
#include "actions/action_set_joint.h"

#include "actions/action_call_tori.h"
#include "actions/action_looking_center.h"

#include "actions/action_face_tracking.h"