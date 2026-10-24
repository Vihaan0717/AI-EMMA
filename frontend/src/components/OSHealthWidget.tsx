import { motion, useSpring, useTransform } from "framer-motion";
import { useEffect, useState } from "react";
import { Activity, Cpu, HardDrive, Battery, BatteryCharging, Zap, Shield, Database, ChevronDown, ChevronUp } from "lucide-react";

interface OSHealthProps {
  data?: {
    active_window: string;
    cpu_percent: number;
    memory_percent: number;
    battery_percent?: number;
    is_plugged_in?: boolean;
    biological_state?: string;
  };
  config?: {
    environment: string;
    model: string;
  };
}

const OSHealthWidget = ({ data, config }: OSHealthProps) => {
  const [isExpanded, setIsExpanded] = useState(true);

  const springConfig = { damping: 20, stiffness: 100, mass: 0.5 };
  const cpuSpring = useSpring(0, springConfig);
  const memSpring = useSpring(0, springConfig);
  const batSpring = useSpring(100, springConfig);

  const cpuPercent = Math.round(data?.cpu_percent || 0);
  const memPercent = Math.round(data?.memory_percent || 0);
  const batPercent = Math.round(data?.battery_percent ?? 100);

  useEffect(() => {
    cpuSpring.set(cpuPercent);
    memSpring.set(memPercent);
    batSpring.set(batPercent);
  }, [cpuPercent, memPercent, batPercent, cpuSpring, memSpring, batSpring]);

  const stats = {
    isPluggedIn: data?.is_plugged_in ?? true,
    state: data?.biological_state || "System Nominal",
    activity: data?.active_window || "Standby",
  };

  const StatBar = ({
    label,
    value,
    springValue,
    icon: Icon,
    color = "hsl(184 100% 50%)",
  }: {
    label: string;
    value: number;
    springValue: any;
    icon: any;
    color?: string;
  }) => {
    const width = useTransform(springValue, (v: number) => `${Math.min(100, Math.max(0, v))}%`);

    return (
      <div className="space-y-1">
        <div className="flex items-center justify-between font-mono text-[10px]">
          <span className="flex items-center gap-1.5 text-slate-300">
            <Icon className="w-3 h-3 text-primary shrink-0" />
            <span className="tracking-wider uppercase">{label}</span>
          </span>
          <span className="font-semibold text-primary font-mono text-[10px]">
            {value}%
          </span>
        </div>
        <div className="h-1.5 rounded-full bg-black/40 border border-white/5 overflow-hidden p-[1px]">
          <motion.div
            className="h-full rounded-full"
            style={{
              width,
              background: `linear-gradient(90deg, ${color}, hsl(278 99% 54% / 0.8))`,
              boxShadow: `0 0 10px ${color}`,
            }}
          />
        </div>
      </div>
    );
  };

  return (
    <motion.div
      className="glass-deep rounded-2xl border border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.5)] overflow-hidden w-72 backdrop-blur-2xl transition-all"
      initial={{ opacity: 0, x: 25 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.2 }}
    >
      {/* Widget Header */}
      <div className="flex items-center justify-between px-3.5 py-2.5 border-b border-white/10 bg-white/[0.02]">
        <div className="flex items-center gap-2">
          <div className="relative">
            <Activity className="w-3.5 h-3.5 text-primary" />
            <span className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 rounded-full bg-primary animate-ping" />
          </div>
          <h3 className="font-mono text-[11px] font-semibold text-primary tracking-[0.16em] uppercase">
            OS Telemetry
          </h3>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-primary/10 border border-primary/25">
            <Shield className="w-2.5 h-2.5 text-primary" />
            <span className="font-mono text-[8px] font-bold text-primary tracking-wider uppercase">
              {config?.environment || "DEV"}
            </span>
          </div>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-slate-400 hover:text-white transition-colors p-0.5"
            aria-label="Toggle telemetry details"
          >
            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Widget Body */}
      {isExpanded && (
        <div className="p-3.5 space-y-3">
          {/* Main Gauges */}
          <div className="space-y-2.5">
            <StatBar label="CPU Load" value={cpuPercent} springValue={cpuSpring} icon={Cpu} />
            <StatBar label="RAM Usage" value={memPercent} springValue={memSpring} icon={HardDrive} color="hsl(278 99% 54%)" />
            <StatBar
              label={stats.isPluggedIn ? "PWR (AC)" : "Battery"}
              value={batPercent}
              springValue={batSpring}
              icon={stats.isPluggedIn ? BatteryCharging : Battery}
              color="hsl(45 100% 55%)"
            />
          </div>

          {/* Biological State & Active Model */}
          <div className="pt-2 border-t border-white/10 space-y-2">
            <div className="flex items-center justify-between text-[10px] font-mono">
              <span className="flex items-center gap-1 text-slate-400">
                <Zap className="w-3 h-3 text-secondary" />
                <span>STATE</span>
              </span>
              <span
                className={`font-semibold tracking-wide uppercase ${
                  stats.state.includes("Stressed") ? "text-rose-400" : "text-emerald-300"
                }`}
              >
                {stats.state}
              </span>
            </div>

            <div className="flex items-center justify-between text-[10px] font-mono px-2 py-1 rounded-lg bg-black/30 border border-white/5">
              <span className="flex items-center gap-1.5 text-slate-400">
                <Database className="w-3 h-3 text-primary" />
                <span>AI CORE</span>
              </span>
              <span className="font-semibold text-slate-200 truncate max-w-[120px]">
                {config?.model || "LLAMA 3.2"}
              </span>
            </div>

            <div className="flex items-center gap-1.5 text-[9px] font-mono text-slate-400 truncate px-1">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse shrink-0" />
              <span className="truncate" title={stats.activity}>
                Focus: {stats.activity}
              </span>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default OSHealthWidget;
