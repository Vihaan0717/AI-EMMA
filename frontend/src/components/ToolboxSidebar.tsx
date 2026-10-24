import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Cloud, Newspaper, Film, BarChart3, FolderOpen, Settings, ChevronRight, Sparkles } from "lucide-react";

type ToolPanel = "weather" | "news" | "movies" | "stats" | "files" | "settings" | null;

interface ToolboxSidebarProps {
  activePanel: ToolPanel;
  onPanelChange: (panel: ToolPanel) => void;
}

const tools = [
  { id: "weather" as ToolPanel, icon: Cloud, label: "Atmospheric & Weather" },
  { id: "news" as ToolPanel, icon: Newspaper, label: "Global Intel & News" },
  { id: "movies" as ToolPanel, icon: Film, label: "Media & Cinema" },
  { id: "stats" as ToolPanel, icon: BarChart3, label: "Neural Diagnostics" },
  { id: "files" as ToolPanel, icon: FolderOpen, label: "Workspace Files" },
  { id: "settings" as ToolPanel, icon: Settings, label: "System Config" },
];

const ToolboxSidebar = ({ activePanel, onPanelChange }: ToolboxSidebarProps) => {
  const [hovered, setHovered] = useState<ToolPanel>(null);

  return (
    <motion.div
      className="fixed left-3 top-1/2 -translate-y-1/2 z-40 flex items-center"
      initial={{ x: -70, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ delay: 0.15, type: "spring", stiffness: 120, damping: 18 }}
    >
      <div className="relative glass-deep p-2 rounded-2xl flex flex-col gap-2 border border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.6)] backdrop-blur-2xl">
        {/* Subtle accent glow line on sidebar */}
        <div className="absolute -left-[1px] top-4 bottom-4 w-[2px] bg-gradient-to-b from-primary/60 via-secondary/40 to-primary/60 rounded-full" />

        {tools.map((tool) => {
          const isActive = activePanel === tool.id;
          const isHovered = hovered === tool.id;

          return (
            <motion.button
              key={tool.id}
              onMouseEnter={() => setHovered(tool.id)}
              onMouseLeave={() => setHovered(null)}
              onClick={() => onPanelChange(isActive ? null : tool.id)}
              className={`relative p-3 rounded-xl transition-all duration-300 flex items-center justify-center group ${
                isActive
                  ? "bg-primary/20 text-primary border border-primary/40 glow-border-cyan"
                  : "text-muted-foreground hover:text-foreground hover:bg-white/[0.06] border border-transparent"
              }`}
              whileHover={{ scale: 1.08 }}
              whileTap={{ scale: 0.94 }}
            >
              {/* Active pulsing cyan dot */}
              {isActive && (
                <span className="absolute -left-1 top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_hsl(var(--glow-cyan))]" />
              )}

              <tool.icon className={`w-4 h-4 transition-transform duration-300 ${isHovered ? "scale-110" : ""}`} />

              {/* Enhanced Tooltip */}
              <AnimatePresence>
                {isHovered && (
                  <motion.div
                    className="absolute left-full ml-3 top-1/2 -translate-y-1/2 glass-deep px-3 py-1.5 rounded-xl border border-primary/30 shadow-[0_0_20px_rgba(0,0,0,0.5)] whitespace-nowrap z-50 pointer-events-none"
                    initial={{ opacity: 0, x: -8, scale: 0.95 }}
                    animate={{ opacity: 1, x: 0, scale: 1 }}
                    exit={{ opacity: 0, x: -8, scale: 0.95 }}
                    transition={{ duration: 0.15 }}
                  >
                    <div className="flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                      <span className="font-mono text-xs font-medium tracking-wide text-foreground">
                        {tool.label}
                      </span>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.button>
          );
        })}
      </div>

      {/* Active panel pointer indicator */}
      {activePanel && (
        <motion.div
          className="ml-2 text-primary drop-shadow-[0_0_8px_hsl(var(--glow-cyan))]"
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <ChevronRight className="w-4 h-4 animate-pulse" />
        </motion.div>
      )}
    </motion.div>
  );
};

export default ToolboxSidebar;
export type { ToolPanel };
