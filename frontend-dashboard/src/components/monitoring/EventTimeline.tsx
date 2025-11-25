import { useState, useEffect } from 'react'

type EventType = '동작시작' | '동작중' | '동작완료' | '에러'

interface TimelineEvent {
  timestamp: string
  type: EventType
  message: string
  details?: string
}

interface RobotLogEntry {
  type: EventType
  ts: string
  rb_command: string
  sound: string
}

const LOG_KEY = 'LOG'

// 상태별 색상
const eventTypeConfig: Record<EventType, {
  borderClass: string
  bgClass: string
  textClass: string
  tagBgClass: string
}> = {
  동작시작: {
    borderClass: 'border-green-500',
    bgClass: 'bg-gradient-to-r from-green-500/10 to-transparent',
    textClass: 'text-green-400',
    tagBgClass: 'bg-green-500/20',
  },
  동작중: {
    borderClass: 'border-gray-500',
    bgClass: 'bg-gradient-to-r from-gray-500/10 to-transparent',
    textClass: 'text-gray-400',
    tagBgClass: 'bg-gray-500/20',
  },
  동작완료: {
    borderClass: 'border-blue-500',
    bgClass: 'bg-gradient-to-r from-blue-500/10 to-transparent',
    textClass: 'text-blue-400',
    tagBgClass: 'bg-blue-500/20',
  },
  에러: {
    borderClass: 'border-red-500',
    bgClass: 'bg-gradient-to-r from-red-500/10 to-transparent',
    textClass: 'text-red-400',
    tagBgClass: 'bg-red-500/20',
  },
}

function formatTimestamp(ts: string): string {
  const date = new Date(ts)

  const yyyy = date.getFullYear()
  const mm = String(date.getMonth() + 1).padStart(2, '0')
  const dd = String(date.getDate()).padStart(2, '0')
  const hh = String(date.getHours()).padStart(2, '0')
  const min = String(date.getMinutes()).padStart(2, '0')
  const ss = String(date.getSeconds()).padStart(2, '0')

  return `${yyyy}-${mm}-${dd} ${hh}:${min}:${ss}`
}

function mapLogToTimelineEvent(log: RobotLogEntry): TimelineEvent {
  const validTypes: EventType[] = ['동작시작', '동작중', '동작완료', '에러']

  const safeType: EventType =
    validTypes.includes(log.type as EventType)
      ? (log.type as EventType)
      : '에러'

  return {
    timestamp: formatTimestamp(log.ts),
    type: safeType,
    message: log.rb_command,
    details: log.sound,
  }
}

export default function EventTimeline() {
  const [events, setEvents] = useState<TimelineEvent[]>([])

  useEffect(() => {
    const loadLogs = () => {
      try {
        const raw = localStorage.getItem(LOG_KEY)
        if (!raw) return

        const logs: RobotLogEntry[] = JSON.parse(raw)

        const mapped = logs
          .slice(-20)       // 최근 20개
          .reverse()        // 최신 위로
          .map(mapLogToTimelineEvent)

        setEvents(mapped)
      } catch (e) {
        console.error('Failed to load logs from localStorage:', e)
      }
    }

    loadLogs()

    // 1초마다 새 로그 반영
    const interval = setInterval(loadLogs, 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="bg-gray-700/40 rounded-2xl p-4 h-full flex flex-col">
      <div className="text-md font-semibold text-white mb-3">
        EVENT TIMELINE
      </div>

      <div className="space-y-2 flex-1 min-h-0 overflow-y-auto">
        {events.length === 0 ? (
          <div className="text-center text-gray-600 text-xs italic py-8">
            No events to display
          </div>
        ) : (
          events.map((event, index) => {
            const config = eventTypeConfig[event.type]

            return (
              <div
                key={index}
                className={`p-3 border-l-3 ${config.borderClass} ${config.bgClass} rounded transition-all`}
              >
                <div className="flex items-center gap-2 mb-3">
                  {/* 상태 태그 */}
                  <span
                    className={`text-sm px-1.5 py-0.5 rounded font-mono ${config.tagBgClass} ${config.textClass}`}
                  >
                    {event.type}
                  </span>

                  {/* 시간 */}
                  <span className="text-sm text-gray-500 font-mono">
                    {event.timestamp}
                  </span>
                </div>

                {/* 명령어 */}
                <div className="text-md text-white font-medium mb-1">
                  {event.message}
                </div>

                {/* 상세 정보 (sound) */}
                {event.details && (
                  <div className="text-sm text-gray-500 italic">
                    🔊 {event.details}
                  </div>
                )}
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
