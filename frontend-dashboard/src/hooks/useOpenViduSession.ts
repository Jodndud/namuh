import { useState, useEffect, useRef, useCallback } from 'react'
import { OpenVidu, Session, StreamEvent, Subscriber } from 'openvidu-browser'
import { createChannelConnection } from '../services/openvidu'

interface UseOpenViduProps {
  channelId: string
  participantId: string
  role?: 'PUBLISHER' | 'SUBSCRIBER'
  autoConnect?: boolean
}

interface ConnectionState {
  session: Session | null
  connected: boolean
  error: string | null
  loading: boolean
  subscriber: Subscriber | null
  streamInfo: {
    resolution: string
    fps: number
    bitrate: string
  } | null
}

export function useOpenViduSession({
  channelId,
  participantId,
  role = 'SUBSCRIBER',
  autoConnect = true
}: UseOpenViduProps) {
  const [connectionState, setConnectionState] = useState<ConnectionState>({
    session: null,
    connected: false,
    error: null,
    loading: false,
    subscriber: null,
    streamInfo: null
  })

  const ovRef = useRef<OpenVidu | null>(null)
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const isConnectingRef = useRef(false)
  const isConnectedRef = useRef(false)

  const connectToSession = useCallback(async () => {
    if (isConnectingRef.current || isConnectedRef.current) {
      console.log('Connection already in progress or established, skipping...')
      return
    }

    try {
      isConnectingRef.current = true
      console.log('Starting OpenVidu connection...')
      setConnectionState(prev => ({ ...prev, loading: true, error: null }))
      
      // 1. 백엔드에서 토큰 발급받기 (올바른 API URL 사용)
      const data = await createChannelConnection(channelId, participantId, role)
      
      if (!data.isSuccess) {
        throw new Error(data.message || 'Failed to get token')
      }
      
      // 백엔드에서 받은 전체 토큰 URL 사용
      const connectionToken = data.result.token
      console.log('Received connection token:', connectionToken)
      
      console.log('Requesting channel:', channelId)
      console.log('Full token response:', data)

      const sessionFromToken = connectionToken.match(/sessionId=([^&]+)/)?.[1]
      console.log('Backend created session:', sessionFromToken)
      console.log('Frontend requested channel:', channelId)
      
      // 2. OpenVidu 세션 생성 및 연결
      ovRef.current = new OpenVidu()
      
      // OpenVidu 서버 URL 명시적 설정
      ovRef.current.setAdvancedConfiguration({
        publisherSpeakingEventsOptions: undefined,
        iceServers: undefined
      })
      
      const session = ovRef.current.initSession()
      
      // 스트림 수신 이벤트 리스너
      session.on('streamCreated', (event: StreamEvent) => {
        console.log('Stream created:', event.stream)
        const subscriber = session.subscribe(event.stream, undefined)

        setConnectionState(prev => ({
            ...prev,
            subscriber
        }))
        
        subscriber.on('videoElementCreated', (event) => {
          const videoElement = event.element as HTMLVideoElement
          setConnectionState(prev => ({ 
            ...prev,
            streamInfo: {
              resolution: `${videoElement.videoWidth}x${videoElement.videoHeight}`,
              fps: 30,
              bitrate: '5.2 Mbps'
            }
          }))
          
          if (videoRef.current) {
            subscriber.addVideoElement(videoRef.current)
          }
        })
      })
      
      session.on('connectionCreated', (event) => {
        console.log('Connection created:', event.connection)
      })
      
      session.on('sessionConnected' as any, (event: any) => {
        console.log('Session connected:', event)
      })

      session.on('streamDestroyed', (event: StreamEvent) => {
        console.log('Stream destroyed:', event.stream)
        setConnectionState(prev => ({ 
          ...prev, 
          subscriber: null,
          streamInfo: null 
        }))
      })

      session.on('exception', (exception) => {
        console.error('Session exception:', exception)
        setConnectionState(prev => ({ 
          ...prev, 
          error: exception.message 
        }))
      })
      
      // 전체 connection token으로 세션 연결
      await session.connect(connectionToken)
      
      isConnectedRef.current = true
      setConnectionState(prev => ({
        ...prev,
        session,
        connected: true,
        loading: false
      }))
      
      console.log('Successfully connected to OpenVidu session')
      
    } catch (error) {
      console.error('OpenVidu connection error:', error)
      setConnectionState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Connection failed',
        loading: false
      }))
    } finally {
      isConnectingRef.current = false
    }
  }, [channelId, participantId, role])

  const disconnect = useCallback(async () => {
    if (connectionState.session) {
      await connectionState.session.disconnect()
    }
    
    isConnectingRef.current = false
    isConnectedRef.current = false
    
    setConnectionState({
      session: null,
      connected: false,
      error: null,
      loading: false,
      subscriber: null,
      streamInfo: null
    })

    console.log('OpenVidu session disconnected')
  }, [connectionState.session])

  // 비디오 요소에 스트림 연결
  const attachVideoElement = useCallback((element: HTMLVideoElement) => {
    videoRef.current = element
    
    if (connectionState.subscriber) {
      connectionState.subscriber.addVideoElement(element)
    }
  }, [connectionState.subscriber])

  // 자동 연결
  useEffect(() => {
    if (autoConnect && channelId && participantId && !isConnectedRef.current && !isConnectingRef.current) {
      console.log('Auto-connecting to OpenVidu session...')
      connectToSession()
    }
  }, [autoConnect, channelId, participantId, connectToSession])

  // 컴포넌트 언마운트 시 정리
  useEffect(() => {
    return () => {
      // 실제로 연결되어 있을 때만 해제
      if (isConnectedRef.current && connectionState.session) {
        console.log('Cleanup: Disconnecting OpenVidu session')
        disconnect()
      }
    }
  }, [])

  return {
    ...connectionState,
    connectToSession,
    disconnect,
    attachVideoElement,
    videoRef
  }
}