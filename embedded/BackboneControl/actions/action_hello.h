#pragma once
#include "../config.h"
#include "../utils/action_utils.h"

void handleHelloAction() {
  static const char* ACTION_NAME = "Hello";
  static float startPitch, startWaist;

  switch (actionStep) {
    case 0: // 허리 정렬
      logActionStep(ACTION_NAME, "Step 0 (Waist Align)");
      moveTo(2, SERVO_WAIST_YAW_INIT, 300);
      actionStep = 1;
      break;
    
    case 1: // 시작, 각도 저장, 첫번째 끄덕임
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 1 (Nod 1)");
        startPitch = servoAnims[1].currentAngle;
        startWaist = servoAnims[2].currentAngle;
        moveTo(1, startPitch - 20, 300); // 목 숙이기
        moveTo(2, startWaist - 15, 400); // 허리 돌리기
        actionStep = 2;
      }
      break;

    case 2: // 첫번째 복귀
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 2 (Return 1)");
        moveTo(1, startPitch, 300);
        actionStep = 3;
      }
      break;

    case 3: // 두번째 끄덕임
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 3 (Nod 2)");
        moveTo(1, startPitch - 20, 300); // 목 숙이기
        actionStep = 4;
      }
      break;

    case 4: // 두번째 복귀 & 허리 복귀
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 4 (Return 2 & Finish)");
        moveTo(1, startPitch, 300);
        moveTo(2, startWaist, 400);
        actionStep = 5;
      }
      break;
    
    case 5: // 모든 움직임이 끝나면 동작 종료
        if (!isMoving()) {
            finishAction();
        }
        break;
  }
}