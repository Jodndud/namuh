import { useState, useEffect } from 'react'

export default function TopPanel() {
  const [time, setTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date())
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="flex items-center justify-between p-4">
      {/* 시스템 이름 */}
      <div className="flex items-center gap-4">
        <div className="w-7 h-7 rounded-md bg-blue-500" />
        <h1 className="text-2xl font-bold text-white">Humanoid Robot Monitoring System</h1>
      </div>
      {/* 상태 및 시계 박스 */}
      <div className="flex items-center gap-6">
        {/* 시스템 상태 */}
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs text-gray-400">System Online</span>
        </div>
        {/* 녹화 상태 */}
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
          <span className="text-xs text-gray-400">Recording</span>
        </div>

        {/* AI 상태 */}
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-cyan-400" />
          <span className="text-xs text-gray-400">AI Active</span>
        </div>

        {/* 시간 */}
        <div className="text-sm text-white">
          {time.toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}
