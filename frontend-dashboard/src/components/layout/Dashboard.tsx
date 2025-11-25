import Scene3D from "../3d/Scene3D";
// import TopPanel from './TopPanel'
import LeftPanel from "./LeftPanel";
import RightPanel from "./RightPanel";
import { useState } from "react";
import { useMqttRobot } from "../../hooks/useMqttRobot";
import { RobotStateProvider } from "../../context/RobotStateContext";
// import RobotDiagram from '../robot/RobotDiagram'
import RobotPOV from "../monitoring/RobotPOV";

export default function Dashboard() {
  const { leftArm, rightArm, backbone } = useMqttRobot();
  const [isRobotInCenter, setIsRobotInCenter] = useState(false);
  const handleToggleSwap = () => setIsRobotInCenter((prev) => !prev);

  return (
    <RobotStateProvider>
      <div className="flex flex-col w-full h-screen bg-black">
        {/* UI 패널들 */}
        {/* <TopPanel /> */}
        <div className="grid grid-cols-4 flex-1 min-h-0">
          <LeftPanel />

          {/* 중앙 콘텐츠 영역 */}
          <div className="col-span-2 p-4 flex min-h-0">
            <div className="flex flex-col flex-1 min-h-0">
              {/* 3D 로봇 모델 / Robot POV (중앙 영역) */}
              <div
                className={`w-full ${
                  isRobotInCenter
                    ? "flex-1 border border-cyan-500/30"
                    : "flex-none"
                } bg-black rounded relative overflow-hidden`}
              >
                {isRobotInCenter ? (
                  <div className="absolute inset-0">
                    <Scene3D
                      leftArm={leftArm}
                      rightArm={rightArm}
                      backbone={backbone}
                    />
                  </div>
                ) : (
                  <RobotPOV fitMode="contain-width" showFrame={false} />
                )}
                {/* 레이블 */}
                {isRobotInCenter && (
                  <div className="absolute top-2 left-2 bg-black/70 px-3 py-1 rounded text-xs text-cyan-400 font-bold z-10">
                    ROBOT STATUS - 3D VIEW
                  </div>
                )}
              </div>
            </div>
          </div>
          <RightPanel
            onToggleSwap={handleToggleSwap}
            isRobotInCenter={isRobotInCenter}
          />
        </div>
      </div>
    </RobotStateProvider>
  );
}

// function DashboardDiagramProxy() {
//   const { currentState } = useRobotState()
//   return <RobotDiagram currentState={currentState} />
// }
