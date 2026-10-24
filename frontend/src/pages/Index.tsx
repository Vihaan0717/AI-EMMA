import { useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import JarvisAvatar from "@/components/JarvisAvatar";
import CommandConsole from "@/components/CommandConsole";
import OSHealthWidget from "@/components/OSHealthWidget";
import ToolboxSidebar, { type ToolPanel } from "@/components/ToolboxSidebar";
import NotificationSystem from "@/components/NotificationSystem";
import DesktopOverlayToggle from "@/components/DesktopOverlayToggle";
import AvatarDirector from "@/components/AvatarDirector";
import WeatherPanel from "@/components/panels/WeatherPanel";
import NewsPanel from "@/components/panels/NewsPanel";
import MoviesPanel from "@/components/panels/MoviesPanel";
import FileExplorer from "@/components/panels/FileExplorer";
import { useJarvisSocket } from "@/hooks/useJarvisSocket";
import { RefreshCw, Radio, Cpu, ShieldCheck } from "lucide-react";
import {
  DEFAULT_AVATAR_FEATURES,
  DEFAULT_WARDROBE,
  type AvatarControl,
  type AvatarFeatures,
  type AvatarWardrobe,
} from "@/lib/avatar";

const Index = () => {
  const { data, avatarState, sendCommand, controlAvatar, setHandPose, setFingerCurl } = useJarvisSocket();
  const [activePanel, setActivePanel] = useState<ToolPanel>(null);
  const [overlayMode, setOverlayMode] = useState(false);
  const [avatarFeatures, setAvatarFeatures] = useState<AvatarFeatures>(DEFAULT_AVATAR_FEATURES);
  const [wardrobe, setWardrobe] = useState<AvatarWardrobe>(DEFAULT_WARDROBE);
  const [currentTime, setCurrentTime] = useState("");
  const [emotionWeight, setEmotionWeight] = useState(0.85);

  // Real-time HUD Clock
  useEffect(() => {
    const updateClock = () => {
      const now = new Date();
      setCurrentTime(
        now.toLocaleTimeString("en-US", {
          hour12: false,
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        })
      );
    };
    updateClock();
    const timer = setInterval(updateClock, 1000);
    return () => clearInterval(timer);
  }, []);

  const applyAvatarControl = (control: AvatarControl) => {
    if (control.features) {
      setAvatarFeatures((current) => ({ ...current, ...control.features }));
    }
    if (control.emotionWeight !== undefined) {
      setEmotionWeight(control.emotionWeight);
    }
    controlAvatar(control);
  };

  const renderPanel = () => {
    switch (activePanel) {
      case "weather":
        return <WeatherPanel data={data.weather} />;
      case "news":
        return <NewsPanel news={data.news} />;
      case "movies":
        return <MoviesPanel movies={data.movies} />;
      case "files":
        return (
          <FileExplorer
            onAction={(action, params) =>
              sendCommand("PROJECT_COMMAND", { action, parameters: params })
            }
          />
        );
      default:
        return null;
    }
  };

  return (
    <div
      className={`relative min-h-screen overflow-hidden select-none transition-colors duration-500 ${
        overlayMode ? "bg-transparent" : ""
      }`}
      style={
        overlayMode
          ? { background: "transparent" }
          : {
              background:
                "radial-gradient(ellipse at 50% 0%, hsl(234 33% 8%) 0%, hsl(234 33% 4%) 70%, hsl(234 33% 3%) 100%)",
            }
      }
    >
      {/* Sci-Fi Ambient Grid & Lighting Elements */}
      {!overlayMode && (
        <>
          {/* Subtle Cyber Grid */}
          <div
            className="fixed inset-0 pointer-events-none opacity-[0.035]"
            style={{
              backgroundImage:
                "linear-gradient(hsl(184 100% 50% / 0.4) 1px, transparent 1px), linear-gradient(90deg, hsl(184 100% 50% / 0.4) 1px, transparent 1px)",
              backgroundSize: "48px 48px",
            }}
          />

          {/* Holographic Radial Accents */}
          <div
            className="fixed inset-0 pointer-events-none"
            style={{
              background:
                "radial-gradient(circle at 50% 30%, hsl(184 100% 50% / 0.04) 0%, transparent 60%), radial-gradient(circle at 85% 75%, hsl(278 99% 54% / 0.035) 0%, transparent 50%)",
            }}
          />

          {/* Futuristic Corner HUD Accents */}
          <div className="fixed top-2 left-2 w-8 h-8 border-t-2 border-l-2 border-primary/30 pointer-events-none" />
          <div className="fixed top-2 right-2 w-8 h-8 border-t-2 border-r-2 border-primary/30 pointer-events-none" />
          <div className="fixed bottom-2 left-2 w-8 h-8 border-b-2 border-l-2 border-primary/30 pointer-events-none" />
          <div className="fixed bottom-2 right-2 w-8 h-8 border-b-2 border-r-2 border-primary/30 pointer-events-none" />
        </>
      )}

      {/* Top HUD Status Bar */}
      <motion.header
        className="fixed top-3 left-4 right-4 z-40 flex items-center justify-between pointer-events-none"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        {/* Left: Mode Switch & Status */}
        <div className="flex items-center gap-3 pointer-events-auto">
          <DesktopOverlayToggle
            enabled={overlayMode}
            onToggle={() => setOverlayMode(!overlayMode)}
          />

          <div className="hidden md:flex items-center gap-2 glass-deep px-3 py-1.5 rounded-xl border border-white/10 font-mono text-[9px] text-slate-400">
            <Radio className="w-3 h-3 text-emerald-400 animate-pulse" />
            <span className="uppercase text-slate-300">LINK: 127.0.0.1:8765</span>
            <span className="text-slate-600">|</span>
            <span className="text-primary font-semibold">SYNCHRONIZED</span>
          </div>
        </div>

        {/* Center: Brand Crest with Realtime Clock & Sound Wave */}
        <div className="pointer-events-auto flex items-center gap-3 glass-deep px-4 py-1.5 rounded-2xl border border-primary/30 shadow-[0_0_20px_hsl(var(--glow-cyan)/0.15)]">
          <div className="w-2 h-2 rounded-full bg-primary shadow-[0_0_8px_hsl(var(--glow-cyan))]" />
          
          <div className="flex flex-col items-center">
            <span className="font-mono text-xs font-bold tracking-[0.28em] text-primary uppercase glow-text-cyan">
              JARVIS-X OS
            </span>
            <span className="font-mono text-[8px] tracking-[0.2em] text-slate-400">
              AUTONOMOUS ASSISTANT
            </span>
          </div>

          <div className="h-4 w-[1px] bg-white/10" />

          <div className="font-mono text-[10px] text-slate-300 font-semibold tracking-wider">
            {currentTime || "--:--:--"}
          </div>
        </div>

        {/* Right: Refresh & Action Buttons */}
        <div className="flex items-center gap-2 pointer-events-auto">
          <motion.button
            className="p-2.5 rounded-xl glass-deep border border-primary/25 text-primary hover:bg-primary/10 hover:border-primary/50 transition-all shadow-[0_0_12px_hsl(var(--glow-cyan)/0.15)]"
            whileHover={{ scale: 1.06, rotate: 180 }}
            whileTap={{ scale: 0.94 }}
            onClick={() => window.location.reload()}
            title="Refresh Interface & Models"
          >
            <RefreshCw size={15} />
          </motion.button>
        </div>
      </motion.header>

      {/* OS Health Telemetry Widget - Positioned in the upper right below top bar */}
      <div className="fixed top-16 right-4 z-30 pointer-events-auto">
        <OSHealthWidget data={data.os_context} config={data.system_config} />
      </div>

      {/* Avatar Studio / Director Controller - Collapsible & Non-overlapping */}
      <AvatarDirector
        emotion={data.currentEmotion ?? "neutral"}
        gesture={data.currentGesture ?? "idle"}
        features={avatarFeatures}
        activeWardrobe={wardrobe}
        audioAmplitude={data.audioAmplitude}
        handPose={data.handPose}
        fingerCurls={data.fingerCurls}
        onControl={applyAvatarControl}
        onWardrobeChange={setWardrobe}
        onHandPoseChange={setHandPose}
        onFingerCurlChange={setFingerCurl}
      />

      {/* 3D Avatar Background Scene */}
      <JarvisAvatar
        state={avatarState}
        tracking={data.tracking}
        audioAmplitude={data.audioAmplitude}
        gesture={data.currentGesture}
        emotion={data.currentEmotion}
        emotionWeight={emotionWeight}
        modelUrl={wardrobe.modelUrl}
        features={avatarFeatures}
        handPose={data.handPose}
        fingerCurls={data.fingerCurls}
        sceneAccent={wardrobe.accent}
      />

      {/* Toolbox Sidebar (Left Dock) */}
      <ToolboxSidebar activePanel={activePanel} onPanelChange={setActivePanel} />

      {/* Slide-out Panels (Weather, News, Movies, Files) */}
      <AnimatePresence mode="wait">
        {activePanel && (
          <motion.div
            key={activePanel}
            className="fixed left-20 top-1/2 -translate-y-1/2 z-35 pointer-events-auto"
            initial={{ opacity: 0, x: -20, scale: 0.95 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: -20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
          >
            {renderPanel()}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Notification Stream - Floats cleanly above bottom right */}
      <NotificationSystem />

      {/* Cybernetic Command Console - Centered at the bottom */}
      <CommandConsole
        onCommand={(cmd) => sendCommand("GET_CODE_GEN", { prompt: cmd })}
        result={data.code_result}
      />
    </div>
  );
};

export default Index;
