import { useRef, useEffect, useCallback, useState, memo } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, Environment, ContactShadows } from "@react-three/drei";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { VRM, VRMLoaderPlugin, VRMUtils } from "@pixiv/three-vrm";
import { VRMAnimationManager } from "@/animation/VRMAnimationManager";
import { AvatarPlatform } from "@/components/AvatarPlatform";
import type { AvatarFeatures } from "@/lib/avatar";

interface ModelProps {
  url: string;
  state: string;
  tracking?: { headPitch: number; headYaw: number; eyePitch: number; eyeYaw: number; blinkLeft?: number; blinkRight?: number };
  audioAmplitude?: number;
  gesture?: string;
  emotion?: string;
  emotionWeight?: number;
  features: AvatarFeatures;
  handPose?: { left?: string; right?: string };
  fingerCurls?: { left?: Record<string, number>; right?: Record<string, number> };
  onLoaded: (manager: VRMAnimationManager) => void;
}

const VRMModel = memo(({ url, state, tracking, audioAmplitude, gesture, emotion, emotionWeight, features, handPose, fingerCurls, onLoaded }: ModelProps) => {
  const [vrm, setVrm] = useState<VRM | null>(null);
  const managerRef = useRef(new VRMAnimationManager());
  const prevStateRef = useRef(state);

  const handleLookAt = useCallback((headY: number, headP: number, eyeY: number, eyeP: number) => {
    if (managerRef.current.isAttached) {
      managerRef.current.setLookAt(headY, headP, eyeY, eyeP);
    }
  }, []);

  // Integrate face tracking directly from props (backend data)
  useEffect(() => {
    if (tracking) {
      if (tracking.headYaw !== undefined && tracking.headPitch !== undefined) {
        handleLookAt(tracking.headYaw, tracking.headPitch, tracking.eyeYaw ?? 0, tracking.eyePitch ?? 0);
      }
      
      if (managerRef.current.isAttached) {
        managerRef.current.setBlinkExact(tracking.blinkLeft, tracking.blinkRight);
      }
    } else if (managerRef.current.isAttached) {
      // Clear exact blinks to fallback to random idle blinks
      managerRef.current.setBlinkExact(undefined, undefined);
    }
  }, [tracking, handleLookAt]);

  useEffect(() => {
    const loader = new GLTFLoader();
    loader.register((parser) => new VRMLoaderPlugin(parser));

    loader.loadAsync(url).then((gltf) => {
      const loadedVrm = gltf.userData.vrm;
      if (!loadedVrm) return;

      // VRoid-exported models already face the default R3F camera. Keeping their
      // authored orientation exposes the face, eyes, and expressions to the user.
      VRMUtils.rotateVRM0(loadedVrm);
      setVrm(loadedVrm);
      
      managerRef.current.attach(loadedVrm);
      (window as any).__vrm = loadedVrm;
      (window as any).__vrmManager = managerRef.current;
      
      // Map state to initial emotion/pose (respecting explicit gesture and emotion props)
      const stateAnim = mapStateToAnimation(state);
      managerRef.current.setEmotion((emotion || stateAnim.emotion) as any);
      managerRef.current.playAction((gesture || stateAnim.pose) as any);

      onLoaded(managerRef.current);
    });
  }, [url]);

  // Handle state changes
  useEffect(() => {
    if (prevStateRef.current !== state && managerRef.current.isAttached) {
      const { emotion, pose } = mapStateToAnimation(state);
      managerRef.current.setEmotion(emotion as any);
      managerRef.current.playAction(pose as any);
      prevStateRef.current = state;
    }
  }, [state]);

  useEffect(() => {
    managerRef.current.setFeatures(features);
  }, [features]);

  // Handle gesture changes from backend AI_RESPONSE / BODY_CONTROL
  useEffect(() => {
    if (gesture && managerRef.current.isAttached) {
      managerRef.current.playAction(gesture);
    }
  }, [gesture]);

  // Handle emotion changes from backend AI_RESPONSE / BODY_CONTROL
  useEffect(() => {
    if (emotion && managerRef.current.isAttached) {
      managerRef.current.setEmotion(emotion, emotionWeight ?? 1.0);
    }
  }, [emotion, emotionWeight]);

  // Handle hand pose changes
  useEffect(() => {
    if (handPose && managerRef.current.isAttached) {
      if (handPose.left) managerRef.current.setHandPose('left', handPose.left as any);
      if (handPose.right) managerRef.current.setHandPose('right', handPose.right as any);
    }
  }, [handPose]);

  // Handle fine finger curl adjustments
  useEffect(() => {
    if (fingerCurls && managerRef.current.isAttached) {
      if (fingerCurls.left) {
        Object.entries(fingerCurls.left).forEach(([f, val]) => {
          managerRef.current.setFingerCurl('left', f, val);
        });
      }
      if (fingerCurls.right) {
        Object.entries(fingerCurls.right).forEach(([f, val]) => {
          managerRef.current.setFingerCurl('right', f, val);
        });
      }
    }
  }, [fingerCurls]);

  useFrame((state_clock, delta) => {
    if (managerRef.current.isAttached) {
      // Only apply lookAt if active tracking is provided (remove mouse fallback)
      if (tracking && tracking.headYaw !== undefined) {
        managerRef.current.setLookAt(tracking.headYaw, tracking.headPitch, tracking.eyeYaw ?? 0, tracking.eyePitch ?? 0);
      }
      if (audioAmplitude !== undefined) {
        managerRef.current.setMouthOpen(audioAmplitude);
      }
      managerRef.current.update(delta);
    }
  });

  return vrm ? <primitive object={vrm.scene} /> : null;
});

const mapStateToAnimation = (state: string) => {
  switch (state) {
    case "listening": return { emotion: "relaxed", pose: "think" };
    case "thinking": return { emotion: "serious", pose: "think" };
    case "scanning": return { emotion: "surprised", pose: "scan" };
    default: return { emotion: "neutral", pose: "idle" };
  }
};

const JarvisVRM = memo(({ 
  state, 
  tracking, 
  audioAmplitude, 
  gesture, 
  emotion, 
  emotionWeight,
  modelUrl, 
  features, 
  handPose,
  fingerCurls,
  sceneAccent = "#8844ff" 
}: { 
  state: string; 
  tracking?: { headYaw: number; headPitch: number; eyeYaw: number; eyePitch: number; blinkLeft?: number; blinkRight?: number }; 
  audioAmplitude?: number; 
  gesture?: string; 
  emotion?: string; 
  emotionWeight?: number;
  modelUrl: string; 
  features: AvatarFeatures; 
  handPose?: { left?: string; right?: string };
  fingerCurls?: { left?: Record<string, number>; right?: Record<string, number> };
  sceneAccent?: string; 
}) => {
  const managerRef = useRef<VRMAnimationManager | null>(null);

  const handleLoaded = useCallback((manager: VRMAnimationManager) => {
    managerRef.current = manager;
  }, []);

  return (
    <div className="absolute inset-0 w-full h-full pointer-events-auto">
      <Canvas 
        camera={{ position: [0.8, 1.0, 3.0], fov: 35 }} 
        className="w-full h-full"
        dpr={[1, 1.5]}
        gl={{ powerPreference: "high-performance", antialias: true, toneMapping: THREE.ACESFilmicToneMapping }}
      >
        <ambientLight intensity={0.8} />
        <directionalLight position={[2, 3, 5]} intensity={1.2} castShadow />
        <directionalLight position={[-2, 2, -3]} intensity={0.3} color={sceneAccent} />
        <pointLight position={[0, 2, 2]} intensity={0.4} color={sceneAccent} />
        
        <AvatarPlatform accentColor={sceneAccent} radius={1.25} position={[0, 0, 0]} />

        <group position={[0, 0, 0]}>
          <VRMModel 
            url={modelUrl} 
            state={state} 
            tracking={tracking} 
            audioAmplitude={audioAmplitude} 
            gesture={gesture} 
            emotion={emotion} 
            emotionWeight={emotionWeight}
            features={features} 
            handPose={handPose}
            fingerCurls={fingerCurls}
            onLoaded={handleLoaded} 
          />
        </group>
        
        <ContactShadows position={[0, 0.005, 0]} opacity={0.5} blur={1.8} scale={3} />
        <Environment files="/studio_small_03_1k.hdr" />
        
        <OrbitControls
          target={[0.8, 0.9, 0]}
          minDistance={1}
          maxDistance={6}
          minPolarAngle={Math.PI * 0.1}
          maxPolarAngle={Math.PI * 0.85}
        />
      </Canvas>
    </div>
  );
});

export default JarvisVRM;
