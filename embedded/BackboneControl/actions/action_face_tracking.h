#pragma once
#include "../config.h"
#include "../utils/action_utils.h"

void handleTrackingAction() {
  static const char* ACTION_NAME = "Face Tracking";

  // Yaw (좌우): 반대로 뒤집음
  int DIR_YAW = -1;    
  
  // Pitch (상하): 반대로 뒤집음
  int DIR_PITCH = -1; 
  // ----------------------------------------------------------

  // 업데이트 주기 관리
  static unsigned long lastTrackingUpdateTime = 0;
  const unsigned int trackingUpdateInterval = 30; 
  
  unsigned long now = millis();
  if (now - lastTrackingUpdateTime < trackingUpdateInterval) {
    return;
  }
  lastTrackingUpdateTime = now;

  // 오차 계산
  float errorX = trackingTargetX - 0.5;
  float errorY = trackingTargetY - 0.5;

  float deadzone = 0.04; 
  float speedGain = 2.5; 

  // Yaw 제어 (좌우)
  if (abs(errorX) > deadzone) {
    servoAnims[0].currentAngle += (errorX * DIR_YAW * speedGain * 5.0);
  }

  // Pitch 제어 (상하)
  if (abs(errorY) > deadzone) {
    servoAnims[1].currentAngle += (errorY * DIR_PITCH * speedGain * 5.0);
  }

  // 최대 이동 각도 제한 (물리적 한계)
  if (servoAnims[0].currentAngle < SERVO_NECK_YAW_MIN) servoAnims[0].currentAngle = SERVO_NECK_YAW_MIN;
  if (servoAnims[0].currentAngle > SERVO_NECK_YAW_MAX) servoAnims[0].currentAngle = SERVO_NECK_YAW_MAX;
  
  if (servoAnims[1].currentAngle < SERVO_NECK_PITCH_MIN) servoAnims[1].currentAngle = SERVO_NECK_PITCH_MIN;
  if (servoAnims[1].currentAngle > SERVO_NECK_PITCH_MAX) servoAnims[1].currentAngle = SERVO_NECK_PITCH_MAX;

  // 정수 변환 및 서보 출력
  int nextYaw = (int)servoAnims[0].currentAngle;
  int nextPitch = (int)servoAnims[1].currentAngle;

  safeWriteNeckYaw(nextYaw);
  safeWriteNeckPitch(nextPitch);

  // 주기적으로 로그 출력
  static unsigned long lastLogTime = 0;
  if (now - lastLogTime > 500) { // 500ms 마다 로그 출력
    char logMsg[100];
    sprintf(logMsg, "Target(%.2f, %.2f) -> Servo(%d, %d)", trackingTargetX, trackingTargetY, nextYaw, nextPitch);
    logActionStep(ACTION_NAME, logMsg);
    lastLogTime = now;
  }
}