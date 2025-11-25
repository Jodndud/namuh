export interface JointAngles {
  joint0: number;
  joint1: number;
  joint2: number;
  joint3: number;
  joint4: number;
  joint5: number;
  gripper: number;
}

export interface BackboneStatus {
  neckYaw: number;
  neckPitch: number;
  waistYaw: number;
  lastUpdated?: Date;
}

export interface RobotState {
  current: string;
  previous: string;
  timestamp: string;
}

export interface StateTransition {
  from: string;
  to: string;
  timestamp: string;
  duration: string;
}
