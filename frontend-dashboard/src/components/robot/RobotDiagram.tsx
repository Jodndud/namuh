import { stateConfig, RobotState } from './stateConfig'

const stateDescriptions: Record<RobotState, string> = {
  IDLE: '대기 상태',
  HEART: '로봇 팔로 머리 위 하트를 그리는 상태',
  HUG: '로봇 팔을 앞으로 하여 안는 상태',
  HI: '오른손으로 손인사를 하는 상태',
  WARMUP: '체조(가위바위보) 대기상태',
  ROCK: '게임의 바위를 낸 상태',
  SCISSORS: '게임의 가위를 낸 상태',
  PAPER: '게임의 보를 낸 상태',
  GOOD_MORNING: '아침 인사를 하는 상태',
  GOOD_NIGHT: '저녁 인사를 하는 상태',
  ATE_ALL: '음식을 다 먹은 상태',
  HUNGRY: '배고픈 상태',
  SET_JOINT: '로봇팔 세팅 중',
  UNKNOWN: '알 수 없는 상태 (오류)',
}

export default function RobotDiagram({
  currentState,
}: {
  currentState: RobotState
}) {
  return (
    <div className="bg-black/40 border border-gray-300 rounded p-2">
      <div className="flex flex-col gap-1">
        {Object.entries(stateConfig).map(([state, cfg]) => (
          <div
            key={state}
            className={`p-2 rounded transition-all ${
              currentState === state
                ? `bg-${cfg.color}-500/30 border-2 border-${cfg.color}-500`
                : 'bg-black/40 border border-gray-700/30'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="text-lg">{cfg.emoji}</div>
              <div className="flex-1">
                <div
                  className={`text-xs font-bold ${
                    currentState === state ? `text-${cfg.color}-400` : 'text-gray-300'
                  }`}
                >
                  {state}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {stateDescriptions[state as RobotState]}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

