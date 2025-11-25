import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Group } from 'three'

// 와이어프레임 컴포넌트
function WireframeMesh({
  geometry,
  position,
  rotation,
  scale,
  color = "#00f0ff"
}: {
  geometry: React.ReactNode
  position?: [number, number, number]
  rotation?: [number, number, number]
  scale?: [number, number, number] | number
  color?: string
}) {
  return (
    <mesh position={position} rotation={rotation} scale={scale}>
      {geometry}
      <meshBasicMaterial
        color={color}
        wireframe={true}
        transparent={true}
        opacity={0.8}
      />
    </mesh>
  )
}

interface RobotArmProps {
  joint0?: number  // base (0-180)
  joint1?: number  // shoulder (0-180)
  joint2?: number  // elbow (0-180)
  joint3?: number  // wrist1 (0-180)
  joint4?: number  // wrist2 (0-180)
  joint5?: number  // wrist3 (0-180)
  gripper?: number // gripper (0-180) 0=closed(일자), 180=open(ㄷ자)
  color?: string   // 와이어프레임 색상
  side?: 'left' | 'right'
}

export default function RobotArm({
  joint0 = 90,
  joint1 = 90,
  joint2 = 90,
  joint3 = 90,
  joint4 = 90,
  // joint5 = 90,
  gripper = 0,
  color = "#00f0ff",
  side = "left",
}: RobotArmProps = {}) {
  const baseRef = useRef<Group>(null)
  const shoulderRef = useRef<Group>(null)
  const elbowRef = useRef<Group>(null)
  const wrist1Ref = useRef<Group>(null)
  const wrist2Ref = useRef<Group>(null)
  const wrist3Ref = useRef<Group>(null)
  const gripperLeftRef = useRef<Group>(null)
  const gripperRightRef = useRef<Group>(null)
  const leftJoint1Ref = useRef<Group>(null)
  const rightJoint1Ref = useRef<Group>(null)

  // 각도를 라디안으로 변환 (0-180도 -> -π/2 ~ π/2)
  const degToRad = (deg: number) => ((deg - 90) * Math.PI) / 180
  
  // 그리퍼 각도 변환 (0-180도 -> 0 ~ π/2 라디안)
  // 0도 = 세로 일직선, 180도 = 가로로 90도씩 벌어짐
  const gripperToRad = (deg: number) => (deg * Math.PI) / 360

  // 각 관절에 각도 적용
  useFrame(() => {
    if (baseRef.current) {
      baseRef.current.rotation.y = degToRad(joint0)
    }
    if (shoulderRef.current) {
      shoulderRef.current.rotation.z = degToRad(joint1)
    }
    if (elbowRef.current) {
      elbowRef.current.rotation.z = degToRad(joint2)
    }
    if (wrist1Ref.current) {
      wrist1Ref.current.rotation.x = degToRad(joint3 + 90)
      // 🔥 왼팔이면 -90, 오른팔이면 +90
      const yOffset = side === "left" ? 90 : 90
      wrist1Ref.current.rotation.y = degToRad(joint3 + yOffset)
      wrist1Ref.current.rotation.z = degToRad(joint3 + 90)
    }
    if (wrist2Ref.current) {
      wrist2Ref.current.rotation.y = degToRad(joint4)
    }
    if (wrist3Ref.current) {
      // wrist3Ref.current.rotation.x = degToRad(joint5)
    }
    // 그리퍼 동작 - 이미지에 맞게 (0도=세로, 180도=가로)
    const baseAngle = gripperToRad(gripper)
    const joint1Angle = baseAngle * 0.5  // 첫 번째 관절은 50%
    
    // 왼쪽 핑거: 반시계방향으로 벌어짐 (180도에서 왼쪽으로)
    if (gripperLeftRef.current) {
      gripperLeftRef.current.rotation.z = -baseAngle
    }
    if (leftJoint1Ref.current) {
      leftJoint1Ref.current.rotation.z = -joint1Angle
    }
    
    // 오른쪽 핑거: 시계방향으로 벌어짐 (180도에서 오른쪽으로)
    if (gripperRightRef.current) {
      gripperRightRef.current.rotation.z = baseAngle
    }
    if (rightJoint1Ref.current) {
      rightJoint1Ref.current.rotation.z = joint1Angle
    }
  })

  return (
    <group position={[0, 0, 0]}>
      {/* Base (J1) */}
      <group ref={baseRef}>
        <WireframeMesh
          geometry={<cylinderGeometry args={[0.4, 0.5, 0.6, 32]} />}
          position={[0, 0.3, 0]}
          color={color}
        />

        {/* Shoulder Link */}
        <group ref={shoulderRef} position={[0, 0.6, 0]}>
          {/* Shoulder Joint (J2) */}
          <WireframeMesh
            geometry={<sphereGeometry args={[0.4, 32, 32]} />}
            color={color}
          />

          {/* Upper Arm */}
          <WireframeMesh
            geometry={<cylinderGeometry args={[0.25, 0.3, 2, 16]} />}
            position={[0, 1, 0]}
            color={color}
          />

          {/* Elbow */}
          <group ref={elbowRef} position={[0, 2, 0]}>
            {/* Elbow Joint (J3) */}
            <WireframeMesh
              geometry={<sphereGeometry args={[0.35, 32, 32]} />}
              color={color}
            />

            {/* Forearm */}
            <WireframeMesh
              geometry={<cylinderGeometry args={[0.2, 0.25, 1.6, 16]} />}
              position={[0, 0.8, 0]}
              color={color}
            />

            {/* Wrist 1 */}
            <group ref={wrist1Ref} position={[0, 1.6, 0]}>
              {/* Wrist Joint 1 (J4) */}
              <WireframeMesh
                geometry={<cylinderGeometry args={[0.25, 0.25, 0.3, 16]} />}
                color={color}
              />

              {/* Wrist Link */}
              <group ref={wrist2Ref} position={[0, 0.3, 0]}>
                <WireframeMesh
                  geometry={<cylinderGeometry args={[0.2, 0.2, 0.4, 16]} />}
                  color={color}
                />

                {/* Wrist 3 / End Effector */}
                <group ref={wrist3Ref} position={[0, 0.4, 0]}>
                  <WireframeMesh
                    geometry={<cylinderGeometry args={[0.15, 0.15, 0.2, 16]} />}
                    color={color}
                  />

                  {/* Tool Base */}
                  <WireframeMesh
                    geometry={<boxGeometry args={[0.3, 0.1, 0.3]} />}
                    position={[0, 0.15, 0]}
                    color={color}
                  />

                  {/* Gripper Mechanism */}
                  <group position={[0, 0.25, 0]}>
                    {/* Left Gripper Finger Assembly */}
                    <group ref={gripperLeftRef} position={[-0.08, 0, 0]}>
                      {/* Base segment */}
                      <WireframeMesh
                        geometry={<boxGeometry args={[0.05, 0.12, 0.08]} />}
                        position={[0, 0.06, 0]}
                        color={color}
                      />

                      {/* Joint 1 */}
                      <group ref={leftJoint1Ref} position={[0, 0.12, 0]}>
                        <WireframeMesh
                          geometry={<cylinderGeometry args={[0.02, 0.02, 0.1, 8]} />}
                          rotation={[Math.PI/2, 0, 0]}
                          color={color}
                        />

                        {/* Extended segment */}
                        <WireframeMesh
                          geometry={<boxGeometry args={[0.04, 0.15, 0.06]} />}
                          position={[0, 0.075, 0]}
                          color={color}
                        />

                        {/* Finger tip */}
                        <WireframeMesh
                          geometry={<boxGeometry args={[0.04, 0.08, 0.06]} />}
                          position={[0, 0.15, 0]}
                          color={color}
                        />
                      </group>
                    </group>

                    {/* Right Gripper Finger Assembly */}
                    <group ref={gripperRightRef} position={[0.08, 0, 0]}>
                      {/* Base segment */}
                      <WireframeMesh
                        geometry={<boxGeometry args={[0.05, 0.12, 0.08]} />}
                        position={[0, 0.06, 0]}
                        color={color}
                      />

                      {/* Joint 1 */}
                      <group ref={rightJoint1Ref} position={[0, 0.12, 0]}>
                        <WireframeMesh
                          geometry={<cylinderGeometry args={[0.02, 0.02, 0.1, 8]} />}
                          rotation={[Math.PI/2, 0, 0]}
                          color={color}
                        />

                        {/* Extended segment */}
                        <WireframeMesh
                          geometry={<boxGeometry args={[0.04, 0.15, 0.06]} />}
                          position={[0, 0.075, 0]}
                          color={color}
                        />

                        {/* Finger tip */}
                        <WireframeMesh
                          geometry={<boxGeometry args={[0.04, 0.08, 0.06]} />}
                          position={[0, 0.15, 0]}
                          color={color}
                        />
                      </group>
                    </group>
                  </group>
                </group>
              </group>
            </group>
          </group>
        </group>
      </group>
    </group>
  )
}
