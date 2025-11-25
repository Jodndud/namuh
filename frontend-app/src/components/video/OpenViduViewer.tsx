import { useCallback, useEffect, useRef, useState } from 'react'
import { OpenVidu, Session, StreamEvent, Subscriber } from 'openvidu-browser'

type ViewerProps = {
  channelId?: string
  participantId?: string
  className?: string
  muted?: boolean
}

type ConnectionState = {
  loading: boolean
  error: string | null
  subscriber: Subscriber | null
}

export default function OpenViduViewer({
  channelId = 'robot-channel-001',
  participantId = 'mobile-viewer',
  className = '',
  muted = true
}: ViewerProps) {
  const [state, setState] = useState<ConnectionState>({
    loading: false,
    error: null,
    subscriber: null
  })

  const ovRef = useRef<OpenVidu | null>(null)
  const sessionRef = useRef<Session | null>(null)
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const isConnectingRef = useRef(false)
  const isConnectedRef = useRef(false)

  const attachVideoElement = useCallback((el: HTMLVideoElement) => {
    videoRef.current = el
    if (state.subscriber && videoRef.current) {
      state.subscriber.addVideoElement(videoRef.current)
    }
  }, [state.subscriber])

  const disconnect = useCallback(() => {
    try {
      sessionRef.current?.disconnect()
    } catch {
      // ignore
    } finally {
      isConnectedRef.current = false
      isConnectingRef.current = false
      ovRef.current = null
      sessionRef.current = null
      setState(prev => ({ ...prev, subscriber: null }))
    }
  }, [])

  const connect = useCallback(async () => {
    if (isConnectingRef.current || isConnectedRef.current) return
    isConnectingRef.current = true
    setState(prev => ({ ...prev, loading: true, error: null }))

    try {
      const baseUrl = 'https://api.buriburi.monster/spring'
      const res = await fetch(`${baseUrl}/v1/channels/${channelId}/connections`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ participantId, role: 'SUBSCRIBER' })
      })
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`)
      }
      const data = await res.json() as { isSuccess: boolean; result?: { token: string }; message?: string }
      if (!data.isSuccess || !data.result?.token) {
        throw new Error(data.message || 'Failed to obtain OpenVidu token')
      }
      const token = data.result.token

      ovRef.current = new OpenVidu()
      const session = ovRef.current.initSession()

      session.on('streamCreated', (event: StreamEvent) => {
        const subscriber = session.subscribe(event.stream, undefined)
        setState(prev => ({ ...prev, subscriber }))
        subscriber.on('videoElementCreated', (e) => {
          const element = e.element as HTMLVideoElement
          if (videoRef.current) {
            subscriber.addVideoElement(videoRef.current)
          } else {
            // fallback: use created element
            element.style.width = '100%'
            element.style.height = '100%'
          }
        })
      })

      session.on('streamDestroyed', () => {
        setState(prev => ({ ...prev, subscriber: null }))
      })

      await session.connect(token)
      sessionRef.current = session
      isConnectedRef.current = true
      setState(prev => ({ ...prev, loading: false }))
    } catch (err: any) {
      console.error('OpenVidu connect error:', err)
      setState(prev => ({ ...prev, loading: false, error: err?.message || 'Connection failed' }))
      isConnectingRef.current = false
    }
  }, [channelId, participantId])

  useEffect(() => {
    connect()
    return () => {
      if (isConnectedRef.current) disconnect()
    }
  }, [connect, disconnect])

  return (
    <div className={`relative w-full bg-black rounded-2xl overflow-hidden ${className}`}>
      <video
        ref={attachVideoElement as any}
        className="w-full h-full object-cover"
        autoPlay
        playsInline
        muted={muted}
        style={{ display: state.subscriber ? 'block' : 'none', minHeight: 240 }}
      />

      {!state.subscriber && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/80">
          {state.loading ? (
            <div className="text-cyan-400 text-center">
              <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
              <p>연결 중...</p>
            </div>
          ) : state.error ? (
            <div className="text-red-400 text-center">
              <p className="mb-2">연결 실패</p>
              <p className="text-sm text-gray-400">{state.error}</p>
            </div>
          ) : (
            <div className="text-gray-400 text-center">
              <p>카메라 연결 대기 중</p>
            </div>
          )}
        </div>
      )}

      {state.subscriber && (
        <div className="absolute top-3 left-3 flex items-center gap-2 bg-black/70 px-2.5 py-1.5 rounded">
          <div className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse" />
          <span className="text-red-400 text-xs font-bold">LIVE</span>
        </div>
      )}
    </div>
  )
}


