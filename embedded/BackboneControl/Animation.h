#pragma once
#include <Arduino.h>

// Easing 함수 (움직임을 부드럽게 만들어 줌)
// https://easings.net/#easeInOutCubic
float easeInOutCubic(float x) {
  return x < 0.5 ? 4 * x * x * x : 1 - pow(-2 * x + 2, 3) / 2;
}
