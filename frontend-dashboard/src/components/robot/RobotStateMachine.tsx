import { useState, useEffect, useRef } from 'react'
import SockJS from 'sockjs-client'
import { Client } from '@stomp/stompjs'
// import RobotDiagram from './RobotDiagram'
import { stateConfig, RobotState } from './stateConfig'
import { useRobotState } from '../../context/RobotStateContext'
// import PortalTooltip from '../ui/PortalTooltip'

const stateStyles: Record<
  string,
  {
    background: string
    border: string
    text: string
    indicator: string
  }
> = {
  gray: {
    background: 'bg-gradient-to-br from-gray-500/20 to-gray-500/5',
    border: 'border-gray-500/50',
    text: 'text-gray-400',
    indicator: 'bg-gray-400',
  },
  cyan: {
    background: 'bg-gradient-to-br from-cyan-500/20 to-cyan-500/5',
    border: 'border-cyan-500/50',
    text: 'text-cyan-400',
    indicator: 'bg-cyan-400',
  },
  pink: {
    background: 'bg-gradient-to-br from-pink-500/20 to-pink-500/5',
    border: 'border-pink-500/50',
    text: 'text-pink-400',
    indicator: 'bg-pink-400',
  },
  purple: {
    background: 'bg-gradient-to-br from-purple-500/20 to-purple-500/5',
    border: 'border-purple-500/50',
    text: 'text-purple-400',
    indicator: 'bg-purple-400',
  },
  green: {
    background: 'bg-gradient-to-br from-green-500/20 to-green-500/5',
    border: 'border-green-500/50',
    text: 'text-green-400',
    indicator: 'bg-green-400',
  },
  yellow: {
    background: 'bg-gradient-to-br from-yellow-500/20 to-yellow-500/5',
    border: 'border-yellow-500/50',
    text: 'text-yellow-400',
    indicator: 'bg-yellow-400',
  },
  blue: {
    background: 'bg-gradient-to-br from-blue-500/20 to-blue-500/5',
    border: 'border-blue-500/50',
    text: 'text-blue-400',
    indicator: 'bg-blue-400',
  },
  orange: {
    background: 'bg-gradient-to-br from-orange-500/20 to-orange-500/5',
    border: 'border-orange-500/50',
    text: 'text-orange-400',
    indicator: 'bg-orange-400',
  },
  teal: {
    background: 'bg-gradient-to-br from-teal-500/20 to-teal-500/5',
    border: 'border-teal-500/50',
    text: 'text-teal-400',
    indicator: 'bg-teal-400',
  },
  indigo: {
    background: 'bg-gradient-to-br from-indigo-500/20 to-indigo-500/5',
    border: 'border-indigo-500/50',
    text: 'text-indigo-400',
    indicator: 'bg-indigo-400',
  },
  red: {
    background: 'bg-gradient-to-br from-red-500/20 to-red-500/5',
    border: 'border-red-500/50',
    text: 'text-red-400',
    indicator: 'bg-red-400',
  },
}

type BackendStatusMessage = {
  id: number // robotId
  status: string // 상태값 (string)
}

const stateMessages: Record<RobotState, string> = {
  IDLE: '대기중',
  HEART: '사랑해',
  HUG: '안아줘',
  HI: '안녕',
  WARMUP: '준비운동',
  ROCK: '바위',
  SCISSORS: '가위',
  PAPER: '보',
  GOOD_MORNING: '좋은 아침',
  GOOD_NIGHT: '잘자',
  ATE_ALL: '배불러',
  HUNGRY: '배고파',
  SET_JOINT: '동작 설정중',
  UNKNOWN: '모르겠어',
}

export default function RobotStateMachine({ robotId = 1 }: { robotId?: number }) {
  const { currentState, setCurrentState } = useRobotState()
  const [isConnected, setIsConnected] = useState(false)
  const clientRef = useRef<Client | null>(null)

  useEffect(() => {
    const WS_URL = import.meta.env.VITE_WS_URL

    const socket = new SockJS(`${WS_URL}/ws-stomp`)
    const client = new Client({
      webSocketFactory: () => socket,
      reconnectDelay: 3000,
      onConnect: () => {
        console.log('WebSocket connected')
        setIsConnected(true)

        client.subscribe(`/sub/robot/${robotId}`, (frame) => {
          try {
            const backendMessage = JSON.parse(frame.body) as BackendStatusMessage
            const statusString = backendMessage.status.toUpperCase()
            const isValidStatus = Object.keys(stateConfig).includes(statusString)
            const newState = isValidStatus ? (statusString as RobotState) : 'UNKNOWN'

            setCurrentState(newState)
          } catch (error) {
            console.error('Error parsing WebSocket message:', error)
          }
        })
      },
      onDisconnect: () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
      },
      onStompError: (error) => {
        console.error('STOMP error:', error)
        setIsConnected(false)
      },
    })

    client.activate()
    clientRef.current = client

    return () => {
      client.deactivate()
      clientRef.current = null
    }
  }, [robotId, setCurrentState])

  const config = stateConfig[currentState]
  const styles = stateStyles[config.color]

  return (
    <div className="h-full flex flex-col">
      <h2 className="text-md font-semibold text-white mb-2">ROBOT STATUS</h2>

      {/* 현재 상태 */}
      <div
        className={`bg-gray-700/40 rounded-2xl p-4 mb-4 ${styles.background} border-2 ${styles.border} relative`}
      >
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400 font-semibold">
            ROBOT #{robotId} 상태
          </span>
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'
              }`}
            />
            <span className="text-sm text-gray-400">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-4xl">{config.emoji}</div>
          <div>
            <div className={`text-2xl font-bold ${styles.text}`}>{currentState}</div>
            <div className="text-sm text-gray-500">{config.label}</div>
          </div>
        </div>

        <div className="mt-3 h-1 bg-black/60 rounded-full overflow-hidden">
          <div
            className={`h-full bg-${config.color}-400`}
            style={{
              width: '100%',
              animation: 'pulse 2s ease-in-out infinite',
            }}
          />
        </div>
      </div>

      {/* <PortalTooltip
        anchorRect={anchorRect}
        visible={isHovering}
        placement="right"
        offset={8}
        className="w-72"
      >
        <RobotDiagram currentState={currentState} />
      </PortalTooltip>

      {/* 상태 메시지 */}
      <div
        className={`bg-gray-700/40 rounded-2xl p-4 ${styles.background} border-2 ${styles.border} relative`}
      >
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400 font-semibold">
            ROBOT #{robotId} 🔊
          </span>
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'
              }`}
            />
            <span className="text-sm text-gray-400">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-4xl">{config.emoji}</div>
          <div>
            <div className={`text-2xl font-bold ${styles.text}`}>
              {stateMessages[currentState]}
            </div>
            <div className="text-sm text-gray-500">{config.label}</div>
          </div>
        </div>

        <div className="mt-3 h-1 bg-black/60 rounded-full overflow-hidden">
          <div
            className={`h-full bg-${config.color}-400`}
            style={{
              width: '100%',
              animation: 'pulse 2s ease-in-out infinite',
            }}
          />
        </div>
      </div>

      {/* 히스토리/툴팁은 현재 미사용
      <PortalTooltip ...>
        <RobotDiagram ... />
      </PortalTooltip>
      */}
    </div>
  )
}
