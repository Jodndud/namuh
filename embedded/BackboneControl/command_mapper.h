#pragma once
#include "globals.h" // 전역 변수와 ActionType enum을 가져옴

void moveInitPose();
void stopCurrentAction(bool moveToInit = true);

// 명령어의 처리 방식을 구분하기 위한 enum
enum CommandHandlerType {
  HANDLER_NONE,         // 아무것도 안함
  HANDLER_ACTION,       // 여러 단계로 구성된 동작
  HANDLER_IMMEDIATE_FN  // 특정 함수를 즉시 호출
};

extern ActionType currentAction;
extern int actionStep;
extern unsigned long actionLastStepTime;
extern bool isIdle;
extern unsigned long lastCommandTime;

// 즉시 호출될 함수를 가리키기 위한 함수 포인터
using ImmediateActionFn = void (*)();

struct CommandMapping {
  const char* commandString;
  CommandHandlerType handlerType;
  union { // union: 두 변수 중 하나만 저장하여 메모리를 아낌
    ActionType action;          // HANDLER_ACTION일 때 사용
    ImmediateActionFn function; // HANDLER_IMMEDIATE_FN일 때 사용
  };
};

// 명령어 매핑 테이블
static const CommandMapping commandMappings[] = {
  // --- 함수를 즉시 호출하는 명령어들 (단순 동작의 경우 처리) ---
  { "init_pose",    HANDLER_IMMEDIATE_FN, { .function = moveInitPose } },
//   { "good_night",   HANDLER_IMMEDIATE_FN, { .function = []{ neckPitchServo.write(120); } } }, // 간단한 동작은 람다로 즉시 정의
  { "looking_center_end", HANDLER_ACTION,     { .action = ACTION_STOP } },

  // --- 여러 단계의 동작을 실행하는 명령어들 ---
  { "set_joint",    HANDLER_ACTION,     { .action = ACTION_SET_JOINT } }, 
  { "good_night",   HANDLER_ACTION,     { .action = ACTION_HELLO } },
  { "hello",        HANDLER_ACTION,     { .action = ACTION_HELLO } },
  { "make_hello",   HANDLER_ACTION,     { .action = ACTION_HELLO } },
  { "good_morning", HANDLER_ACTION,     { .action = ACTION_NOD } },
  { "hungry",       HANDLER_ACTION,     { .action = ACTION_SHAKE } },
  { "make_heart",   HANDLER_ACTION,     { .action = ACTION_MAKE_HEART } },
  { "make_hug",     HANDLER_ACTION,     { .action = ACTION_MAKE_HUG } },
  { "scissors",     HANDLER_ACTION,     { .action = ACTION_SCISSORS } },
  { "rock",         HANDLER_ACTION,     { .action = ACTION_ROCK } },
  { "paper",        HANDLER_ACTION,     { .action = ACTION_PAPER } },
  { "ate_all",      HANDLER_ACTION,     { .action = ACTION_ATE_ALL } },
  { "call_tori",   HANDLER_ACTION,      { .action = ACTION_CALL_TORI } }, 
  { "looking_center", HANDLER_ACTION,   { .action = ACTION_LOOKING_CENTER } },
};

// 명령어 문자열을 받아 테이블에서 맞는 동작을 찾아 실행하는 함수
void executeCommand(const char* cmd, const JsonDocument& doc) { 
  for (const auto& mapping : commandMappings) {
    if (strcmp(cmd, mapping.commandString) == 0) {
      if (mapping.handlerType == HANDLER_ACTION) {
        currentAction = mapping.action;
      } else if (mapping.handlerType == HANDLER_IMMEDIATE_FN) {
        mapping.function();        
      }
      return; 
    }
  }
  Serial.printf("Unknown command: %s.\n", cmd);
  stopCurrentAction(false); // init pose로 가지 않고 즉시 idle로 전환
}