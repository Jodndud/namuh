#pragma once
#include "../config.h"
#include "../utils/action_utils.h"

void handleMakeHeartAction() {
  static const char* ACTION_NAME = "Make Heart";
  static float startYaw, startPitch, startWaist;

  switch (actionStep) {
    case 0: // 갸웃
      logActionStep(ACTION_NAME, "Step 0 (Tilt)");
      startYaw = servoAnims[0].currentAngle;
      startPitch = servoAnims[1].currentAngle;
      startWaist = servoAnims[2].currentAngle;
      moveTo(0, startYaw - 15, 250);
      moveTo(1, startPitch + 15, 250);
      actionStep = 1;
      break;
    case 1: // 허리 둠칫 1
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 1 (Waist Left)");
        moveTo(2, startWaist - 15, 350);
        actionStep = 2;
      }
      break;
    case 2: // 허리 둠칫 2
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 2 (Waist Right)");
        moveTo(2, startWaist + 15, 350);
        actionStep = 3;
      }
      break;
    case 3: // 원위치 복귀
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 3 (Return & Finish)");
        moveTo(0, startYaw, 250);
        moveTo(1, startPitch, 250);
        moveTo(2, startWaist, 350);
        actionStep = 4;
      }
      break;
    case 4: // 종료
      if (!isMoving()) {
        finishAction();
      }
      break;
  }
}