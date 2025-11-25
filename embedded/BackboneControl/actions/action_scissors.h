#pragma once
#include "../config.h"
#include "../utils/action_utils.h"

void handleScissorsAction() {
  static const char* ACTION_NAME = "Scissors (Smooth)";

  static float startWaist;
  static unsigned long delayStartTime;

  switch (actionStep) {
    case 0:  // 허리 정렬 시작
      logActionStep(ACTION_NAME, "Step 0 (Waist Align)");
      moveTo(2, SERVO_WAIST_YAW_INIT, 300);
      actionStep = 1;
      break;

    case 1: // 허리 정렬 완료 대기 및 딜레이 시작
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Waist aligned. Starting delay...");
        delayStartTime = millis();
        actionStep = 2;
      }
      break;
      
    case 2: // 딜레이 대기
      if (millis() - delayStartTime >= MEDIAPIPE_ACTION_DELAY) {
        actionStep = 3;
      }
      break;

    case 3:  // 대기 후 반동 준비
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 1 (Wind up)");

        // 현재 허리 각도 저장 (기준점)
        startWaist = servoAnims[2].currentAngle;
        
        // 목과 허리를 정면으로 고정
        moveTo(0, SERVO_NECK_YAW_INIT, 300);    // 목 회전을 초기 각도로 고정
        moveTo(1, SERVO_NECK_PITCH_INIT, 300);  // 목 상하를 초기 각도로 고정

        moveTo(2, startWaist + 15, 150);        // 오른쪽으로 살짝
        actionStep = 4;
      }
      break;
    case 4:  // 왼쪽으로 확 틀기
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 2 (Swing Left)");

        moveTo(0, SERVO_NECK_YAW_INIT + 20, 200);
        moveTo(2, startWaist + 15, 200);
        actionStep = 5;
      }
      break;
    case 5:  // 원위치로 복귀
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 3 (Swing Right)");

        moveTo(0, SERVO_NECK_YAW_INIT - 30, 300);
        moveTo(1, SERVO_NECK_PITCH_INIT + 15, 300);
        moveTo(2, startWaist - 30, 300);
        actionStep = 6;
      }
      break;
    case 6:  // 원위치 복귀
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 4 (Return)");
        
        // 허리 복귀
        moveTo(2, startWaist, 300);
        
        // 목도 정면 복귀
        moveTo(0, SERVO_NECK_YAW_INIT, 300);
        moveTo(1, SERVO_NECK_PITCH_INIT, 300);
        
        actionStep = 7;
      }
      break;
    case 7:  // 종료
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 5 (Finish)");
        finishAction();
      }
      break;
  }
}