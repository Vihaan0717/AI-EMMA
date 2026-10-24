import { memo } from "react";
import { motion } from "framer-motion";
import JarvisVRM from "./JarvisVRM";
import type { AvatarFeatures } from "@/lib/avatar";

type AvatarState = "idle" | "listening" | "thinking" | "scanning";

interface JarvisAvatarProps {
  state?: AvatarState;
  tracking?: { headPitch: number; headYaw: number; eyePitch: number; eyeYaw: number; blinkLeft?: number; blinkRight?: number };
  audioAmplitude?: number;
  gesture?: string;
  emotion?: string;
  emotionWeight?: number;
  modelUrl: string;
  features: AvatarFeatures;
  handPose?: { left?: string; right?: string };
  fingerCurls?: { left?: Record<string, number>; right?: Record<string, number> };
  sceneAccent?: string;
}

const JarvisAvatar = memo(({ 
  state = "idle", 
  tracking, 
  audioAmplitude, 
  gesture, 
  emotion, 
  emotionWeight,
  modelUrl, 
  features, 
  handPose, 
  fingerCurls,
  sceneAccent 
}: JarvisAvatarProps) => {
  const ringColors: Record<AvatarState, string> = {
    idle: "hsl(184, 100%, 50%)",
    listening: "hsl(184, 100%, 50%)",
    thinking: "hsl(278, 99%, 54%)",
    scanning: "hsl(184, 100%, 50%)",
  };

  const color = ringColors[state];

  return (
    <motion.div
      className="fixed inset-0 z-0 pointer-events-none"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
    >
      <div className="relative w-full h-full">
        {/* VRM 3D Model background integration */}
        <JarvisVRM
          state={state}
          tracking={tracking}
          audioAmplitude={audioAmplitude}
          gesture={gesture}
          emotion={emotion}
          emotionWeight={emotionWeight}
          modelUrl={modelUrl}
          features={features}
          handPose={handPose}
          fingerCurls={fingerCurls}
          sceneAccent={sceneAccent}
        />

        {/* Subtle Sci-Fi Floor Ring below avatar */}
        <div className="absolute bottom-16 left-1/2 -translate-x-1/2 w-80 h-20 rounded-full border border-primary/15 opacity-40 [transform:rotateX(75deg)] shadow-[0_0_50px_hsl(var(--glow-cyan)/0.15)] pointer-events-none" />

        {/* Avatar Status Badge - placed cleanly at bottom-left corner of avatar zone, avoiding console collision */}
        <motion.div
          className="absolute bottom-6 left-24 glass-deep px-3 py-1.5 rounded-full border border-white/10 flex items-center gap-2 pointer-events-auto"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <span
            className="w-2 h-2 rounded-full animate-ping"
            style={{ backgroundColor: color }}
          />
          <span
            className="font-mono text-[10px] tracking-[0.2em] uppercase font-semibold"
            style={{ color }}
          >
            AVA: {state === "idle" ? "STANDBY" : state.toUpperCase()}
          </span>
          {emotion && (
            <span className="font-mono text-[9px] text-slate-400 uppercase border-l border-white/10 pl-2">
              {emotion}
            </span>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
});

export default JarvisAvatar;
