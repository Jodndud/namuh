import { useState, useEffect } from 'react'

interface STTResult {
  timestamp: string
  text: string
  confidence: number
  action?: string
}

interface TTSOutput {
  timestamp: string
  text: string
  status: 'queued' | 'playing' | 'completed'
  duration?: string
}

export default function VoiceMonitor() {
  const [sttResults, setSttResults] = useState<STTResult[]>([
    { timestamp: '14:32:45', text: '사랑해', confidence: 96.5, action: 'HEART' },
    { timestamp: '14:30:12', text: '안녕', confidence: 94.2, action: 'HI' },
    { timestamp: '14:28:34', text: '가위바위보하자', confidence: 92.8, action: 'GAME' },
  ])

  const [ttsQueue, setTtsQueue] = useState<TTSOutput[]>([
    { timestamp: '14:32:46', text: '사랑해', status: 'playing', duration: '1.2s' },
    { timestamp: '14:32:50', text: '또 놀자!', status: 'queued', duration: '1.5s' },
  ])

  const [isListening] = useState(true)
  const [currentSTT, setCurrentSTT] = useState('')

  // 시뮬레이션: STT 실시간 입력
  useEffect(() => {
    const phrases = ['사랑해', '안녕', '안아줘', '가위바위보하자', '']
    let phraseIndex = 0

    const interval = setInterval(() => {
      const phrase = phrases[phraseIndex % phrases.length]
      setCurrentSTT(phrase)
      phraseIndex++

      if (phrase && Math.random() > 0.5) {
        const now = new Date().toLocaleTimeString()
        const confidence = 85 + Math.random() * 15
        const actions: Record<string, string> = {
          '사랑해': 'HEART',
          '안녕': 'HI',
          '안아줘': 'HUG',
          '가위바위보하자': 'GAME'
        }

        setSttResults(prev => [
          { timestamp: now, text: phrase, confidence, action: actions[phrase] },
          ...prev.slice(0, 4)
        ])
      }
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  // 시뮬레이션: TTS 상태 변경
  useEffect(() => {
    const interval = setInterval(() => {
      setTtsQueue(prev => {
        const updated = [...prev]
        if (updated.length > 0 && updated[0].status === 'playing') {
          updated[0].status = 'completed'
          if (updated.length > 1) {
            updated[1].status = 'playing'
          }
        }
        return updated.filter(item => item.status !== 'completed')
      })
    }, 4000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-3">
      {/* STT (Speech-to-Text) */}
      <div className="bg-black/40 border border-cyan-500/20 rounded p-3">
        <div className="flex items-center justify-between mb-3">
          <div className="text-xs text-gray-400 font-semibold">STT MONITOR</div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isListening ? 'bg-green-400 animate-pulse' : 'bg-gray-600'}`} />
            <span className="text-xs text-gray-500">{isListening ? 'Listening' : 'Idle'}</span>
          </div>
        </div>

        {/* 실시간 입력 표시 */}
        <div className="mb-3 p-3 bg-black/60 border border-cyan-500/10 rounded">
          <div className="text-xs text-gray-500 mb-1">Current Input:</div>
          <div className="text-cyan-400 font-mono text-lg min-h-[28px]">
            {currentSTT || <span className="text-gray-600 italic">waiting...</span>}
            {currentSTT && <span className="animate-pulse">|</span>}
          </div>
        </div>

        {/* STT 결과 히스토리 */}
        <div className="space-y-2 max-h-40 overflow-y-auto">
          {sttResults.map((result, index) => (
            <div
              key={index}
              className="p-2 bg-gradient-to-r from-cyan-500/10 to-transparent border-l-2 border-cyan-500 rounded text-xs"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-gray-500 font-mono">{result.timestamp}</span>
                <span className="text-cyan-400">Confidence: {result.confidence.toFixed(1)}%</span>
              </div>
              <div className="text-white font-medium">{result.text}</div>
            </div>
          ))}
        </div>
      </div>

      {/* TTS (Text-to-Speech) */}
      <div className="bg-black/40 border border-purple-500/20 rounded p-3">
        <div className="flex items-center justify-between mb-3">
          <div className="text-xs text-gray-400 font-semibold">TTS OUTPUT QUEUE</div>
          <div className="text-xs text-gray-500">{ttsQueue.length} in queue</div>
        </div>

        <div className="space-y-2">
          {ttsQueue.length === 0 ? (
            <div className="text-center text-gray-600 text-xs italic py-4">
              No TTS output in queue
            </div>
          ) : (
            ttsQueue.map((output, index) => {
              const statusConfig = {
                queued: { color: 'gray', label: 'Queued', icon: '⏳' },
                playing: { color: 'green', label: 'Playing', icon: '🔊' },
                completed: { color: 'blue', label: 'Completed', icon: '✓' }
              }
              const config = statusConfig[output.status]

              return (
                <div
                  key={index}
                  className={`p-2 border-l-2 rounded text-xs ${
                    output.status === 'playing'
                      ? 'bg-gradient-to-r from-green-500/20 to-transparent border-green-500'
                      : 'bg-black/40 border-gray-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-gray-500 font-mono">{output.timestamp}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-xs">{config.icon}</span>
                      <span className={`text-${config.color}-400`}>{config.label}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="text-white font-medium">{output.text}</div>
                    {output.duration && (
                      <span className="text-gray-500 text-xs">{output.duration}</span>
                    )}
                  </div>
                  {output.status === 'playing' && (
                    <div className="mt-2 h-1 bg-black/60 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-green-400"
                        style={{
                          animation: 'progress 3s linear forwards'
                        }}
                      />
                    </div>
                  )}
                </div>
              )
            })
          )}
        </div>

        <style>{`
          @keyframes progress {
            from {
              width: 0%;
            }
            to {
              width: 100%;
            }
          }
        `}</style>
      </div>

      {/* Wake Word Detection */}
      <div className="bg-black/40 border border-yellow-500/20 rounded p-3">
        <div className="text-xs text-gray-400 font-semibold mb-2">WAKE WORD DETECTION</div>
        <div className="flex items-center justify-between p-2 bg-yellow-500/10 border border-yellow-500/30 rounded">
          <div>
            <div className="text-xs text-yellow-400 font-bold">Active</div>
            <div className="text-xs text-gray-500">Listening for wake word...</div>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-500">Keyword</div>
            <div className="text-sm text-yellow-400 font-mono">"친구야"</div>
          </div>
        </div>
      </div>
    </div>
  )
}
