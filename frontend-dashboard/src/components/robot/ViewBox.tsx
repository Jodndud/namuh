import { Canvas, useThree, useFrame } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, Text } from '@react-three/drei'
import { useRef, useCallback, useEffect, useMemo, useState } from 'react'
import * as THREE from 'three'

interface ViewBoxProps {
  onSelectView?: (dir: [number, number, number]) => void
  onOrbitChange?: (dir: [number, number, number]) => void
  externalDir?: [number, number, number] | null
  onSelectViewSnap?: (dir: [number, number, number]) => void
}

function ControlsSync({
  controlsRef,
  onOrbitChange,
  onUserInteract,
  fixedDistance,
}: {
  controlsRef: React.RefObject<any>
  onOrbitChange?: (dir: [number, number, number]) => void
  onUserInteract?: () => void
  fixedDistance: number
}) {
  const { camera } = useThree()
  const lastDir = useRef<THREE.Vector3 | null>(null)

  const handleChange = useCallback(() => {
    onUserInteract?.()
    const dir = (camera as THREE.PerspectiveCamera).position.clone().normalize()
    // 거리 고정
    ;(camera as THREE.PerspectiveCamera).position.copy(dir.clone().multiplyScalar(fixedDistance))
    if (!lastDir.current || lastDir.current.angleTo(dir) > 0.02) {
      lastDir.current = dir.clone()
      onOrbitChange?.([dir.x, dir.y, dir.z])
    }
  }, [camera, onOrbitChange, fixedDistance, onUserInteract])

  return (
    <OrbitControls
      ref={controlsRef}
      enablePan={false}
      enableZoom={false}
      mouseButtons={{
        LEFT: THREE.MOUSE.ROTATE,
        MIDDLE: THREE.MOUSE.PAN,
        RIGHT: THREE.MOUSE.ROTATE,
      }}
      onChange={handleChange}
    />
  )
}

function ViewBoxAnimator({
  desiredDir,
  controlsRef,
  onDone,
  fixedDistance,
}: {
  desiredDir: [number, number, number] | null
  controlsRef: React.RefObject<any>
  onDone?: () => void
  fixedDistance: number
}) {
  const { camera } = useThree()
  const destVec = useRef<THREE.Vector3 | null>(null)
  const isAnimatingRef = useRef(false)

  useEffect(() => {
    if (!desiredDir) return
    const dir = new THREE.Vector3(desiredDir[0], desiredDir[1], desiredDir[2]).normalize()
    const dest = dir.multiplyScalar(fixedDistance)
    if (!destVec.current) destVec.current = new THREE.Vector3()
    destVec.current.copy(dest)
    isAnimatingRef.current = true
  }, [desiredDir, camera, controlsRef, fixedDistance])

  useFrame(() => {
    if (isAnimatingRef.current && destVec.current) {
      camera.position.lerp(destVec.current, 0.15)
      camera.lookAt(0, 0, 0)
      // 거리 고정
      const dirNow = (camera as THREE.PerspectiveCamera).position.clone().normalize()
      ;(camera as THREE.PerspectiveCamera).position.copy(dirNow.multiplyScalar(fixedDistance))
      controlsRef.current?.update?.()
      if (camera.position.distanceTo(destVec.current) < 0.01) {
        destVec.current = null
        isAnimatingRef.current = false
        onDone?.()
      }
    }
  })

  return null
}

export default function ViewBox({ onOrbitChange, externalDir, onSelectViewSnap }: ViewBoxProps) {
  const controlsRef = useRef<any>(null)
  const [desiredDir, setDesiredDir] = useState<[number, number, number] | null>(null)
  const initialDistanceRef = useRef<number | null>(null)
  const [hoveredFace, setHoveredFace] = useState<number | null>(null)
  const [activeFace, setActiveFace] = useState<number | null>(null)

  // 초기 카메라 거리 고정값 저장
  useEffect(() => {
    if (initialDistanceRef.current !== null) return
    // wait a tick for camera to mount
    requestAnimationFrame(() => {
      try {
        const cam = (controlsRef.current?.object ?? null) as THREE.PerspectiveCamera | null
        if (cam) {
          initialDistanceRef.current = cam.position.length()
        } else {
          initialDistanceRef.current = Math.sqrt(2.5 * 2.5 + 2.5 * 2.5 + 2.5 * 2.5)
        }
      } catch {
        initialDistanceRef.current = Math.sqrt(2.5 * 2.5 + 2.5 * 2.5 + 2.5 * 2.5)
      }
    })
  }, [])

  // 외부에서 전달된 방향(externalDir)이 바뀌면 ViewBox도 그 방향으로 회전
  useEffect(() => {
    if (!externalDir) return
    setDesiredDir(externalDir)
  }, [externalDir])

  const handleFaceClick = useCallback(
    (e: any) => {
      e.stopPropagation()
      const faceNormal = e.face?.normal as THREE.Vector3 | undefined
      if (!faceNormal) return
      const worldNormal = faceNormal.clone().transformDirection(e.object.matrixWorld).normalize()
      const dirTuple: [number, number, number] = [worldNormal.x, worldNormal.y, worldNormal.z]
      // ViewBox 자체 즉시 스냅
      const dist = initialDistanceRef.current ?? Math.sqrt(2.5 * 2.5 + 2.5 * 2.5 + 2.5 * 2.5)
      try {
        const cam = (controlsRef.current?.object ?? null) as THREE.PerspectiveCamera | null
        if (cam) {
          const v = new THREE.Vector3(dirTuple[0], dirTuple[1], dirTuple[2]).normalize().multiplyScalar(dist)
          cam.position.copy(v)
          cam.lookAt(0, 0, 0)
          controlsRef.current?.update?.()
        }
      } catch {}
      setDesiredDir(null)
      // 메인 Scene도 즉시 스냅
      onSelectViewSnap?.(dirTuple)
    },
    [onSelectViewSnap]
  )

  const handleLabelClick = useCallback(
    (dir: [number, number, number]) => {
      // ViewBox 자체 즉시 스냅
      const dist = initialDistanceRef.current ?? Math.sqrt(2.5 * 2.5 + 2.5 * 2.5 + 2.5 * 2.5)
      try {
        const cam = (controlsRef.current?.object ?? null) as THREE.PerspectiveCamera | null
        if (cam) {
          const v = new THREE.Vector3(dir[0], dir[1], dir[2]).normalize().multiplyScalar(dist)
          cam.position.copy(v)
          cam.lookAt(0, 0, 0)
          controlsRef.current?.update?.()
        }
      } catch {}
      setDesiredDir(null)
      // 메인 Scene도 즉시 스냅
      onSelectViewSnap?.(dir)
    },
    [onSelectViewSnap]
  )

  const labels = useMemo(
    () =>
      [
        { name: 'Front', dir: [0, 0, 1] as [number, number, number], pos: [0, 0, 0.51], rot: [0, 0, 0] },
        { name: 'Back', dir: [0, 0, -1] as [number, number, number], pos: [0, 0, -0.51], rot: [0, Math.PI, 0] },
        { name: 'Right', dir: [1, 0, 0] as [number, number, number], pos: [0.51, 0, 0], rot: [0, -Math.PI / 2, 0] },
        { name: 'Left', dir: [-1, 0, 0] as [number, number, number], pos: [-0.51, 0, 0], rot: [0, Math.PI / 2, 0] },
        { name: 'Top', dir: [0, 1, 0] as [number, number, number], pos: [0, 0.51, 0], rot: [-Math.PI / 2, 0, 0] },
        { name: 'Bottom', dir: [0, -1, 0] as [number, number, number], pos: [0, -0.51, 0], rot: [Math.PI / 2, 0, 0] },
      ] as Array<{ name: string; dir: [number, number, number]; pos: [number, number, number]; rot: [number, number, number] }>,
    []
  )

  return (
    <div
      className="w-full h-full"
      onWheel={(e) => {
        // ViewBox는 스크롤/휠로 확대 금지, 이벤트 버블 방지
        e.preventDefault()
        e.stopPropagation()
      }}
    >
      <Canvas>
        <PerspectiveCamera makeDefault position={[2.5, 2.5, 2.5]} fov={35} />
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 5, 5]} intensity={0.8} />

        <mesh onPointerDown={handleFaceClick}>
          <boxGeometry args={[1, 1, 1]} />
          <meshStandardMaterial color="#9ca3af" />
        </mesh>

        {labels.map((f, idx) => (
          <group key={`${f.name}-bg`}>
            <mesh
              position={(f.pos as any).map((v: number) => (Math.sign(v) !== 0 ? v * 0.998 : v)) as any}
              rotation={f.rot as any}
              renderOrder={0}
              onPointerOver={(e) => {
                e.stopPropagation()
                setHoveredFace(idx)
              }}
              onPointerOut={(e) => {
                e.stopPropagation()
                setHoveredFace((prev) => (prev === idx ? null : prev))
                // hover가 풀릴 때 active도 함께 해제하지는 않음
              }}
              onPointerDown={(e) => {
                e.stopPropagation()
                setActiveFace(idx)
                // 면 클릭 시 메인 Scene 스냅
                handleLabelClick(f.dir)
              }}
              onPointerUp={(e) => {
                e.stopPropagation()
                setActiveFace((prev) => (prev === idx ? null : prev))
              }}
            >
              <planeGeometry args={[0.98, 0.98]} />
              <meshStandardMaterial
                color={activeFace === idx || hoveredFace === idx ? '#ffffff' : '#ffffff'}
                transparent
                opacity={activeFace === idx || hoveredFace === idx ? 1 : 0}
                side={THREE.DoubleSide}
                depthWrite={false}
              />
            </mesh>
          </group>
        ))}

        {labels.map((f, idx) => (
          <Text
            key={`${f.name}-label`}
            position={f.pos as any}
            rotation={f.rot as any}
            fontSize={0.18}
            color={activeFace === idx || hoveredFace === idx ? '#000000' : '#ffffff'}
            renderOrder={1}
            anchorX="center"
            anchorY="middle"
            onPointerDown={(e) => {
              e.stopPropagation()
              handleLabelClick(f.dir)
            }}
            onPointerOver={(e) => {
              e.stopPropagation()
              setHoveredFace(idx)
            }}
            onPointerOut={(e) => {
              e.stopPropagation()
              setHoveredFace((prev) => (prev === idx ? null : prev))
            }}
            onPointerUp={(e) => {
              e.stopPropagation()
              setActiveFace((prev) => (prev === idx ? null : prev))
            }}
            // 텍스트가 클릭 타겟이 되도록 유지 (상위로 이벤트만 전달)
          >
            {f.name}
          </Text>
        ))}

        <ControlsSync
          controlsRef={controlsRef}
          onOrbitChange={onOrbitChange}
          onUserInteract={() => setDesiredDir(null)}
          fixedDistance={initialDistanceRef.current ?? Math.sqrt(2.5 * 2.5 + 2.5 * 2.5 + 2.5 * 2.5)}
        />
        <ViewBoxAnimator
          desiredDir={desiredDir}
          controlsRef={controlsRef}
          onDone={() => setDesiredDir(null)}
          fixedDistance={initialDistanceRef.current ?? Math.sqrt(2.5 * 2.5 + 2.5 * 2.5 + 2.5 * 2.5)}
        />
      </Canvas>
    </div>
  )
}