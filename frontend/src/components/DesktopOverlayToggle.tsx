import { motion } from "framer-motion";
import { Monitor, Layers } from "lucide-react";

interface DesktopOverlayToggleProps {
  enabled: boolean;
  onToggle: () => void;
}

const DesktopOverlayToggle = ({ enabled, onToggle }: DesktopOverlayToggleProps) => {
  return (
    <motion.button
      onClick={onToggle}
      className={`glass-card px-3 py-2 flex items-center gap-2.5 cursor-pointer transition-all duration-300 group border ${
        enabled
          ? "border-primary/50 shadow-[0_0_15px_hsl(var(--glow-cyan)/0.25)] bg-primary/10"
          : "border-white/10 hover:border-white/20 bg-black/30"
      }`}
      whileHover={{ scale: 1.04, y: -1 }}
      whileTap={{ scale: 0.96 }}
      initial={{ opacity: 0, y: -15 }}
      animate={{ opacity: 1, y: 0 }}
      title={enabled ? "Switch to Full HUD Mode" : "Switch to Transparent Overlay Mode"}
    >
      <div className="relative">
        {enabled ? (
          <Layers className="w-4 h-4 text-primary animate-pulse" />
        ) : (
          <Monitor className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />
        )}
      </div>

      <div className="flex flex-col text-left">
        <span className="font-mono text-[9px] uppercase tracking-[0.18em] text-muted-foreground leading-none">
          Display Mode
        </span>
        <span
          className={`font-mono text-xs font-semibold tracking-wider transition-colors ${
            enabled ? "text-primary glow-text-cyan" : "text-slate-300"
          }`}
        >
          {enabled ? "HUD OVERLAY" : "DESKTOP OS"}
        </span>
      </div>

      <div
        className={`w-8 h-4 rounded-full flex items-center px-0.5 ml-1 transition-colors duration-300 border ${
          enabled
            ? "bg-primary/25 border-primary/40"
            : "bg-black/40 border-white/10"
        }`}
      >
        <motion.div
          className={`w-3 h-3 rounded-full transition-shadow ${
            enabled
              ? "bg-primary shadow-[0_0_8px_hsl(var(--glow-cyan))]"
              : "bg-muted-foreground/60"
          }`}
          animate={{ x: enabled ? 14 : 0 }}
          transition={{ type: "spring", stiffness: 500, damping: 28 }}
        />
      </div>
    </motion.button>
  );
};

export default DesktopOverlayToggle;
