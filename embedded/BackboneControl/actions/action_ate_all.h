#pragma once
#include "../config.h"
#include "../utils/action_utils.h"

void handleAteAllAction() {
    static const char* ACTION_NAME = "Ate All";
    static float startPitch;

    switch (actionStep) {
        case 0:
            logActionStep(ACTION_NAME, "Step 0");
            startPitch = servoAnims[1].currentAngle;
            moveTo(1, startPitch - 25, 500); // 만족스럽게 깊이
            actionStep = 1;
            break;
        case 1:
            if (!isMoving()) {
                logActionStep(ACTION_NAME, "Step 1 (Finish)");
                moveTo(1, startPitch, 500);
                actionStep = 2;
            }
            break;
        case 2:
            if (!isMoving()) {
                finishAction();
            }
            break;
    }
}