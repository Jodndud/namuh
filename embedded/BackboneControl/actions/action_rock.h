#pragma once
#include "../config.h"
#include "../utils/action_utils.h"

void handleRockAction() {
  static const char* ACTION_NAME = "Rock (Smooth)";

  static float startPitch;
  static unsigned long delayStartTime;

  switch (actionStep) {
    case 0:  // 허리 및 목 정렬 시작
      logActionStep(ACTION_NAME, "Step 0 (Align)");
      moveTo(0, SERVO_NECK_YAW_INIT, 300);    // 목 회전을 초기 각도로 고정
      moveTo(1, SERVO_NECK_PITCH_INIT, 300);  // 목 상하를 초기 각도로 고정
      moveTo(2, SERVO_WAIST_YAW_INIT, 300);   // 허리 회전을 초기 각도로 고정
      actionStep = 1;
      break;

    case 1: // 정렬 완료 대기 및 딜레이 시작
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Aligned. Starting delay...");
        delayStartTime = millis();
        actionStep = 2;
      }
      break;

    case 2: // 딜레이 후 반동 준비
      if (millis() - delayStartTime >= MEDIAPIPE_ACTION_DELAY) {
        logActionStep(ACTION_NAME, "Step 1 (Prepare)");
        startPitch = servoAnims[1].currentAngle;
        actionStep = 3;
      }
      break;

    case 3:  // 아래로 쿵 찍기
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 2 (Smash Down)");
        moveTo(1, startPitch + 25, 300);  // 아래로 강하게
        actionStep = 4;
      }
      break;
    case 4:  // 원위치로 복귀
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 3 (Return)");
        moveTo(1, startPitch, 300);
        actionStep = 5;
      }
      break;
    case 5:  // 종료
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 4 (Finish)");
        finishAction();
      }
      break;
  }
}