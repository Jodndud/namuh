#pragma once

#include "../config.h"
#include "../utils/action_utils.h"

void handleLookingCenterAction() {
  static const char* ACTION_NAME = "Looking Center";
  static unsigned long lastMoveTime;
  static unsigned long nextMoveInterval;

  switch (actionStep) {
    case 0: // 초기 정렬
      logActionStep(ACTION_NAME, "Step 0 (Align to Center)");
      moveInitPose();
      actionStep = 1;
      break;

    case 1: // 정렬 완료 대기
      if (!isMoving()) {
        logActionStep(ACTION_NAME, "Step 1 (Alignment Complete, starting idle moves)");
        lastMoveTime = millis();
        nextMoveInterval = random(1500, 3000);
        actionStep = 2;
      }
      break;
    
    case 2: // 중앙에서 미세하게 움직이기
      if (millis() - lastMoveTime > nextMoveInterval) {
        if (isMoving()) break; // 아직 이전 움직임이 진행 중이면 대기

        logActionStep(ACTION_NAME, "Step 2 (Performing micro-movement)");

        int moveType = random(0, 3);
        float targetYaw, targetPitch, targetWaistYaw;
        unsigned long duration = random(1500, 2500);

        switch(moveType) {
          case 0: // 미세한 끄덕임
            targetPitch = SERVO_NECK_PITCH_INIT + random(-5, 6);
            moveTo(1, targetPitch, duration);
            break;
          
          case 1: // 미세한 두리번
            targetYaw = SERVO_NECK_YAW_INIT + random(-7, 8);
            targetWaistYaw = SERVO_WAIST_YAW_INIT + random(-4, 5);
            moveTo(0, targetYaw, duration);
            moveTo(2, targetWaistYaw, duration);
            break;

          case 2: // 숨쉬기
            targetPitch = servoAnims[1].currentAngle + random(-3, 4);
            targetWaistYaw = servoAnims[2].currentAngle + random(-2, 3);
            moveTo(1, targetPitch, duration);
            moveTo(2, targetWaistYaw, duration);
            break;
        }

        lastMoveTime = millis();
        nextMoveInterval = random(1500, 3000);
      }
      break;
  }
}
