import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, Grid, PerspectiveCamera } from "@react-three/drei";
import { EffectComposer, Bloom } from "@react-three/postprocessing";
import HumanoidRobot from "../robot/HumanoidRobot";
import ViewBox from "../robot/ViewBox";
import { useRobotState } from "../../context/RobotStateContext";

import { JointAngles, BackboneStatus } from "../types/robot";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";

interface Scene3DProps {
  leftArm?: JointAngles;
  rightArm?: JointAngles;
  backbone?: BackboneStatus;
}

function GridFloor() {
  return (
    <Grid
      args={[50, 50]}
      cellSize={1}
      cellThickness={1}
      cellColor="#00f0ff"
      sectionSize={5}
      sectionThickness={1.5}
      sectionColor="gray"
      fadeDistance={50}
      fadeStrength={1}
      followCamera={false}
      infiniteGrid={true}
    />
  );
}

interface CentralObjectProps {
  leftArm?: JointAngles;
  rightArm?: JointAngles;
  backbone?: BackboneStatus;
}

function CentralObject({ leftArm, rightArm, backbone }: CentralObjectProps) {
  const { currentState } = useRobotState();

  return (
    <group>
      {/* 중앙 휴머노이드 로봇 */}
      <HumanoidRobot
        leftArm={leftArm}
        rightArm={rightArm}
        robotState={currentState}
        waistRotationY={backbone?.waistYaw ?? 90}
        neckRotationY={backbone?.neckYaw ?? 90}
        neckRotationX={backbone?.neckPitch ?? 90}
      />
    </group>
  );
}

function CameraAnimator({
  desiredDir,
  controlsRef,
  onDone,
}: {
  desiredDir: [number, number, number] | null;
  controlsRef: React.RefObject<any>;
  onDone?: () => void;
}) {
  const { camera } = useThree();
  const targetVec = useMemo(() => new THREE.Vector3(0, 0, 0), []);
  const destVec = useRef<THREE.Vector3 | null>(null);
  const isAnimatingRef = useRef(false);

  // Recompute destination only when desiredDir changes
  useEffect(() => {
    if (!desiredDir) return;
    const controlsTarget = controlsRef.current?.target as
      | THREE.Vector3
      | undefined;
    if (controlsTarget) {
      targetVec.copy(controlsTarget);
    } else {
      targetVec.set(0, 0, 0);
    }
    const distance = camera.position.distanceTo(targetVec);
    const dir = new THREE.Vector3(
      desiredDir[0],
      desiredDir[1],
      desiredDir[2]
    ).normalize();
    const dest = dir.multiplyScalar(distance).add(targetVec);
    if (!destVec.current) destVec.current = new THREE.Vector3();
    destVec.current.copy(dest);
    isAnimatingRef.current = true;
  }, [desiredDir, camera, controlsRef, targetVec]);

  useFrame(() => {
    if (isAnimatingRef.current && destVec.current) {
      camera.position.lerp(destVec.current, 0.15);
      camera.lookAt(targetVec);
      controlsRef.current?.update?.();
      if (camera.position.distanceTo(destVec.current) < 0.02) {
        destVec.current = null;
        isAnimatingRef.current = false;
        onDone?.();
      }
    }
  });

  return null;
}

export default function Scene3D({ leftArm, rightArm, backbone }: Scene3DProps) {
  const controlsRef = useRef<any>(null);
  const [desiredDir, setDesiredDir] = useState<[number, number, number] | null>(
    null
  );
  const [viewBoxDir, setViewBoxDir] = useState<[number, number, number] | null>(
    null
  );

  const handleViewChange = useCallback((dir: [number, number, number]) => {
    setDesiredDir(dir);
  }, []);

  const snapToDirection = useCallback((dir: [number, number, number]) => {
    if (!controlsRef.current) return;
    const camera = controlsRef.current.object as THREE.PerspectiveCamera;
    const target: THREE.Vector3 =
      controlsRef.current.target ?? new THREE.Vector3(0, 0, 0);
    const distance = camera.position.distanceTo(target);
    const dest = new THREE.Vector3(dir[0], dir[1], dir[2])
      .normalize()
      .multiplyScalar(distance)
      .add(target);
    camera.position.copy(dest);
    camera.lookAt(target);
    controlsRef.current.update();
    setDesiredDir(null);
    // ViewBox에도 최신 방향 반영
    const newDir = new THREE.Vector3()
      .subVectors(camera.position, target)
      .normalize();
    setViewBoxDir([newDir.x, newDir.y, newDir.z]);
  }, []);

  const handleMainControlsChange = useCallback(() => {
    if (!controlsRef.current) return;
    // 사용자가 드래그 중이면 애니메이션 중지
    if (desiredDir) setDesiredDir(null);
    const target: THREE.Vector3 =
      controlsRef.current.target ?? new THREE.Vector3(0, 0, 0);
    // 카메라 방향(타깃 기준)을 정규화해 ViewBox에 전달
    const dir = new THREE.Vector3()
      .subVectors(
        (controlsRef.current.object as THREE.PerspectiveCamera).position,
        target
      )
      .normalize();
    setViewBoxDir([dir.x, dir.y, dir.z]);
  }, [desiredDir]);

  return (
    <div className="relative w-full h-full">
      <Canvas>
        <group position={[0, -4, 0]}>
          <PerspectiveCamera
            makeDefault
            position={[15.23, 12.69, 15.23]}
            fov={45}
          />

          {/* 조명 */}
          <ambientLight intensity={0.2} />
          <pointLight position={[10, 10, 10]} intensity={1} color="#00f0ff" />
          <pointLight
            position={[-10, 5, -10]}
            intensity={0.5}
            color="#8b5cf6"
          />

          {/* 3D 객체들 */}
          <GridFloor />
          <CentralObject
            leftArm={leftArm}
            rightArm={rightArm}
            backbone={backbone}
          />

          {/* 컨트롤 */}
          <OrbitControls
            ref={controlsRef}
            enableDamping
            dampingFactor={0.05}
            minDistance={10}
            maxDistance={35}
            maxPolarAngle={Math.PI / 2}
            mouseButtons={{
              LEFT: THREE.MOUSE.ROTATE,
              MIDDLE: THREE.MOUSE.PAN,
              RIGHT: THREE.MOUSE.PAN,
            }}
            onChange={handleMainControlsChange}
          />

          <CameraAnimator
            desiredDir={desiredDir}
            controlsRef={controlsRef}
            onDone={() => setDesiredDir(null)}
          />

          {/* 포스트 프로세싱 (글로우 효과) */}
          <EffectComposer>
            <Bloom
              intensity={0.5}
              luminanceThreshold={0.2}
              luminanceSmoothing={0.9}
            />
          </EffectComposer>
        </group>
      </Canvas>
      {/* ViewBox 오버레이 (오른쪽 상단 고정) */}
      <div className="absolute top-2 right-2 w-28 h-28 pointer-events-auto">
        <ViewBox
          onSelectView={handleViewChange}
          onOrbitChange={handleViewChange}
          externalDir={viewBoxDir}
          onSelectViewSnap={snapToDirection}
        />
      </div>
    </div>
  );
}
