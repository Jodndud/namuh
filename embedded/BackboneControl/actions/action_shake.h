#pragma once
#include "../config.h"
#include "../utils/action_utils.h"

void handleShakeHeadAction() {
  static const char* ACTION_NAME = "Shake Head";
  static float startYaw, startWaist;

  switch (actionStep) {
    case 0: // 왼쪽 보기
      logActionStep(ACTION_NAME, "Step 0 (Shake Left)");
      startYaw = servoAnims[0].currentAngle;
      startWaist = servoAnims[2].currentAngle;
      moveTo(0, startYaw - 30, 250);
      moveTo(2, startWaist - 10, 300);
      actionStep = 1;
      break;
    case 1: // 오른쪽 보기
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 1 (Shake Right)");
        moveTo(0, startYaw + 30, 500); // 반대편은 더 길게
        moveTo(2, startWaist + 10, 600);
        actionStep = 2;
      }
      break;
    case 2: // 원위치 복귀
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 2 (Return & Finish)");
        moveTo(0, startYaw, 250);
        moveTo(2, startWaist, 300);
        actionStep = 3;
      }
      break;
    case 3: // 종료
      if (!isMoving()) {
        finishAction();
      }
      break;
  }
}