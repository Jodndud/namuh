import { useEffect, useRef } from 'react'
import { useOpenViduSession } from '../../hooks/useOpenViduSession'

interface RobotPOVProps {
  channelId?: string
  robotId?: string
  onExpand?: () => void
  // 중앙 영역에서 가로를 꽉 채우고 세로는 비율 유지(레터박스)용
  fitMode?: 'cover' | 'contain-width'
  // 외곽 프레임(보더) 표시 여부
  showFrame?: boolean
}


export default function RobotPOV({ 
  channelId = 'robot-channel-001',
  robotId = 'dashboard-viewer',
  onExpand,
  fitMode = 'cover',
  showFrame = true,
}: RobotPOVProps) {
  const videoRef = useRef<HTMLVideoElement>(null)

  const {
    loading,
    error,
    subscriber,
    // streamInfo,
    attachVideoElement
  } = useOpenViduSession({
    channelId,
    participantId: robotId,
    role: 'SUBSCRIBER',
    autoConnect: true
  })

  // 비디오 요소가 생성되면 훅에 전달
  useEffect(() => {
    if (videoRef.current) {
        attachVideoElement(videoRef.current)
    }
  }, [attachVideoElement])

  const containerClass =
    `w-full h-full bg-black ${showFrame ? 'border border-cyan-500/30' : ''} ` +
    `rounded relative overflow-hidden cursor-pointer ` +
    `${fitMode === 'contain-width' ? 'flex items-center justify-center' : ''}`

  const videoClass =
    fitMode === 'contain-width'
      ? 'w-full h-auto max-h-full object-contain'
      : 'w-full h-full object-cover'

  return (
    <div
      className={containerClass}
      onClick={onExpand}
      
    >
      {/* WebRTC 비디오 스트림 */}
      <video
        ref={videoRef}
        className={videoClass}
        autoPlay
        playsInline
        muted
        style={{ display: subscriber ? 'block' : 'none' }} // 이 부분은 이미 올바르게 수정되었습니다.
      />

      {!subscriber && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/80">
          {loading && (
            <div className="text-cyan-400 text-center">
              <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
              <p>연결 중...</p>
            </div>
          )}
          {error && (
            <div className="text-red-400 text-center">
              <p className="mb-2">연결 실패</p>
              <p className="text-sm text-gray-400">{error}</p>
            </div>
          )}
          {/* subscriber가 없고, 로딩도 아니고, 에러도 아닌 초기 상태 */}
          {!loading && !error && !subscriber && (
            <div className="text-gray-400 text-center">
              <p>카메라 연결 대기 중</p>
            </div>
          )}
        </div>
      )}

      {subscriber && (
        <div className="absolute top-1.5 left-1.5 flex items-center gap-2 bg-red-500/90 px-2 py-1 rounded">
          <div className="w-2 h-2 rounded-full bg-white animate-pulse" />
          <span className="text-white text-xs font-bold">LIVE</span>
        </div>
      )}

      {/* 타임스탬프 (이하 동일) */}
      {/* <div className="absolute top-4 right-4 bg-black/70 px-3 py-2 rounded font-mono text-cyan-400 text-sm">
          {new Date().toLocaleTimeString()}
      </div> */}

      {/* 하단 정보 바 */}
      {/* <div className="absolute bottom-0 left-0 right-0 bg-black/80 p-3 border-t border-cyan-500/30">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-4">
            <span className="text-gray-400">Resolution: <span className="text-cyan-400">
              {streamInfo?.resolution || '1920x1080'}
            </span></span>
              <span className="text-gray-400">FPS: <span className="text-green-400">
              {streamInfo?.fps || 30}
            </span></span>
              <span className="text-gray-400">Bitrate: <span className="text-cyan-400">
              {streamInfo?.bitrate || '5.2 Mbps'}
            </span></span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-gray-400">Status:</span>
            <span className={`px-2 py-0.5 rounded ${
              subscriber
                ? 'bg-green-500/20 text-green-400'
                : loading
                    ? 'bg-yellow-500/20 text-yellow-400'
                    : 'bg-red-500/20 text-red-400'
            }`}>
              {subscriber ? 'Connected' : loading ? 'Connecting' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div> */}
    </div>
  )
}
