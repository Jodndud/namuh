#pragma once
#include "../config.h"
#include "../utils/action_utils.h"

void performIdleMove() {
  if (isMoving()) return; // 애니메이션이 진행 중이면 IDLE 동작을 실행하지 않음

  unsigned long now = millis();
  if (now - lastIdleMoveTime < nextIdleMoveInterval) {
    return;
  }
  
  lastIdleMoveTime = now;
  // 동작 사이의 간격 설정
  nextIdleMoveInterval = random(1000, 4000); // 5-12초 -> 1-4초 변경 (정적 상태가 잦아서)
  
  static const char* ACTION_NAME = "Idle Move";
  int moveType = random(0, 8);
  
  float targetYaw, targetPitch, targetWaistYaw;
  unsigned long duration = random(1800, 3000); // 동작 시간을 무작위로 설정

  switch (moveType) {
    // =========================================================
    // [Micro Movements] : 짧고 미세한 움직임 (살아있는 느낌)
    // =========================================================
    case 0: // 미세한 호흡 (숨쉬기)
      logActionStep(ACTION_NAME, "Breathing...");
      targetPitch = servoAnims[1].currentAngle + random(-3, 4); // 현재 각도에서 아주 조금만 변화
      duration = random(500, 1000); 
      moveTo(1, targetPitch, duration);
      // 허리도 아주 살짝 틀어줌 (유기적인 느낌)
      targetWaistYaw = servoAnims[2].currentAngle + random(-2, 3);
      moveTo(2, targetWaistYaw, duration);
      break;

    case 1: // 갸우뚱 (짧은 반응)
      logActionStep(ACTION_NAME, "Micro tilt...");
      targetPitch = random(SERVO_NECK_PITCH_INIT - 10, SERVO_NECK_PITCH_INIT + 10);
      duration = random(400, 800); // 이건 좀 빠르게
      moveTo(1, targetPitch, duration);
      break;

    // =========================================================
    // [Macro Movements] : 크고 확실한 움직임
    // =========================================================
    case 2: // [왼쪽] 허리를 크게 사용하여 쳐다보기
      logActionStep(ACTION_NAME, "Look Left (Waist lead)...");
      duration = random(1200, 2000); 
      targetWaistYaw = random(SERVO_WAIST_YAW_MIN, SERVO_WAIST_YAW_INIT - 10);
      targetYaw = targetWaistYaw - random(10, 30); // 허리보다 더 많이 꺾음
      
      // 허리가 먼저 돌고(duration), 목이 살짝 늦게(duration + delay) 도착하면 더 자연스러움
      // 여기서는 단순화를 위해 동시에 시작하되 목을 더 많이 꺾음
      moveTo(2, targetWaistYaw, duration);
      moveTo(0, targetYaw, duration);
      break;

    case 3: // [오른쪽] 허리를 크게 사용하여 쳐다보기
      logActionStep(ACTION_NAME, "Look Right (Waist lead)...");
      duration = random(1200, 2000);
      targetWaistYaw = random(SERVO_WAIST_YAW_INIT + 10, SERVO_WAIST_YAW_MAX);
      targetYaw = targetWaistYaw + random(10, 30);
      
      moveTo(2, targetWaistYaw, duration);
      moveTo(0, targetYaw, duration);
      break;
      
    case 4: // 하늘 보기 (허리도 같이 뒤로 젖히는 느낌을 주기 위해 허리 정렬)
      logActionStep(ACTION_NAME, "Looking Up...");
      duration = random(1500, 2500);
      targetPitch = random(SERVO_NECK_PITCH_MIN, SERVO_NECK_PITCH_INIT - 10);
      targetWaistYaw = SERVO_WAIST_YAW_INIT + random(-10, 10); // 허리는 거의 정면
      
      moveTo(1, targetPitch, duration);
      moveTo(2, targetWaistYaw, duration);
      break;

    case 5: // 바닥 훑기 (지루한 듯이)
      logActionStep(ACTION_NAME, "Scanning floor...");
      duration = random(2000, 3500); // 천천히
      targetPitch = random(SERVO_NECK_PITCH_INIT + 10, SERVO_NECK_PITCH_MAX);
      targetYaw = random(SERVO_NECK_YAW_MIN + 20, SERVO_NECK_YAW_MAX - 20); // 바닥을 보며 고개를 돌림
      
      moveTo(1, targetPitch, duration);
      moveTo(0, targetYaw, duration);
      break;
    
    case 6: // 퀵 리셋 (깜짝 놀라거나 자세 고쳐잡기)
      logActionStep(ACTION_NAME, "Quick Reset...");
      duration = random(500, 800); // 아주 빠르게 원위치
      moveInitPoseWithDuration(duration); // moveInitPose에 duration 인자가 있다고 가정
      break;

    case 7: // 스트레칭 (가장 큰 범위로 천천히)
      logActionStep(ACTION_NAME, "Big Stretch...");
      duration = random(3000, 4500); // 아주 천천히
      // 허리와 목을 서로 반대 방향이나 끝까지 보내는 로직 등
      targetWaistYaw = (random(0, 2) == 0) ? SERVO_WAIST_YAW_MIN : SERVO_WAIST_YAW_MAX;
      moveTo(2, targetWaistYaw, duration);
      moveTo(1, SERVO_NECK_PITCH_INIT, duration); // 고개는 정면 유지
      break;
  }
}
