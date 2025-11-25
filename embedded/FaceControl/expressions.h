#pragma once
#include <FastLED.h>

// LED/Matrix helpers
extern CRGB leds[];

#ifndef MATRIX_W
#define MATRIX_W 16
#endif
#ifndef MATRIX_H
#define MATRIX_H 16
#endif
#ifndef SERPENTINE
#define SERPENTINE 1
#endif

static inline uint16_t XY(uint8_t x, uint8_t y) {
  if (x >= MATRIX_W || y >= MATRIX_H) return 0;
#if SERPENTINE
  if (y & 0x01) {
    // odd rows go right->left
    return (y * MATRIX_W) + (MATRIX_W - 1 - x);
  } else {
    return (y * MATRIX_W) + x;
  }
#else
  return (y * MATRIX_W) + x;
#endif
}

static inline void clearAll() { fill_solid(leds, MATRIX_W * MATRIX_H, CRGB::Black); }
static inline void fillAll(const CRGB &c) { fill_solid(leds, MATRIX_W * MATRIX_H, c); }

// ---- Simple primitives ----
static inline void setPixel(uint8_t x, uint8_t y, const CRGB &c) {
  leds[XY(x, y)] = c;
}

static inline void box(uint8_t x0, uint8_t y0, uint8_t w, uint8_t h, const CRGB &c) {
  for (uint8_t y = y0; y < y0 + h && y < MATRIX_H; ++y) {
    for (uint8_t x = x0; x < x0 + w && x < MATRIX_W; ++x) {
      setPixel(x, y, c);
    }
  }
}

static inline void circle(uint8_t cx, uint8_t cy, uint8_t r, const CRGB &c) {
  for (int y = -r; y <= r; ++y) {
    for (int x = -r; x <= r; ++x) {
      if (x*x + y*y <= r*r) {
        int xx = cx + x, yy = cy + y;
        if (xx >= 0 && yy >= 0 && xx < MATRIX_W && yy < MATRIX_H) setPixel(xx, yy, c);
      }
    }
  }
}

// Small heart 5x5 pattern
static inline void smallHeart(uint8_t x0, uint8_t y0, const CRGB &c) {
  // rough heart bitmap
  const uint8_t bmp[5][5] = {
    {0,1,0,1,0},
    {1,1,1,1,1},
    {1,1,1,1,1},
    {0,1,1,1,0},
    {0,0,1,0,0},
  };
  for (uint8_t y=0;y<5;y++) {
    for (uint8_t x=0;x<5;x++) {
      if (bmp[y][x]) setPixel(x0+x, y0+y, c);
    }
  }
}

// ---- Eyes + mouth helpers ----
static inline void drawEye(uint8_t x0, uint8_t y0, uint8_t pupilX, uint8_t pupilY, const CRGB &eye, const CRGB &pupil) {
  box(x0, y0, 4, 4, eye);
  setPixel(x0 + 1 + (pupilX % 2), y0 + 1 + (pupilY % 2), pupil);
  setPixel(x0 + 1 + (pupilX % 2), y0 + (pupilY % 2), pupil);
  setPixel(x0 + (pupilX % 2), y0 + 1 + (pupilY % 2), pupil);
  setPixel(x0 + (pupilX % 2), y0 + (pupilY % 2), pupil);
}

static inline void drawMouth(uint8_t y, const CRGB &c) {
  for (uint8_t x = 4; x <= 11; ++x) setPixel(x, y, c);
}

// ---- Expressions ----
enum ExprId {
  EXPR_NEUTRAL,
  EXPR_HAPPY,
  EXPR_HEART,
  EXPR_HUG,
  EXPR_TRACKING,
  EXPR_THINKING,
  EXPR_FOLLOW_ON,
  EXPR_ERROR,
  // 추가 액션: hello / scissors / rock / paper
  EXPR_HELLO,
  EXPR_SCISSORS,
  EXPR_ROCK,
  EXPR_PAPER,
  // 신규 액션 표정들
  EXPR_GOOD_MORNING,
  EXPR_GOOD_NIGHT,
  EXPR_HUNGRY,
  EXPR_ATE_ALL
};

static inline void renderNeutral(uint32_t frame) {
  (void)frame; clearAll();
  drawEye(4, 5, 0, 0, CRGB::White, CRGB::Black);
  drawEye(10,5, 0, 0, CRGB::White, CRGB::Black);
  drawMouth(12, CRGB(60,60,60));
}

static inline void renderHappy(uint32_t frame) {
  (void)frame; clearAll();
  drawEye(4, 5, 0, 0, CRGB::White, CRGB::Black);
  drawEye(10,5, 0, 0, CRGB::White, CRGB::Black);
  // simple smile arc
  for (uint8_t x=5;x<=10;x++) setPixel(x, 12, CRGB::Yellow);
  setPixel(4, 11, CRGB::Yellow); setPixel(11, 11, CRGB::Yellow);
}

static inline void renderHeart(uint32_t frame) {
  clearAll();
  uint8_t beat = (frame/8) % 3; // 0..2
  CRGB c = CHSV(0, 255, beat==1 ? 255 : 160);
  // big heart center
  circle(8,8,5,c);
  circle(6,6,3,c);
  circle(10,6,3,c);
}

static inline void renderHug(uint32_t frame) {
  (void)frame; clearAll();
  drawEye(4, 5, 0, 0, CRGB::White, CRGB::Black);
  drawEye(10,5, 0, 0, CRGB::White, CRGB::Black);
  smallHeart(1, 11, CRGB::HotPink);
  smallHeart(10, 11, CRGB::HotPink);
}

static inline void renderTracking(uint32_t frame) {
  clearAll();
  uint8_t px = (frame/3) % 4; // 0..3
  drawEye(4, 5, px, 0, CRGB::White, CRGB::Blue);
  drawEye(10,5, 3-px, 0, CRGB::White, CRGB::Blue);
  // scanning bar
  uint8_t y = 3 + (frame % 10);
  for (uint8_t x=0;x<MATRIX_W;x++) setPixel(x, y, CRGB(10,30,60));
}

static inline void renderThinking(uint32_t frame) {
  clearAll();
  // spinner around center
  static const uint8_t pts[8][2] = {
    {8,2},{12,4},{14,8},{12,12},{8,14},{4,12},{2,8},{4,4}
  };
  for (uint8_t i=0;i<8;i++) {
    uint8_t idx = (i + (frame/3)) & 7;
    setPixel(pts[idx][0], pts[idx][1], CHSV(160 + i*8, 200, 180));
  }
}

static inline void renderFollowOn(uint32_t frame) {
  (void)frame; clearAll();
  // star eyes
  smallHeart(3,4, CRGB::Yellow);
  smallHeart(9,4, CRGB::Yellow);
  drawMouth(12, CRGB(80,80,20));
}

static inline void renderError(uint32_t frame) {
  (void)frame; clearAll();
  // X eyes
  for (uint8_t i=0;i<4;i++) { setPixel(4+i,5+i, CRGB::Red); setPixel(7-i,5+i, CRGB::Red); }
  for (uint8_t i=0;i<4;i++) { setPixel(10+i,5+i, CRGB::Red); setPixel(13-i,5+i, CRGB::Red); }
  drawMouth(12, CRGB::Red);
}

// ---- 추가 표정 렌더러 ----
static inline void renderHello(uint32_t frame) {
  clearAll();
  // 깜빡이는 눈 + 볼에 하트 점
  bool wink = ((frame / 10) % 2) == 0;
  drawEye(4, 5, wink ? 1 : 0, 0, CRGB::White, wink ? CRGB::Black : CRGB::Black);
  drawEye(10,5, wink ? 0 : 1, 0, CRGB::White, CRGB::Black);
  smallHeart(2, 11, CRGB(255,120,180));
  smallHeart(11, 11, CRGB(255,120,180));
  // 살짝 웃는 입
  for (uint8_t x=5;x<=10;x++) setPixel(x, 12, CRGB(255,200,80));
}

static inline void renderScissors(uint32_t frame) {
  clearAll();
  // 가위: 보라색 V 모양을 깜빡이며 표시
  drawEye(4, 5, 0, 0, CRGB::White, CRGB::Purple);
  drawEye(10,5, 0, 0, CRGB::White, CRGB::Purple);
  uint8_t phase = (frame / 6) % 2; // 0/1 토글
  CRGB c = CHSV(200, 200, phase ? 220 : 140);
  // V mouth
  setPixel(7, 11, c); setPixel(8, 12, c); setPixel(9, 11, c);
  setPixel(6, 10, c); setPixel(10,10, c);
}

static inline void renderRock(uint32_t frame) {
  clearAll();
  // 바위: 단단한 블록형 입 + 진한 눈썹
  drawEye(4, 5, 0, 0, CRGB::White, CRGB::Black);
  drawEye(10,5, 0, 0, CRGB::White, CRGB::Black);
  // 눈썹
  for (uint8_t x=3;x<=7;x++) setPixel(x, 4, CRGB(180, 60, 40));
  for (uint8_t x=9;x<=13;x++) setPixel(x, 4, CRGB(180, 60, 40));
  // 네모난 입(주기적으로 살짝 밝기 변화)
  uint8_t v = (frame % 10) < 5 ? 140 : 100;
  for (uint8_t y=11;y<=12;y++) for (uint8_t x=5;x<=10;x++) setPixel(x, y, CRGB(v, v/2, 0));
}

static inline void renderPaper(uint32_t frame) {
  clearAll();
  // 보: 평평한 입 + 환한 눈동자
  drawEye(4, 5, (frame/8)%2, 0, CRGB::White, CRGB::Blue);
  drawEye(10,5, (frame/8)%2, 0, CRGB::White, CRGB::Blue);
  for (uint8_t x=4;x<=11;x++) setPixel(x, 12, CRGB(200, 220, 255));
}

static inline void renderGoodMorning(uint32_t frame) {
  clearAll();
  // 해가 떠오르는 느낌: 상단 노란/오렌지 그라디언트 + 눈 반짝임
  for (uint8_t y=0;y<4;y++) {
    for (uint8_t x=0;x<MATRIX_W;x++) {
      uint8_t v = 180 - y*30;
      setPixel(x,y, CRGB(v, 140 + y*10, 20));
    }
  }
  drawEye(4,5, (frame/6)%3, 0, CRGB::White, CRGB::Black);
  drawEye(10,5, (frame/6)%3, 0, CRGB::White, CRGB::Black);
  // 밝아지는 미소
  uint8_t phase = (frame/10)%3; // 0..2
  for (uint8_t x=5;x<=10;x++) setPixel(x, 12, CHSV(30 + phase*10, 200, 200));
}

static inline void renderGoodNight(uint32_t frame) {
  clearAll();
  // 달과 별: 좌측 위 달, 주변 점멸 별
  circle(3,3,2, CRGB(200,200,120));
  for (uint8_t i=0;i<6;i++) {
    uint8_t sx = (i*3 + frame) % MATRIX_W;
    uint8_t sy = 2 + (i*5) % 6;
    setPixel(sx, sy, (frame/4 + i)%2 ? CRGB(40,40,80) : CRGB(120,120,160));
  }
  // 졸린 눈: 반쯤 감김
  drawEye(4,5,1,1, CRGB::White, CRGB(10,10,40));
  drawEye(10,5,1,1, CRGB::White, CRGB(10,10,40));
  // 잔잔한 입
  for (uint8_t x=6;x<=9;x++) setPixel(x, 12, CRGB(60,40,80));
}

static inline void renderHungry(uint32_t frame) {
  clearAll();
  // 배고픔: 가운데 접시 + 움직이는 포크/숟가락 아이콘
  circle(8,9,4, CRGB(50,50,50));
  circle(8,9,3, CRGB(10,10,10));
  // 눈은 기대감으로 위쪽
  drawEye(4,5,0,0, CRGB::White, CRGB::Black);
  drawEye(10,5,0,0, CRGB::White, CRGB::Black);
  // 포크/숟가락 교대
  bool fork = ((frame/15)%2)==0;
  if (fork) {
    // 포크: 오른쪽
    for (uint8_t y=6;y<=11;y++) setPixel(13,y, CRGB(150,150,160));
    setPixel(12,6, CRGB(150,150,160)); setPixel(14,6, CRGB(150,150,160));
  } else {
    // 숟가락: 왼쪽
    for (uint8_t y=6;y<=11;y++) setPixel(2,y, CRGB(150,150,160));
    circle(2,6,1, CRGB(150,150,160));
  }
  // 입: 살짝 벌어진
  for (uint8_t x=6;x<=9;x++) setPixel(x, 12, CHSV(0,150, 120 + (frame%10<5?40:0)));
}

static inline void renderAteAll(uint32_t frame) {
  clearAll();
  // 접시 비워짐 + 만족스러운 얼굴
  circle(8,9,4, CRGB(90,90,20));
  drawEye(4,5,(frame/8)%2,0, CRGB::White, CRGB::Black);
  drawEye(10,5,(frame/8)%2,0, CRGB::White, CRGB::Black);
  // 만족 미소
  for (uint8_t x=5;x<=10;x++) setPixel(x, 12, CRGB(220,180,80));
  setPixel(4,11, CRGB(200,160,70)); setPixel(11,11, CRGB(200,160,70));
  // 반짝이는 별 둘
  uint8_t tw = (frame/5)%3; // 0..2
  if (tw==0) { setPixel(1,14, CRGB::Yellow); setPixel(14,14, CRGB::Yellow);} else if (tw==1) { setPixel(1,14, CRGB(120,120,0)); setPixel(14,14, CRGB(120,120,0)); }
}

// Render router
static inline void renderExpression(uint8_t expr, uint32_t frame) {
  switch (expr) {
    case EXPR_NEUTRAL:    renderNeutral(frame); break;
    case EXPR_HAPPY:      renderHappy(frame); break;
    case EXPR_HEART:      renderHeart(frame); break;
    case EXPR_HUG:        renderHug(frame); break;
    case EXPR_TRACKING:   renderTracking(frame); break;
    case EXPR_THINKING:   renderThinking(frame); break;
    case EXPR_FOLLOW_ON:  renderFollowOn(frame); break;
    case EXPR_ERROR:      renderError(frame); break;
    case EXPR_HELLO:      renderHello(frame); break;
    case EXPR_SCISSORS:   renderScissors(frame); break;
    case EXPR_ROCK:       renderRock(frame); break;
    case EXPR_PAPER:      renderPaper(frame); break;
  case EXPR_GOOD_MORNING: renderGoodMorning(frame); break;
  case EXPR_GOOD_NIGHT:   renderGoodNight(frame); break;
  case EXPR_HUNGRY:       renderHungry(frame); break;
  case EXPR_ATE_ALL:      renderAteAll(frame); break;
    default:              renderNeutral(frame); break;
  }
}
