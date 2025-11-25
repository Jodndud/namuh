import { createContext, useContext, useState, ReactNode } from 'react'
import type { RobotState } from '../components/robot/stateConfig'

type RobotStateContextType = {
  currentState: RobotState
  setCurrentState: (s: RobotState) => void
}

const RobotStateContext = createContext<RobotStateContextType | undefined>(undefined)

export function RobotStateProvider({ children }: { children: ReactNode }) {
  const [currentState, setCurrentState] = useState<RobotState>('IDLE')
  return (
    <RobotStateContext.Provider value={{ currentState, setCurrentState }}>
      {children}
    </RobotStateContext.Provider>
  )
}

export function useRobotState() {
  const ctx = useContext(RobotStateContext)
  if (!ctx) {
    throw new Error('useRobotState must be used within a RobotStateProvider')
  }
  return ctx
}


