#pragma once
#include "../config.h"
#include "../utils/action_utils.h"

void handleSetJointAction() {
    static const char* ACTION_NAME = "Set Joint";

    if (actionStep == 0) {
        char logMsg[100];
        sprintf(logMsg, "servo_id=%d to angle=%d in %dms", targetServoId, targetAngle, moveTimeMs);
        logActionStep(ACTION_NAME, logMsg);
        
        moveTo(targetServoId, targetAngle, moveTimeMs);
        actionStep = 1;
    }

    if (actionStep == 1) {
        if (!isMoving()) {
            logActionStep(ACTION_NAME, "Finished");
            finishAction();
        }
    }
}