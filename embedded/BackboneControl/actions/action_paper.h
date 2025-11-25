#pragma once
#include "../config.h"
#include "../utils/action_utils.h"

void handlePaperAction() {
  static const char* ACTION_NAME = "Paper (Smooth)";

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

    case 3:  // 정면 바라보며 자세 리셋
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 1 (Align)");

        startWaist = servoAnims[2].currentAngle;

        // 목을 초기 각도로 고정
        moveTo(0, SERVO_NECK_YAW_INIT, 300);  
        moveTo(1, SERVO_NECK_PITCH_INIT, 300);
        
        // 허리를 왼쪽으로 30도 틀어 반동 준비 (60도 안전 범위 내)
        moveTo(2, startWaist - 30, 200);        // 왼쪽으로 살짝
        actionStep = 4;
      }
      break;
    case 4:  // 왼쪽으로 웅크리기
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 2 (Wind up)");

        moveTo(0, SERVO_NECK_YAW_INIT - 20, 200);
        moveTo(1, SERVO_NECK_PITCH_INIT + 10, 200);
        moveTo(2, startWaist - 30, 200);
        actionStep = 5;
      }
      break;
    case 5:  // 오른쪽으로 쫙 펼치기
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 3 (Spread)");

        moveTo(2, startWaist + 20, 300);
        moveTo(0, SERVO_NECK_YAW_INIT + 30, 300);
        moveTo(1, SERVO_NECK_PITCH_INIT - 10, 300);
        
        actionStep = 6;
      }
      break;
    case 6:  // [복귀] 원위치
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 4 (Return)");
        
        moveTo(2, startWaist, 300);
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