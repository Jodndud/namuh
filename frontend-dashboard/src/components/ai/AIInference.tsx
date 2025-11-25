import { useState, useEffect } from 'react'
import { SmileDetection, HandGesture, PersonTracking, InferenceMetrics } from '../types/ai'

export default function AIInference() {
  const [smileDetection, setSmileDetection] = useState<SmileDetection>({
    detected: false,
    confidence: 0,
    duration: 0,
    timestamp: ''
  })

  const [handGesture, setHandGesture] = useState<HandGesture>({
    type: 'none',
    confidence: 0
  })

  const [personTracking, setPersonTracking] = useState<PersonTracking>({
    detected: true,
    distance: 1.5,
    position: { x: 0, y: 0 }
  })

  const [metrics, setMetrics] = useState<InferenceMetrics>({
    fps: 30,
    avgProcessingTime: 33.5,
    modelVersion: 'v2.1.0'
  })

  // 시뮬레이션: AI 추론 결과 업데이트
  useEffect(() => {
    const interval = setInterval(() => {
      // Smile Detection
      const isSmiling = Math.random() > 0.7
      if (isSmiling) {
        setSmileDetection({
          detected: true,
          confidence: 85 + Math.random() * 15,
          duration: 1 + Math.random() * 3,
          timestamp: new Date().toLocaleTimeString()
        })
        setTimeout(() => {
          setSmileDetection(prev => ({ ...prev, detected: false }))
        }, 2000)
      }

      // Hand Gesture
      const gestures: HandGesture['type'][] = ['scissors', 'rock', 'paper', 'none']
      const randomGesture = gestures[Math.floor(Math.random() * gestures.length)]
      setHandGesture({
        type: randomGesture,
        confidence: randomGesture === 'none' ? 0 : 80 + Math.random() * 20
      })

      // Person Tracking
      setPersonTracking({
        detected: Math.random() > 0.1,
        distance: 1.0 + Math.random() * 2,
        position: {
          x: -0.5 + Math.random(),
          y: -0.3 + Math.random() * 0.6
        }
      })

      // Metrics
      setMetrics({
        fps: 28 + Math.random() * 4,
        avgProcessingTime: 30 + Math.random() * 10,
        modelVersion: 'v2.1.0'
      })
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  const gestureLabel = {
    scissors: 'SCISSORS',
    rock: 'ROCK',
    paper: 'PAPER',
    none: 'NONE'
  }

  return (
    <div className="space-y-3">
      {/* Smile Detection */}
      <div className={`p-3 border rounded transition-all ${
        smileDetection.detected
          ? 'bg-gradient-to-br from-pink-500/30 to-purple-500/20 border-pink-500/50'
          : 'bg-black/40 border-cyan-500/20'
      }`}>
        <div className="flex items-center justify-between mb-2">
          <div className="text-xs text-gray-400 font-semibold">SMILE DETECTION</div>
          <div className={`text-xs px-2 py-1 rounded ${
            smileDetection.detected
              ? 'bg-pink-500/30 text-pink-400'
              : 'bg-gray-500/20 text-gray-500'
          }`}>
            {smileDetection.detected ? 'DETECTED' : 'IDLE'}
          </div>
        </div>

        {smileDetection.detected && (
          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-gray-400">Confidence:</span>
              <span className="text-pink-400 font-bold">{smileDetection.confidence.toFixed(1)}%</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-gray-400">Duration:</span>
              <span className="text-purple-400">{smileDetection.duration.toFixed(1)}s</span>
            </div>
            <div className="h-2 bg-black/60 rounded-full overflow-hidden">
              <div
                className="h-full bg-pink-400"
                style={{ width: `${smileDetection.confidence}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Hand Gesture Recognition */}
      <div className={`p-3 border rounded ${
        handGesture.type !== 'none'
          ? 'bg-gradient-to-br from-blue-500/20 to-cyan-500/10 border-blue-500/50'
          : 'bg-black/40 border-cyan-500/20'
      }`}>
        <div className="flex items-center justify-between mb-2">
          <div className="text-xs text-gray-400 font-semibold">HAND GESTURE</div>
          <div className={`text-xs px-2 py-1 rounded ${
            handGesture.type !== 'none'
              ? 'bg-blue-500/30 text-blue-400'
              : 'bg-gray-500/20 text-gray-500'
          }`}>
            {gestureLabel[handGesture.type]}
          </div>
        </div>

        {handGesture.type !== 'none' && (
          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-gray-400">Confidence:</span>
              <span className="text-blue-400 font-bold">{handGesture.confidence.toFixed(1)}%</span>
            </div>
            <div className="h-2 bg-black/60 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-400"
                style={{ width: `${handGesture.confidence}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Person Tracking */}
      <div className={`p-3 border rounded ${
        personTracking.detected
          ? 'bg-gradient-to-br from-green-500/20 to-teal-500/10 border-green-500/50'
          : 'bg-gradient-to-br from-red-500/20 to-orange-500/10 border-red-500/50'
      }`}>
        <div className="flex items-center justify-between mb-2">
          <div className="text-xs text-gray-400 font-semibold">PERSON TRACKING</div>
          <div className={`text-xs px-2 py-1 rounded ${
            personTracking.detected
              ? 'bg-green-500/30 text-green-400'
              : 'bg-red-500/30 text-red-400'
          }`}>
            {personTracking.detected ? 'TRACKING' : 'LOST'}
          </div>
        </div>

        {personTracking.detected && (
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-gray-400">Distance:</span>
              <span className="text-green-400 font-bold">{personTracking.distance.toFixed(2)}m</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-gray-400">Position:</span>
              <span className="text-teal-400 font-mono">
                ({personTracking.position.x.toFixed(2)}, {personTracking.position.y.toFixed(2)})
              </span>
            </div>

            {/* Visual Position Indicator */}
            <div className="relative h-16 bg-black/60 rounded border border-green-500/30">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-xs text-gray-600">Robot View</div>
              </div>
              <div
                className="absolute w-3 h-3 rounded-full bg-green-400 shadow-lg shadow-green-400/50 transition-all"
                style={{
                  left: `${50 + personTracking.position.x * 40}%`,
                  top: `${50 + personTracking.position.y * 80}%`,
                  transform: 'translate(-50%, -50%)'
                }}
              >
                <div className="absolute inset-0 rounded-full bg-green-400 animate-ping opacity-75" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Inference Metrics */}
      <div className="p-3 bg-black/40 border border-cyan-500/20 rounded">
        <div className="text-xs text-gray-400 font-semibold mb-2">INFERENCE METRICS</div>
        <div className="grid grid-cols-2 gap-2">
          <div className="p-2 bg-black/40 border border-cyan-500/10 rounded">
            <div className="text-xs text-gray-500">FPS</div>
            <div className="text-lg font-bold text-cyan-400">{metrics.fps.toFixed(1)}</div>
          </div>
          <div className="p-2 bg-black/40 border border-cyan-500/10 rounded">
            <div className="text-xs text-gray-500">Proc. Time</div>
            <div className="text-lg font-bold text-purple-400">{metrics.avgProcessingTime.toFixed(1)}ms</div>
          </div>
        </div>
        <div className="mt-2 text-xs text-gray-500 text-center">
          Model: <span className="text-cyan-400 font-mono">{metrics.modelVersion}</span>
        </div>
      </div>
    </div>
  )
}
