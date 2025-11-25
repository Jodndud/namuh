export type RobotState = 'IDLE' | 'HEART' | 'HUG' | 'HI' | 'WARMUP' | 'ROCK' | 'SCISSORS' | 'PAPER' | 'GOOD_MORNING' | 'GOOD_NIGHT' | 'ATE_ALL' | 'HUNGRY' | 'SET_JOINT' | 'UNKNOWN'

export const stateConfig: Record<RobotState, { color: string; label: string; emoji: string }> = {
  IDLE: { color: 'gray', label: '대기 상태', emoji: '😴' },
  HEART: { color: 'pink', label: '로봇 팔로 머리 위 하트를 그리는 상태', emoji: '💖' },
  HUG: { color: 'purple', label: '로봇 팔을 앞으로 하여 안는 상태', emoji: '🤗' },
  HI: { color: 'green', label: '양손으로 인사를 하는 상태', emoji: '👋' },
  WARMUP: { color: 'yellow', label: '체조(가위바위보) 대기상태', emoji: '🤸‍♂️' },
  SCISSORS: { color: 'blue', label: '가위 표현 상태', emoji: '✌️' },
  ROCK: { color: 'orange', label: '바위 표현 상태', emoji: '✊' },
  PAPER: { color: 'teal', label: '보 표현 상태', emoji: '✋' },
  GOOD_MORNING: { color: 'yellow', label: '아침 인사를 하는 상태', emoji: '🌅' },
  GOOD_NIGHT: { color: 'indigo', label: '저녁 인사를 하는 상태', emoji: '🌙' },
  ATE_ALL: { color: 'green', label: '음식을 다 먹은 상태', emoji: '😋' },
  HUNGRY: { color: 'red', label: '배고픈 상태', emoji: '🍽️' },
  SET_JOINT: { color: 'gray', label: '로봇 팔 동작 설정 상태', emoji: '⚙️' },
  UNKNOWN: { color: 'gray', label: 'Unknown', emoji: '❓' },
}


