export interface SmileDetection {
  detected: boolean
  confidence: number
  duration: number
  timestamp: string
}

export interface HandGesture {
  type: 'scissors' | 'rock' | 'paper' | 'none'
  confidence: number
}

export interface PersonTracking {
  detected: boolean
  distance: number
  position: { x: number; y: number }
}

export interface InferenceMetrics {
  fps: number
  avgProcessingTime: number
  modelVersion: string
}