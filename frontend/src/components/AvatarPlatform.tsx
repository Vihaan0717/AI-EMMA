import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

interface AvatarPlatformProps {
  accentColor?: string;
  radius?: number;
  position?: [number, number, number];
}

export const AvatarPlatform = ({
  accentColor = "#22d3ee",
  radius = 1.35,
  position = [0, 0, 0],
}: AvatarPlatformProps) => {
  const outerRingRef = useRef<THREE.Group>(null);
  const midRingRef = useRef<THREE.Group>(null);
  const pulseDiscRef = useRef<THREE.Mesh>(null);

  useFrame((_, delta) => {
    // Smooth sci-fi counter-rotations
    if (outerRingRef.current) {
      outerRingRef.current.rotation.y += delta * 0.18;
    }
    if (midRingRef.current) {
      midRingRef.current.rotation.y -= delta * 0.28;
    }
    if (pulseDiscRef.current) {
      const mat = pulseDiscRef.current.material as THREE.MeshBasicMaterial;
      if (mat) {
        mat.opacity = 0.12 + Math.sin(Date.now() * 0.002) * 0.04;
      }
    }
  });

  return (
    <group position={position}>
      {/* 1. Main Solid Grounding Dais (Catches foot contacts and shadows) */}
      <mesh position={[0, -0.015, 0]} receiveShadow>
        <cylinderGeometry args={[radius * 1.05, radius * 1.12, 0.03, 64]} />
        <meshStandardMaterial
          color="#060913"
          roughness={0.35}
          metalness={0.85}
        />
      </mesh>

      {/* 2. Platform Upper Carbon-Glass Surface */}
      <mesh position={[0, 0.001, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[radius, 64]} />
        <meshStandardMaterial
          color="#080e1c"
          roughness={0.2}
          metalness={0.9}
        />
      </mesh>

      {/* 3. Soft Holographic Glowing Floor Disc */}
      <mesh
        ref={pulseDiscRef}
        position={[0, 0.003, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
      >
        <circleGeometry args={[radius * 0.95, 64]} />
        <meshBasicMaterial
          color={accentColor}
          transparent
          opacity={0.14}
          depthWrite={false}
        />
      </mesh>

      {/* 4. Outer Rotating Energy Ring with Tech Segments */}
      <group ref={outerRingRef} position={[0, 0.006, 0]}>
        <mesh rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[radius * 0.98, radius * 1.02, 64]} />
          <meshBasicMaterial
            color={accentColor}
            transparent
            opacity={0.85}
            side={THREE.DoubleSide}
          />
        </mesh>

        {/* 12 Radial Ticks */}
        {Array.from({ length: 12 }).map((_, i) => {
          const angle = (i / 12) * Math.PI * 2;
          return (
            <mesh
              key={i}
              position={[
                Math.cos(angle) * (radius * 1.06),
                0,
                Math.sin(angle) * (radius * 1.06),
              ]}
              rotation={[0, -angle, 0]}
            >
              <boxGeometry args={[0.07, 0.005, 0.012]} />
              <meshBasicMaterial color={accentColor} transparent opacity={0.9} />
            </mesh>
          );
        })}
      </group>

      {/* 5. Middle Segmented Counter-Rotating Grid Ring */}
      <group ref={midRingRef} position={[0, 0.008, 0]}>
        <mesh rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[radius * 0.65, radius * 0.67, 48]} />
          <meshBasicMaterial
            color={accentColor}
            transparent
            opacity={0.5}
            side={THREE.DoubleSide}
          />
        </mesh>

        {/* 8 Tech Node Markers */}
        {Array.from({ length: 8 }).map((_, i) => {
          const angle = (i / 8) * Math.PI * 2;
          return (
            <mesh
              key={i}
              position={[
                Math.cos(angle) * (radius * 0.66),
                0,
                Math.sin(angle) * (radius * 0.66),
              ]}
            >
              <cylinderGeometry args={[0.018, 0.018, 0.008, 16]} />
              <meshBasicMaterial color="#ffffff" transparent opacity={0.85} />
            </mesh>
          );
        })}
      </group>

      {/* 6. Inner Focus Ring Under Footsteps */}
      <mesh position={[0, 0.01, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[radius * 0.32, radius * 0.34, 32]} />
        <meshBasicMaterial
          color={accentColor}
          transparent
          opacity={0.4}
          side={THREE.DoubleSide}
        />
      </mesh>

      {/* 7. Subtle Standing Base Shadow Catcher */}
      <mesh position={[0, 0.002, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[radius * 0.55, 32]} />
        <meshBasicMaterial
          color="#000000"
          transparent
          opacity={0.35}
          depthWrite={false}
        />
      </mesh>
    </group>
  );
};
