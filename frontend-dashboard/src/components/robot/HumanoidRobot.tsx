import { useRef, Suspense } from "react";
import { useFrame } from "@react-three/fiber";
import { Group } from "three";
import RobotArm from "./RobotArm";
import STLModel from "./STLModel";
import { JointAngles } from "../types/robot";

// Degree to Radian 변환 헬퍼
const degToRad = (degrees: number) => degrees * (Math.PI / 180);

interface HumanoidRobotProps {
  leftArm?: JointAngles;
  rightArm?: JointAngles;
  waistRotationY?: number;
  waistRotationX?: number;
  neckRotationY?: number;
  neckRotationX?: number;
  robotState?: string;
}

export default function HumanoidRobot({
  leftArm = {
    joint0: 90,
    joint1: 90,
    joint2: 90,
    joint3: 90,
    joint4: 90,
    joint5: 90,
    gripper: 0,
  },
  rightArm = {
    joint0: 90,
    joint1: 90,
    joint2: 90,
    joint3: 90,
    joint4: 90,
    joint5: 90,
    gripper: 0,
  },
  waistRotationY,
  waistRotationX = 0,
  neckRotationY,
  neckRotationX,
}: HumanoidRobotProps = {}) {
  const headRef = useRef<Group>(null);
  const torsoRef = useRef<Group>(null);

  const waistYRad = degToRad((waistRotationY ?? 90) - 90) * 0.5;
  const neckYRad = degToRad((neckRotationY ?? 90) - 90) * 0.5;
  const neckXRad = degToRad((neckRotationX ?? 90) - 90) * 0.5;

  const adjustedLeftArm: JointAngles = {
    ...leftArm,
    joint3: -leftArm.joint3,
    joint4: -leftArm.joint4,
  };

  const adjustedRightArm: JointAngles = {
    ...rightArm,
    joint3: -rightArm.joint3,
    joint0: 180 - rightArm.joint0,
  };
  // 디버깅용 로그
  // console.log('Robot State:', robotState)
  // console.log('Original rightArm:', rightArm)
  // console.log('Adjusted rightArm:', adjustedRightArm)

  // 부드러운 호흡 애니메이션
  useFrame((state) => {
    const t = state.clock.getElapsedTime();

    if (headRef.current) {
      // 머리 좌우 회전
      // headRef.current.rotation.y = Math.sin(t * 0.3) * 0.2;
    }

    if (torsoRef.current) {
      // 몸통 호흡 효과
      torsoRef.current.scale.y = 1 + Math.sin(t * 0.5) * 0.02;
    }
  });

  // 네온 시안 와이어프레임 머티리얼
  const neonMaterial = {
    color: "#00f0ff",
    wireframe: true,
    transparent: true,
    opacity: 0.8,
  };

  // 네온 옐로우 와이어프레임 머티리얼
  const neonYellowMaterial = {
    color: "#ffff00",
    wireframe: true,
    transparent: true,
    opacity: 0.8,
  };

  return (
    <group
      position={[0, 0, 0]}
      scale={[1.5, 1.5, 1.5]}
      rotation={[0, Math.PI, 0]}
    >
      {/* 베이스 플랫폼 - 네온 */}
      <mesh position={[0, 0.2, 0]}>
        <cylinderGeometry args={[1.2, 1.4, 0.3, 32]} />
        <meshBasicMaterial {...neonMaterial} />
      </mesh>

      {/* 하체 연결부 - 네온 */}
      <mesh position={[0, 0.7, 0]}>
        <cylinderGeometry args={[0.5, 0.7, 1, 16]} />
        <meshBasicMaterial {...neonMaterial} />
      </mesh>

      {/* 골반/복부 - 네온 */}
      <mesh position={[0, 1.7, 0]}>
        <boxGeometry args={[1.4, 1, 0.8]} />
        <meshBasicMaterial {...neonMaterial} />
      </mesh>

      {/* ========== 허리 관절 시스템 ========== */}
      <group position={[0, 2.3, 0]}>
        {/* 허리 아래쪽 - Y축 좌우 회전 - 옐로우 */}
        <group rotation={[0, waistYRad, 0]}>
          <mesh>
            <cylinderGeometry args={[0.4, 0.45, 0.3, 16]} />
            <meshBasicMaterial {...neonYellowMaterial} />
          </mesh>

          {/* 허리 위쪽 - X축 앞뒤 끄덕 - 옐로우 */}
          <group position={[0, 0.2, 0]} rotation={[waistRotationX, 0, 0]}>
            <mesh>
              <cylinderGeometry args={[0.35, 0.4, 0.3, 16]} />
              <meshBasicMaterial {...neonYellowMaterial} />
            </mesh>

            {/* ========== 상체 (가슴) ========== */}
            <group
              ref={torsoRef}
              position={[-0.25, 1.5, 0.6]}
              rotation={[Math.PI / -2, 0, 0]}
            >
              <Suspense fallback={null}>
                {/* 상체 내부 척추 */}
                {/* <STLModel path="torso_spine.stl" position={[0, 0.4, 0]} scale={0.01} /> */}

                {/* 상체 커버 - 앞면/뒷면 */}
                <STLModel
                  path="torso_front.stl"
                  position={[0, 0.4, 2]}
                  scale={0.01}
                />
                <STLModel
                  path="torso_back.stl"
                  position={[0, 0.4, 2]}
                  scale={0.01}
                />

                {/* 어깨 커버 - 네온 그린 */}
                <STLModel
                  path="shoulder_left.stl"
                  position={[0, 0.4, 2]}
                  scale={0.01}
                  color="#00f0ff"
                />
                <STLModel
                  path="shoulder_right.stl"
                  position={[0, 0.4, 2]}
                  scale={0.01}
                  color="#00f0ff"
                />
              </Suspense>

              {/* 왼팔 */}
              <group position={[-0.4, 0.4, 0.3]}>
                <group rotation={[0, 0, Math.PI / 2]} scale={[0.8, 0.8, 0.8]}>
                  <RobotArm {...adjustedLeftArm} side="left" color="#00f0ff" />
                </group>
              </group>

              {/* 오른팔 */}
              <group position={[1, 0.5, 0.3]}>
                <group rotation={[0, 0, -Math.PI / 2]} scale={[-0.8, 0.8, 0.8]}>
                  <RobotArm
                    {...adjustedRightArm}
                    side="right"
                    color="#00f0ff"
                  />
                </group>
              </group>

              {/* ========== 목 관절 시스템 (STL) ========== */}
              <group position={[0, 1.2, 0]}>
                <Suspense fallback={null}>
                  {/* 목 좌우 회전 그룹 - 옐로우 (회전 중심점을 목 위치로 이동) */}
                  <group position={[0, -0.9, 2]} rotation={[0, 0, neckYRad]}>
                    {/* 목 아래쪽 */}
                    <STLModel
                      path="neck_lower.stl"
                      position={[0, 0.15, 0]}
                      scale={0.01}
                      color="#ffff00"
                    />
                    {/* 목 위쪽 */}
                    <STLModel
                      path="neck_upper.stl"
                      position={[0, 0.15, 0]}
                      scale={0.01}
                      color="#ffff00"
                    />

                    {/* 머리 끄덕 회전 그룹 (새로운 중심점에 맞게 상대 위치 조정) */}
                    <group position={[0, 0.2, -2]} rotation={[neckXRad, 0, 0]}>
                      {/* 머리만 끄덕 */}
                      <group ref={headRef} position={[0, -0.3, 1.75]}>
                        <STLModel
                          path="head_jaw.stl"
                          position={[0, 0.2, 0]}
                          scale={0.01}
                          color="#ffff00"
                        />
                        <STLModel
                          path="head_connector.stl"
                          position={[0, 0.2, 0]}
                          scale={0.01}
                        />
                        <STLModel
                          path="head_top.stl"
                          position={[0, 0.2, 0]}
                          scale={0.01}
                        />
                      </group>
                    </group>
                  </group>
                </Suspense>
              </group>
            </group>
          </group>
        </group>
      </group>
    </group>
  );
}
