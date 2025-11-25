#pragma once
#include "../config.h"
#include "../utils/action_utils.h"

void handleNodAction() {
  static const char* ACTION_NAME = "Nod";
  static float startPitch;

  switch (actionStep) {
    case 0: // 첫번째 끄덕임
      logActionStep(ACTION_NAME, "Step 0 (Nod 1 Down)");
      startPitch = servoAnims[1].currentAngle;
      moveTo(1, startPitch - 20, 300);
      actionStep = 1;
      break;
    case 1: // 첫번째 복귀
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 1 (Nod 1 Up)");
        moveTo(1, startPitch, 300);
        actionStep = 2;
      }
      break;
    case 2: // 두번째 끄덕임
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 2 (Nod 2 Down)");
        moveTo(1, startPitch - 20, 300);
        actionStep = 3;
      }
      break;
    case 3: // 두번째 복귀
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 3 (Nod 2 Up & Finish)");
        moveTo(1, startPitch, 300);
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