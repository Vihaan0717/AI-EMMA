import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Send, 
  Copy, 
  Check, 
  Terminal, 
  Sparkles, 
  CornerDownLeft, 
  ShieldCheck, 
  ChevronUp, 
  ChevronDown, 
  Minimize2, 
  Maximize2 
} from "lucide-react";

interface CommandConsoleProps {
  onCommand?: (cmd: string) => void;
  result?: string;
}

const quickSuggestions = [
  "scan_physical_environment",
  "system_telemetry_check",
  "write python script for data analysis",
  "avatar_gesture wave",
];

const CommandConsole = ({ onCommand, result }: CommandConsoleProps) => {
  const [isMinimized, setIsMinimized] = useState(true);
  const [input, setInput] = useState("");
  const [history, setHistory] = useState<{ type: "input" | "output"; text: string }[]>([
    { type: "output", text: "JARVIS OS v2.5 [NEURAL CORE ACTIVE]. Ready for command sequences..." },
  ]);
  const [copied, setCopied] = useState<number | null>(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history]);

  // Handle incoming AI results
  useEffect(() => {
    if (result) {
      setHistory((prev) => [...prev, { type: "output", text: result }]);
      if (isMinimized) {
        setUnreadCount((c) => c + 1);
      }
    }
  }, [result, isMinimized]);

  // Focus input when expanding
  useEffect(() => {
    if (!isMinimized) {
      setUnreadCount(0);
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isMinimized]);

  // Keyboard shortcut: Esc to minimize, Ctrl+K to toggle
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !isMinimized) {
        setIsMinimized(true);
      } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setIsMinimized((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isMinimized]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim()) return;
    setHistory((prev) => [...prev, { type: "input", text: input }]);
    onCommand?.(input);
    setInput("");
  };

  const handleCopy = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopied(idx);
    setTimeout(() => setCopied(null), 2000);
  };

  const handleChipClick = (suggestion: string) => {
    setInput(suggestion);
    inputRef.current?.focus();
  };

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-40 pointer-events-auto">
      <AnimatePresence mode="wait">
        {isMinimized ? (
          /* Minimized Compact Floating Sci-Fi Bar / Pill */
          <motion.button
            key="minimized-console"
            onClick={() => setIsMinimized(false)}
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            className="group flex items-center gap-3 px-4 py-2 rounded-2xl glass-deep border border-primary/30 shadow-[0_4px_25px_hsl(var(--glow-cyan)/0.25)] hover:border-primary/60 hover:shadow-[0_0_30px_hsl(var(--glow-cyan)/0.4)] transition-all cursor-pointer select-none"
            title="Click to maximize Command Console (or Ctrl+K)"
          >
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse shadow-[0_0_8px_hsl(var(--glow-cyan))]" />
              <Terminal className="w-3.5 h-3.5 text-primary group-hover:rotate-12 transition-transform" />
              <span className="font-mono text-[11px] font-semibold tracking-wider text-slate-200 uppercase glow-text-cyan">
                COMMAND INTERFACE
              </span>
            </div>

            <div className="h-3 w-[1px] bg-white/10" />

            <div className="flex items-center gap-2 font-mono text-[10px] text-slate-400">
              <span className="hidden sm:inline text-slate-500">SYS_PORT: 8765</span>
              {unreadCount > 0 && (
                <span className="px-1.5 py-0.2 rounded-full bg-secondary/30 border border-secondary text-[9px] text-secondary font-bold animate-bounce">
                  {unreadCount} NEW
                </span>
              )}
            </div>

            <div className="flex items-center gap-1 pl-1 text-primary/80 group-hover:text-primary transition-colors">
              <span className="font-mono text-[9px] tracking-widest uppercase hidden md:inline opacity-70">
                TOUCH TO EXPAND
              </span>
              <ChevronUp className="w-3.5 h-3.5 group-hover:-translate-y-0.5 transition-transform" />
            </div>
          </motion.button>
        ) : (
          /* Maximized Full Cybernetic Command Console */
          <motion.div
            key="maximized-console"
            className="w-[calc(100vw-2rem)] max-w-2xl px-2 sm:px-0"
            initial={{ opacity: 0, y: 30, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 30, scale: 0.96 }}
            transition={{ duration: 0.28, ease: "easeOut" }}
          >
            <div className="glass-deep rounded-2xl border border-white/15 shadow-[0_16px_50px_rgba(0,0,0,0.8)] backdrop-blur-2xl p-3.5 transition-all focus-within:border-primary/50 focus-within:shadow-[0_0_30px_hsl(var(--glow-cyan)/0.3)] relative overflow-hidden">
              {/* Subtle cyan ambient glow inside console */}
              <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-primary/60 to-transparent" />

              {/* Console Header Bar */}
              <div className="flex items-center justify-between pb-2 mb-2 border-b border-white/10 font-mono text-[9px] text-slate-400">
                <div 
                  className="flex items-center gap-2 cursor-pointer select-none"
                  onClick={() => setIsMinimized(true)}
                  title="Click header to minimize"
                >
                  <span className="w-2 h-2 rounded-full bg-primary animate-pulse shadow-[0_0_8px_hsl(var(--glow-cyan))]" />
                  <span className="text-primary font-semibold tracking-widest uppercase">COMMAND INTERFACE</span>
                  <span className="text-slate-600">|</span>
                  <span className="text-slate-400 uppercase hidden sm:inline">SYS_PORT: 8765</span>
                </div>

                <div className="flex items-center gap-2.5">
                  <div className="hidden sm:flex items-center gap-1.5 text-emerald-400">
                    <ShieldCheck className="w-3 h-3" />
                    <span className="tracking-wider uppercase text-[8px]">ENCRYPTED</span>
                  </div>

                  <button
                    onClick={() => setIsMinimized(true)}
                    className="p-1 px-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-primary/40 text-slate-300 hover:text-primary transition-all flex items-center gap-1 font-mono text-[9px] tracking-wider uppercase"
                    title="Minimize window (Esc)"
                  >
                    <span>Minimize</span>
                    <ChevronDown className="w-3 h-3" />
                  </button>
                </div>
              </div>

              {/* History stream */}
              <div
                ref={scrollRef}
                className="max-h-36 overflow-y-auto mb-2.5 space-y-1.5 pr-1 scrollbar-thin scrollbar-thumb-primary/20 font-mono text-xs"
              >
                <AnimatePresence>
                  {history.map((item, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, y: 4 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex items-start gap-2 group leading-relaxed"
                    >
                      {item.type === "input" ? (
                        <span className="text-primary font-semibold shrink-0">❯</span>
                      ) : (
                        <span className="text-secondary font-semibold shrink-0">::</span>
                      )}

                      <span
                        className={`flex-1 break-words ${
                          item.type === "input" ? "text-primary font-medium" : "text-slate-300"
                        }`}
                      >
                        {item.text}
                      </span>

                      {item.type === "output" && (
                        <button
                          onClick={() => handleCopy(item.text, idx)}
                          className="opacity-0 group-hover:opacity-100 transition-opacity ml-1 shrink-0 p-0.5 text-slate-400 hover:text-white"
                          title="Copy response"
                        >
                          {copied === idx ? (
                            <Check className="w-3 h-3 text-emerald-400" />
                          ) : (
                            <Copy className="w-3 h-3" />
                          )}
                        </button>
                      )}
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>

              {/* Quick Suggestion Chips */}
              <div className="flex items-center gap-1.5 overflow-x-auto pb-2 scrollbar-none">
                {quickSuggestions.map((s, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleChipClick(s)}
                    className="px-2 py-0.5 rounded-md bg-white/[0.03] hover:bg-white/[0.08] border border-white/5 hover:border-primary/30 text-[9px] font-mono text-slate-400 hover:text-primary transition-all whitespace-nowrap"
                  >
                    +{s}
                  </button>
                ))}
              </div>

              {/* Input bar */}
              <form onSubmit={handleSubmit} className="flex items-center gap-2 pt-1.5 border-t border-white/5">
                <Terminal className="w-4 h-4 text-primary shrink-0" />
                <input
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask Jarvis, issue system commands, or trigger skills..."
                  className="flex-1 bg-transparent font-mono text-xs text-foreground placeholder:text-slate-500 outline-none tracking-wide"
                />

                <button
                  type="submit"
                  disabled={!input.trim()}
                  className="px-2.5 py-1.5 rounded-lg bg-primary/20 hover:bg-primary/30 border border-primary/40 text-primary transition-all disabled:opacity-30 disabled:pointer-events-none flex items-center gap-1 font-mono text-[10px] uppercase font-semibold"
                >
                  <span>Send</span>
                  <CornerDownLeft className="w-3 h-3" />
                </button>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default CommandConsole;
