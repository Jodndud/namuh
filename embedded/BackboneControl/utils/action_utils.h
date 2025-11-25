#pragma once
#include "../config.h"  

// === 공통 지연 시작 함수 ====
void startActionDelay(
    const char* actionName,     // 로그에 찍을 행동 이름
    unsigned long& startTime,   // 값 갱신할 시간 변수 (참조 &)
    int& step                   // 값 변경할 단계 변수 (참조 &)
) {
  Serial.print("[ACTION] ");
  Serial.print(actionName);
  Serial.print(": Start delay (");
  Serial.print(MEDIAPIPE_ACTION_DELAY / 1000);
  Serial.println(" seconds).");

  startTime = millis();
  step = 1; 
}

// 액션 스텝 로그 출력
void logActionStep(const char* actionName, const char* stepMessage) {
    Serial.print("[ACTION] ");
    Serial.print(actionName);
    Serial.print(": ");
    Serial.println(stepMessage);
}

// 액션 종료 시 공통으로 실행되는 클린업 함수
void finishAction() {
    currentAction = ACTION_NONE;
    detachWaistServo();
}