#include <Arduino.h>
#include <Servo.h>

// Arduino Mega 2560용 표준 Servo 라이브러리 버전
// - ESP32 전용 코드(ESP32Servo/ledc) 제거
// - 동일한 직렬 명령 지원: help / sweep / 각도(0..180) / us=<500..2500>

// 서보 핀/파라미터 설정 (Mega2560에서 안전한 기본 핀: 9)
#ifndef SERVO_PIN
#define SERVO_PIN 9      // Mega2560 권장 핀 예: 9, 10, 11, 12, 13 등
#endif
#ifndef SERVO_MIN_US
#define SERVO_MIN_US 500   // 펄스폭 최소 (us)
#endif
#ifndef SERVO_MAX_US
#define SERVO_MAX_US 2500  // 펄스폭 최대 (us)
#endif
#ifndef SERVO_FREQ
#define SERVO_FREQ 50      // 서보용 주파수(Hz) - Servo 라이브러리는 내부 타이머 사용
#endif

static Servo gServo;
static bool gAttached = false;
static int gAngle = 90; // 현재 각도(0~180)

static void ensureAttach() {
  if (!gAttached) {
    // 표준 Servo 라이브러리: attach(pin, min, max)로 맵핑 범위 지정
    gServo.attach(SERVO_PIN, SERVO_MIN_US, SERVO_MAX_US);
    gAttached = true;
  }
}

static void setServoByAngle(int angle) {
  angle = constrain(angle, 0, 180);
  ensureAttach();
  gServo.write(angle);
  gAngle = angle;
}

static void setServoByMicros(int us) {
  us = constrain(us, SERVO_MIN_US, SERVO_MAX_US);
  ensureAttach();
  gServo.writeMicroseconds(us);
}

static void printHelp() {
  Serial.println();
  Serial.println(F("Mega2560 Servo Serial Control"));
  Serial.println(F("Commands:"));
  Serial.println(F("  <0..180>         : set angle in degrees"));
  Serial.println(F("  us=<500..2500>   : set pulse width in microseconds"));
  Serial.println(F("  sweep            : sweep 0 -> 180 -> 0"));
  Serial.println(F("  help             : show this help"));
  Serial.println();
}

void setup() {
  Serial.begin(115200);
  delay(100);
  printHelp();
  setServoByAngle(gAngle);
  Serial.print(F("Servo attached on pin "));
  Serial.print(SERVO_PIN);
  Serial.print(F(", angle="));
  Serial.println(gAngle);
}

static void doSweep() {
  for (int a = 0; a <= 180; a += 2) {
    setServoByAngle(a);
    delay(10);
  }
  for (int a = 180; a >= 0; a -= 2) {
    setServoByAngle(a);
    delay(10);
  }
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    if (line.length() == 0) return;

    if (line.equalsIgnoreCase("help")) {
      printHelp();
      return;
    }
    if (line.equalsIgnoreCase("sweep")) {
      Serial.println(F("sweeping..."));
      doSweep();
      Serial.println(F("done"));
      return;
    }
    if (line.startsWith("us=")) {
      int us = line.substring(3).toInt();
      us = constrain(us, SERVO_MIN_US, SERVO_MAX_US);
      setServoByMicros(us);
      Serial.print(F("OK us="));
      Serial.println(us);
      return;
    }
    // 숫자(각도) 파싱
    bool numeric = true;
    for (size_t i = 0; i < line.length(); ++i) {
      char c = line[i];
      if (!(c == '-' || (c >= '0' && c <= '9'))) { numeric = false; break; }
    }
    if (numeric) {
      int angle = line.toInt();
      angle = constrain(angle, 0, 180);
      setServoByAngle(angle);
      Serial.print(F("OK angle="));
      Serial.println(angle);
    } else {
      Serial.println(F("ERR unknown command; type 'help'"));
    }
  }
}
