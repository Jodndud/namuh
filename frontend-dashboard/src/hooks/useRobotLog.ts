import { useCallback } from 'react'

const LOG_KEY = 'LOG'

export interface RobotLogEntry {
  type: string
  ts: string | number
  rb_command: string
  sound: string
}

interface RobotLogInput {
  type: string
  ts: string | number
  rb_command: string
}

const commandToState: Record<string, string> = {
  init_pose: '',
  set_joint: '로봇 팔 동작 세팅중',
  make_heart: '사랑해',
  make_hug: '안아줄게',
  make_hi: '안녕?',
  warm_up: '시작할게',
  rock: '바위',
  scissors: '가위',
  paper: '보',
  good_morning: '좋은아침~',
  good_night: '잘자~',
  ate_all: '이 닦을 시간이야~',
  hungry: '배고프다 밥먹을 시간이야!',
}

const typeToMessage: Record<string, string> = {
  ack: '동작시작',
  progress: '동작중',
  result: '동작완료',
  error: '에러',
}

function getMappedType(type: string): string {
  if (typeToMessage[type]) {
    return typeToMessage[type]
  }
  return '알수없음'
}


function getSound(command: string): string {
  return commandToState[command] ?? '모르는 명령이야...'
}

function getStoredLogs(): RobotLogEntry[] {
  try {
    const raw = localStorage.getItem(LOG_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export function useRobotLog(maxLogs: number = 20) {
  const appendLog = useCallback(
    (entry: RobotLogInput) => {
      const { type, ts, rb_command } = entry

      const newLog: RobotLogEntry = {
        type: getMappedType(type),
        ts,
        rb_command,
        sound: getSound(rb_command),
      }

      const prevLogs = getStoredLogs()
      let logs = [...prevLogs, newLog]

      if (logs.length > maxLogs) {
        logs = logs.slice(logs.length - maxLogs)
      }

      localStorage.setItem(LOG_KEY, JSON.stringify(logs))
    },
    [maxLogs]
  )

  const getLogs = useCallback(() => getStoredLogs(), [])
  const clearLogs = useCallback(() => localStorage.removeItem(LOG_KEY), [])

  return { appendLog, getLogs, clearLogs }
}
