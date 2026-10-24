import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, FileText, Bell, X } from "lucide-react";

interface Notification {
  id: string;
  type: "info" | "warning" | "file";
  message: string;
  time: string;
}

const NotificationSystem = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const dismiss = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const configMap = {
    info: {
      icon: Bell,
      border: "border-primary/40",
      glow: "shadow-[0_0_12px_hsl(var(--glow-cyan)/0.15)]",
      badge: "bg-primary/20 text-primary",
    },
    warning: {
      icon: AlertCircle,
      border: "border-amber-400/40",
      glow: "shadow-[0_0_12px_rgba(251,191,36,0.15)]",
      badge: "bg-amber-400/20 text-amber-300",
    },
    file: {
      icon: FileText,
      border: "border-secondary/40",
      glow: "shadow-[0_0_12px_hsl(var(--glow-purple)/0.15)]",
      badge: "bg-secondary/20 text-secondary",
    },
  };

  return (
    <div className="fixed top-[22rem] right-4 z-30 flex flex-col gap-2 w-72 pointer-events-none">
      <AnimatePresence>
        {notifications.map((notif) => {
          const cfg = configMap[notif.type];
          const Icon = cfg.icon;

          return (
            <motion.div
              key={notif.id}
              className={`glass-deep p-2.5 rounded-xl flex items-start gap-2.5 border ${cfg.border} ${cfg.glow} pointer-events-auto backdrop-blur-xl`}
              initial={{ opacity: 0, x: 25, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 25, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              layout
            >
              <div className={`p-1.5 rounded-lg ${cfg.badge} shrink-0 mt-0.5`}>
                <Icon className="w-3.5 h-3.5" />
              </div>

              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-slate-100 leading-snug truncate">{notif.message}</p>
                <p className="font-mono text-[9px] text-slate-400 mt-0.5">{notif.time}</p>
              </div>

              <button
                onClick={() => dismiss(notif.id)}
                className="text-slate-400 hover:text-white transition-colors p-0.5"
                title="Dismiss"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
};

export default NotificationSystem;
