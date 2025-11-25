interface RobotStatus {
  joint0: number
  joint1: number
  joint2: number
  joint3: number
  joint4: number
  joint5: number
  gripper: number
  lastUpdated?: Date
  connected: boolean
}

interface RobotArmControllerProps {
  leftArm: RobotStatus
  rightArm: RobotStatus
  connectionStatus: 'connected' | 'disconnected' | 'connecting'
}

export default function RobotArmController({
  leftArm,
  rightArm,
  connectionStatus
}: RobotArmControllerProps) {
  const joints = [
    { key: 'joint0', label: 'Joint 0 (Base)' },
    { key: 'joint1', label: 'Joint 1 (Shoulder)' },
    { key: 'joint2', label: 'Joint 2 (Elbow)' },
    { key: 'joint3', label: 'Joint 3 (Wrist 1)' },
    { key: 'joint4', label: 'Joint 4 (Wrist 2)' },
    { key: 'joint5', label: 'Joint 5 (Wrist 3)' },
    { key: 'gripper', label: 'Gripper' }
  ]

  const formatLastUpdated = (date?: Date) => {
    if (!date) return 'Never'
    return date.toLocaleTimeString()
  }

  return (
    <div className="space-y-4">
      {/* Connection Status */}
      <div className="bg-black/40 border border-gray-500/20 rounded p-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-400">MQTT Connection</span>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${
              connectionStatus === 'connected' ? 'bg-green-500' : 
              connectionStatus === 'connecting' ? 'bg-yellow-500' : 'bg-red-500'
            }`} />
            <span className={`text-xs font-mono ${
              connectionStatus === 'connected' ? 'text-green-400' : 
              connectionStatus === 'connecting' ? 'text-yellow-400' : 'text-red-400'
            }`}>
              {connectionStatus.toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      {/* Left Arm Status */}
      <div className="bg-black/40 border border-cyan-500/20 rounded p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-cyan-400">Left Robot (robot_left)</h3>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${leftArm.connected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-xs text-gray-400">
              {formatLastUpdated(leftArm.lastUpdated)}
            </span>
          </div>
        </div>
        <div className="space-y-3">
          {joints.map(({ key, label }) => (
            <div key={`left-${key}`}>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs text-gray-400">{label}</label>
                <span className="text-xs text-cyan-400 font-mono">
                  {String(typeof leftArm[key as keyof RobotStatus] === 'number' ? leftArm[key as keyof RobotStatus] : 0)}°
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="180"
                value={leftArm[key as keyof RobotStatus] as number}
                disabled
                className="w-full h-2 bg-black/60 rounded-lg appearance-none cursor-default accent-cyan-500 opacity-70"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Right Arm Status */}
      <div className="bg-black/40 border border-purple-500/20 rounded p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-purple-400">Right Robot (robot_right)</h3>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${rightArm.connected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-xs text-gray-400">
              {formatLastUpdated(rightArm.lastUpdated)}
            </span>
          </div>
        </div>
        <div className="space-y-3">
          {joints.map(({ key, label }) => (
            <div key={`right-${key}`}>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs text-gray-400">{label}</label>
                <span className="text-xs text-purple-400 font-mono">
                  {String(typeof rightArm[key as keyof RobotStatus] === 'number' ? rightArm[key as keyof RobotStatus] : 0)}°
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="180"
                value={rightArm[key as keyof RobotStatus] as number}
                disabled
                className="w-full h-2 bg-black/60 rounded-lg appearance-none cursor-default accent-purple-500 opacity-70"
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
