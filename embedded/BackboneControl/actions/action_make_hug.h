#pragma once
#include "../config.h"
#include "../utils/action_utils.h"

void handleMakeHugAction() {
    static const char* ACTION_NAME = "Make Hug";
    static float startPitch;

    switch (actionStep) {
        case 0: // 첫번째 끄덕임
            logActionStep(ACTION_NAME, "Step 0 (Nod 1)");
            startPitch = servoAnims[1].currentAngle;
            moveTo(1, startPitch - 15, 150);
            moveTo(2, SERVO_WAIST_YAW_INIT, 300); // 허리 정렬
            actionStep = 1;
            break;
        case 1:
            if (!isMoving()) {
                logActionStep(ACTION_NAME, "Step 1 (Return 1)");
                moveTo(1, startPitch, 150);
                actionStep = 2;
            }
            break;
        case 2:
            if (!isMoving()) {
                logActionStep(ACTION_NAME, "Step 2 (Nod 2)");
                moveTo(1, startPitch - 15, 150);
                actionStep = 3;
            }
            break;
        case 3:
            if (!isMoving()) {
                logActionStep(ACTION_NAME, "Step 3 (Return 2)");
                moveTo(1, startPitch, 150);
                actionStep = 4;
            }
            break;
        case 4:
            if (!isMoving()) {
                logActionStep(ACTION_NAME, "Step 4 (Nod 3)");
                moveTo(1, startPitch - 15, 150);
                actionStep = 5;
            }
            break;
        case 5:
            if (!isMoving()) {
                logActionStep(ACTION_NAME, "Step 5 (Return 3 & Finish)");
                moveTo(1, startPitch, 150);
                actionStep = 6;
            }
            break;
        case 6:
            if (!isMoving()) {
                finishAction();
            }
            break;
    }
}