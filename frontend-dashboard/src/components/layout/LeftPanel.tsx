import RobotStateMachine from '../robot/RobotStateMachine'
// import VoiceMonitor from '../voice/VoiceMonitor'
// import RobotArmController from '../robot/RobotArmController'
import SystemStatus from '../monitoring/SystemStatus'
// import TodayStatistics from '../monitoring/TodayStatistics'
// import QuickActionButtons from '../ui/QuickActionButtons'
// import { useMqttRobot } from '../../hooks/useMqttRobot'

interface LeftPanelProps {
  // MQTT 연결로 로봇 상태를 받으므로 props 불필요
}

export default function LeftPanel({}: LeftPanelProps) {
  // const { leftArm, rightArm, connectionStatus } = useMqttRobot()
  return (
    // 🔹 그리드에서 주어진 높이를 꽉 채우도록 설정
    <div className="col-span-1 w-full h-full min-h-0 z-0">
      {/* 🔹 내부를 세로 flex 레이아웃으로 만들고 전체 높이 채우기 */}
      <div className="py-4 pl-4 h-full flex flex-col space-y-6">
        {/* System Status – 내용만큼만 높이 사용 */}
        <SystemStatus />

        {/* Robot State Machine – 남은 공간 전체를 차지 */}
        <div className="flex-1 min-h-0">
          <RobotStateMachine />
        </div>

        {/* Voice Monitor (STT/TTS) */}
        {/* <h2 className="text-lg font-semibold text-cyan-400 mb-4">Voice Monitor</h2>
        <div className="mb-8">
          <VoiceMonitor />
        </div> */}

        {/* Robot Arm Status
        <h2 className="text-lg font-semibold text-cyan-400 mb-4">Robot Arm Status</h2>
        <div className="mb-8">
          <RobotArmController
            leftArm={leftArm}
            rightArm={rightArm}
            connectionStatus={connectionStatus}
          />
        </div> */}

        {/* Today's Statistics */}
        {/* <h2 className="text-lg font-semibold text-cyan-400 mb-4">Today's Statistics</h2>
        <div className="mb-8">
          <TodayStatistics />
        </div> */}

        {/* Quick Actions */}
        {/* <h2 className="text-lg font-semibold text-cyan-400 mb-4">Quick Actions</h2>
        <QuickActionButtons /> */}
      </div>
    </div>
  )
}
