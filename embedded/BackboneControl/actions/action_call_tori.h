#pragma once
#include "../config.h"
#include "../utils/action_utils.h"

void handleCallToriAction() {
  static const char* ACTION_NAME = "Call Tori";
  static float startYaw, startPitch, startWaist;

  switch (actionStep) {
    case 0: // 허리 정렬
      logActionStep(ACTION_NAME, "Step 0 (Waist Align)");
      moveTo(2, SERVO_WAIST_YAW_INIT, 300);
      actionStep = 1;
      break;
    case 1: // 왼쪽 보기
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 1 (Look Left)");
        startYaw = servoAnims[0].currentAngle;
        startPitch = servoAnims[1].currentAngle;
        startWaist = servoAnims[2].currentAngle;
        moveTo(0, 130, 1000);
        moveTo(2, 110, 1200);
        actionStep = 2;
      }
      break;
    case 2: // 오른쪽 보기
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 2 (Look Right)");
        moveTo(0, 50, 1000);
        moveTo(2, 70, 1200);
        actionStep = 3;
      }
      break;
    case 3: // 원위치 복귀
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 3 (Return)");
        moveInitPose(); // config.h에 정의된 초기 자세로 돌아감
        actionStep = 4;
      }
      break;
    case 4: // 원위치 복귀 완료 대기 및 첫번째 끄덕임 (아래)
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 4 (Nod 1 Down)");
        moveTo(1, SERVO_NECK_PITCH_INIT + 15, 250);
        actionStep = 5;
      }
      break;
    case 5: // 첫번째 끄덕임 (위)
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 5 (Nod 1 Up)");
        moveTo(1, SERVO_NECK_PITCH_INIT, 250);
        actionStep = 6;
      }
      break;
    case 6: // 두번째 끄덕임 (아래)
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 6 (Nod 2 Down)");
        moveTo(1, SERVO_NECK_PITCH_INIT + 15, 250);
        actionStep = 7;
      }
      break;
    case 7: // 두번째 끄덕임 (위)
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 7 (Nod 2 Up)");
        moveTo(1, SERVO_NECK_PITCH_INIT, 250);
        actionStep = 8;
      }
      break;
    case 8: // 종료
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 8 (Finish)");
        finishAction();
      }
      break;
  }
}