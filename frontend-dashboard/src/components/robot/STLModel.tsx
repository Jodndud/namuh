import { useLoader } from '@react-three/fiber'
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js'
// import { Mesh } from 'three'

interface STLModelProps {
  path: string
  position?: [number, number, number]
  rotation?: [number, number, number]
  scale?: number | [number, number, number]
  color?: string
  wireframe?: boolean
  opacity?: number
}

export default function STLModel({
  path,
  position = [0, 0, 0],
  rotation = [0, 0, 0],
  scale = 1,
  color = '#00f0ff',
  wireframe = true,
  opacity = 0.8,
}: STLModelProps) {
  const geometry = useLoader(STLLoader, `/models/${path}`)

  return (
    <mesh
      geometry={geometry}
      position={position}
      rotation={rotation}
      scale={scale}
    >
      <meshBasicMaterial
        color={color}
        wireframe={wireframe}
        transparent={true}
        opacity={opacity}
      />
    </mesh>
  )
}
