import { useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Activity,
  AudioLines,
  ChevronDown,
  ChevronUp,
  Eye,
  HeartPulse,
  LoaderCircle,
  ScanFace,
  Shirt,
  Sparkles,
  Upload,
  WandSparkles,
  Sliders,
  Smile,
  X,
} from "lucide-react";
import {
  AVATAR_WARDROBE,
  type AvatarControl,
  type AvatarFeature,
  type AvatarFeatures,
  type AvatarWardrobe,
} from "@/lib/avatar";

interface AvatarDirectorProps {
  emotion: string;
  gesture: string;
  features: AvatarFeatures;
  activeWardrobe: AvatarWardrobe;
  audioAmplitude?: number;
  handPose?: { left?: string; right?: string };
  fingerCurls?: { left?: Record<string, number>; right?: Record<string, number> };
  onControl: (control: AvatarControl) => void;
  onWardrobeChange: (wardrobe: AvatarWardrobe) => void;
  onHandPoseChange?: (hand: "left" | "right" | "both", pose: string) => void;
  onFingerCurlChange?: (hand: "left" | "right" | "both", finger: string, amount: number) => void;
}

const emotions = [
  { id: "neutral", label: "Calm", color: "text-slate-200" },
  { id: "happy", label: "Happy", color: "text-amber-300" },
  { id: "thinking", label: "Think", color: "text-violet-300" },
  { id: "surprised", label: "Surprise", color: "text-fuchsia-300" },
  { id: "sad", label: "Sad", color: "text-sky-300" },
  { id: "angry", label: "Angry", color: "text-rose-400" },
  { id: "wink", label: "Wink", color: "text-pink-300" },
  { id: "smug", label: "Smug", color: "text-emerald-300" },
  { id: "shy", label: "Shy", color: "text-rose-300" },
  { id: "relaxed", label: "Relaxed", color: "text-teal-300" },
] as const;

const gestures = [
  { id: "idle", label: "Idle" },
  { id: "walk", label: "Walk" },
  { id: "run", label: "Jog" },
  { id: "explain", label: "Explain" },
  { id: "nod", label: "Nod" },
  { id: "disagree", label: "Disagree" },
  { id: "point", label: "Point" },
  { id: "listen", label: "Listen" },
  { id: "reassure", label: "Reassure" },
  { id: "confusion", label: "Puzzled" },
  { id: "wave", label: "Wave" },
  { id: "think", label: "Think" },
  { id: "peace_sign", label: "Peace" },
  { id: "cheer", label: "Cheer" },
  { id: "clap", label: "Clap" },
  { id: "bow", label: "Bow" },
  { id: "hug_self", label: "Comfort" },
  { id: "sit", label: "Sit" },
  { id: "seiza", label: "Seiza" },
  { id: "agura", label: "Cross-leg" },
  { id: "afk_idle", label: "AFK Idle" },
  { id: "dance", label: "Dance" },
] as const;

const featureMeta: { id: AvatarFeature; label: string; icon: typeof Activity }[] = [
  { id: "lipSync", label: "Lip sync", icon: AudioLines },
  { id: "eyeTracking", label: "Eyes + blink", icon: Eye },
  { id: "breathing", label: "Breathing", icon: HeartPulse },
  { id: "hairPhysics", label: "Hair physics", icon: Sparkles },
];

const emotionAliases: Record<string, string> = {
  joy: "happy",
  joyful: "happy",
  happiness: "happy",
  sorrow: "sad",
  sadness: "sad",
  mad: "angry",
  rage: "angry",
  relaxed: "relaxed",
  serious: "serious",
  ponder: "thinking",
  think: "thinking",
  curious: "thinking",
  surprise: "surprised",
  shocked: "surprised",
  playful: "wink",
  flirty: "wink",
  confident: "smug",
  smug: "smug",
  bashful: "shy",
  shy: "shy",
};

const gestureAliases: Record<string, string> = {
  walking: "walk",
  wave_hand: "wave",
  waving: "wave",
  greeting: "wave",
  thinking: "think",
  ponder: "think",
  explain: "explain",
  explaining: "explain",
  talk: "explain",
  talking: "explain",
  speak: "explain",
  cheer: "cheer",
  cheering: "cheer",
  celebrate: "cheer",
  celebrating: "cheer",
  clap: "clap",
  clapping: "clap",
  applause: "clap",
  applaud: "clap",
  sitting: "sit",
  crossed_arms: "hug_self",
  comfort: "hug_self",
  hug: "hug_self",
  open_hands: "peace_sign",
  peace: "peace_sign",
  victory: "peace_sign",
  bowing: "bow",
  pointing: "think",
  dancing: "dance",
};

function normalize(value: unknown, aliases: Record<string, string>, allowed: readonly string[]) {
  if (typeof value !== "string") return undefined;
  const normalized = value.toLowerCase().trim().replace(/[\s-]+/g, "_");
  const resolved = aliases[normalized] ?? normalized;
  return allowed.includes(resolved) ? resolved : undefined;
}

function readLLMCue(cue: string): AvatarControl {
  const clean = cue.replace(/```json|```/gi, "").trim();
  let input: Record<string, unknown> = {};

  try {
    input = JSON.parse(clean);
  } catch {
    input = { text: cue };
  }

  const source = [
    String(input.emotion ?? ""),
    String(input.gesture ?? input.action ?? ""),
    String(input.text ?? input.speech ?? input.reply ?? cue),
  ].join(" ").toLowerCase();

  const emotion = normalize(
    input.emotion ?? emotions.find(({ id }) => source.includes(id))?.id,
    emotionAliases,
    emotions.map(({ id }) => id),
  );
  const gesture = normalize(
    input.gesture ?? input.action ?? gestures.find(({ id }) => source.includes(id.replace("_", " ")))?.id,
    gestureAliases,
    gestures.map(({ id }) => id),
  );
  const speech = [input.speech, input.text, input.reply].find((item) => typeof item === "string") as string | undefined;
  const audioUrl = [input.audio_url, input.audioUrl].find((item) => typeof item === "string") as string | undefined;

  return { emotion, gesture, speech, audioUrl };
}

const AvatarDirector = ({
  emotion,
  gesture,
  features,
  activeWardrobe,
  audioAmplitude = 0,
  onControl,
  onWardrobeChange,
  onHandPoseChange,
  onFingerCurlChange,
  handPose,
  fingerCurls,
}: AvatarDirectorProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"cue" | "pose" | "bones" | "wardrobe">("pose");
  const [selectedHand, setSelectedHand] = useState<"both" | "left" | "right">("both");
  const [intensity, setIntensity] = useState(0.85);
  const [cue, setCue] = useState('{"emotion":"happy","gesture":"wave","text":"Hello."}');
  const [lastCue, setLastCue] = useState("Awaiting LLM output");
  const uploadRef = useRef<HTMLInputElement>(null);

  const applyCue = () => {
    const control = readLLMCue(cue);
    onControl(control);
    setLastCue(`${control.emotion ?? "neutral"} · ${control.gesture ?? "idle"}`);
  };

  const selectFeature = (feature: AvatarFeature) => {
    onControl({ features: { [feature]: !features[feature] } });
  };

  const handleVRMUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const [file] = Array.from(event.target.files ?? []);
    if (!file) return;

    onWardrobeChange({
      id: `local-${file.name}-${file.lastModified}`,
      name: file.name.replace(/\.vrm$/i, ""),
      description: "Local VRM wardrobe / character",
      modelUrl: URL.createObjectURL(file),
      accent: "#a78bfa",
      source: "local",
    });
    event.target.value = "";
  };

  const lipSyncPercent = Math.round(Math.min(1, audioAmplitude) * 100);

  return (
    <>
      {/* Floating Trigger Pill button when collapsed or to toggle */}
      {!isOpen && (
        <motion.button
          onClick={() => setIsOpen(true)}
          className="fixed right-4 top-[17.5rem] z-40 glass-deep px-3.5 py-2.5 rounded-2xl flex items-center gap-2.5 border border-secondary/40 shadow-[0_0_20px_hsl(var(--glow-purple)/0.25)] text-slate-200 hover:text-white transition-all group"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <div className="w-6 h-6 rounded-lg bg-secondary/20 flex items-center justify-center text-secondary group-hover:scale-110 transition-transform">
            <WandSparkles className="w-3.5 h-3.5" />
          </div>
          <div className="text-left font-mono">
            <div className="text-[10px] uppercase tracking-wider text-secondary font-semibold">Avatar Studio</div>
            <div className="text-[8px] text-slate-400 uppercase tracking-widest">{emotion} · {gesture}</div>
          </div>
        </motion.button>
      )}

      {/* Expanded Avatar Director Modal/Drawer */}
      <AnimatePresence>
        {isOpen && (
          <motion.aside
            className="fixed right-4 top-[17.5rem] z-40 w-[min(23rem,calc(100vw-2rem))] overflow-hidden rounded-2xl border border-white/10 glass-deep shadow-2xl shadow-black/60 backdrop-blur-2xl"
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ duration: 0.25 }}
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-white/10 px-3.5 py-2.5 bg-white/[0.02]">
              <div className="flex items-center gap-2">
                <div className="grid h-7 w-7 place-items-center rounded-lg bg-secondary/20 text-secondary">
                  <WandSparkles className="h-3.5 w-3.5" />
                </div>
                <div>
                  <p className="font-mono text-[11px] font-semibold tracking-[0.14em] text-white">AVATAR STUDIO</p>
                  <p className="font-mono text-[8px] uppercase tracking-[0.1em] text-emerald-300">VRM Kinematics & Body Core</p>
                </div>
              </div>

              <button
                className="rounded-lg p-1.5 text-slate-400 hover:bg-white/10 hover:text-white transition-colors"
                onClick={() => setIsOpen(false)}
                aria-label="Close avatar director"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Sub-Navigation Tabs */}
            <div className="flex border-b border-white/10 bg-black/20 p-1 gap-1">
              <button
                onClick={() => setActiveTab("pose")}
                className={`flex-1 py-1 px-1.5 rounded-lg font-mono text-[9px] tracking-wider uppercase transition-all flex items-center justify-center gap-1 ${
                  activeTab === "pose"
                    ? "bg-secondary/20 text-white border border-secondary/40 shadow-[0_0_10px_hsl(var(--glow-purple)/0.2)]"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <Smile className="w-2.5 h-2.5 text-secondary" /> Poses
              </button>
              <button
                onClick={() => setActiveTab("bones")}
                className={`flex-1 py-1 px-1.5 rounded-lg font-mono text-[9px] tracking-wider uppercase transition-all flex items-center justify-center gap-1 ${
                  activeTab === "bones"
                    ? "bg-secondary/20 text-white border border-secondary/40 shadow-[0_0_10px_hsl(var(--glow-purple)/0.2)]"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <Sliders className="w-2.5 h-2.5 text-secondary" /> Bones
              </button>
              <button
                onClick={() => setActiveTab("cue")}
                className={`flex-1 py-1 px-1.5 rounded-lg font-mono text-[9px] tracking-wider uppercase transition-all flex items-center justify-center gap-1 ${
                  activeTab === "cue"
                    ? "bg-secondary/20 text-white border border-secondary/40 shadow-[0_0_10px_hsl(var(--glow-purple)/0.2)]"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <Sparkles className="w-2.5 h-2.5 text-secondary" /> Cue
              </button>
              <button
                onClick={() => setActiveTab("wardrobe")}
                className={`flex-1 py-1 px-1.5 rounded-lg font-mono text-[9px] tracking-wider uppercase transition-all flex items-center justify-center gap-1 ${
                  activeTab === "wardrobe"
                    ? "bg-secondary/20 text-white border border-secondary/40 shadow-[0_0_10px_hsl(var(--glow-purple)/0.2)]"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <Shirt className="w-2.5 h-2.5 text-secondary" /> Models
              </button>
            </div>

            {/* Tab Contents */}
            <div className="max-h-[calc(100vh-25rem)] overflow-y-auto p-3.5 space-y-4">
              {activeTab === "pose" && (
                <>
                  <section>
                    <p className="mb-1.5 font-mono text-[10px] uppercase tracking-[0.14em] text-slate-400 flex items-center justify-between">
                      <span>Facial Expression</span>
                      <span className="text-secondary font-semibold">{emotion} ({Math.round(intensity * 100)}%)</span>
                    </p>
                    <div className="grid grid-cols-5 gap-1.5">
                      {emotions.map((item) => (
                        <button
                          key={item.id}
                          onClick={() => onControl({ emotion: item.id, emotionWeight: intensity })}
                          className={`rounded-lg border px-1.5 py-1.5 text-center transition-all ${
                            emotion === item.id
                              ? "border-secondary/60 bg-secondary/20 shadow-[0_0_10px_hsl(var(--glow-purple)/0.3)] text-white font-semibold"
                              : "border-white/5 bg-white/[0.02] hover:border-white/20 hover:bg-white/[0.05]"
                          }`}
                        >
                          <span className={`block font-mono text-[9px] ${item.color}`}>{item.label}</span>
                        </button>
                      ))}
                    </div>

                    {/* Expression Intensity Slider */}
                    <div className="mt-2.5 rounded-xl border border-white/5 bg-black/30 p-2 space-y-1.5">
                      <div className="flex items-center justify-between text-[9px] font-mono">
                        <span className="text-slate-400 uppercase tracking-wider flex items-center gap-1">
                          <Sliders className="w-2.5 h-2.5 text-secondary" /> Intensity
                        </span>
                        <span className="text-secondary font-semibold">{Math.round(intensity * 100)}%</span>
                      </div>
                      <input
                        type="range"
                        min="0.2"
                        max="1.0"
                        step="0.05"
                        value={intensity}
                        onChange={(e) => {
                          const val = parseFloat(e.target.value);
                          setIntensity(val);
                          onControl({ emotion, emotionWeight: val });
                        }}
                        className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-secondary"
                      />
                      <div className="flex justify-between text-[8px] font-mono text-slate-500">
                        <span>Subtle (30%)</span>
                        <span>Natural (60%)</span>
                        <span>Expressive (100%)</span>
                      </div>
                    </div>
                  </section>

                  <section>
                    <p className="mb-1.5 font-mono text-[10px] uppercase tracking-[0.14em] text-slate-400 flex items-center justify-between">
                      <span>Full-Body Action</span>
                      <span className="text-primary font-semibold">{gesture}</span>
                    </p>
                    <div className="grid grid-cols-4 gap-1.5">
                      {gestures.map((item) => (
                        <button
                          key={item.id}
                          onClick={() => onControl({ gesture: item.id })}
                          className={`rounded-lg border px-1 py-1.5 font-mono text-[9px] transition-all text-center ${
                            gesture === item.id
                              ? "border-primary/60 bg-primary/20 text-cyan-200 shadow-[0_0_10px_hsl(var(--glow-cyan)/0.3)]"
                              : "border-white/5 bg-white/[0.02] text-slate-400 hover:border-white/20 hover:text-white"
                          }`}
                        >
                          {item.label}
                        </button>
                      ))}
                    </div>
                  </section>

                  <section className="rounded-xl border border-white/10 bg-black/20 p-2.5">
                    <div className="mb-2 flex items-center justify-between">
                      <div className="flex items-center gap-1.5 text-slate-200">
                        <ScanFace className="h-3 w-3 text-primary" />
                        <span className="font-mono text-[9px] uppercase tracking-[0.12em]">Physical Layers</span>
                      </div>
                      {audioAmplitude > 0.03 ? (
                        <span className="flex items-center gap-1 font-mono text-[9px] text-emerald-300">
                          <LoaderCircle className="h-3 w-3 animate-spin" /> {lipSyncPercent}%
                        </span>
                      ) : (
                        <span className="font-mono text-[9px] text-slate-500">Idle</span>
                      )}
                    </div>
                    <div className="grid grid-cols-2 gap-1.5">
                      {featureMeta.map(({ id, label, icon: Icon }) => (
                        <button
                          key={id}
                          onClick={() => selectFeature(id)}
                          className={`flex items-center justify-between rounded-lg border px-2 py-1.5 text-left transition ${
                            features[id]
                              ? "border-emerald-300/30 bg-emerald-300/10 text-slate-100"
                              : "border-white/5 bg-black/20 text-slate-500"
                          }`}
                        >
                          <span className="flex items-center gap-1 font-mono text-[9px]">
                            <Icon className="h-3 w-3" />
                            {label}
                          </span>
                          <span className={`h-1.5 w-1.5 rounded-full ${features[id] ? "bg-emerald-300 shadow-[0_0_6px_#10b981]" : "bg-slate-600"}`} />
                        </button>
                      ))}
                    </div>
                  </section>
                </>
              )}

              {activeTab === "bones" && (
                <div className="space-y-3.5">
                  {/* Biomechanical Health Status Pill */}
                  <div className="p-2.5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 font-mono text-[9px] space-y-1">
                    <div className="flex items-center justify-between font-semibold">
                      <span>✓ 54-BONE RIG SYNCHRONIZED</span>
                      <span className="text-emerald-400">Y=0 GROUNDED</span>
                    </div>
                    <div className="text-[8px] text-slate-300 leading-relaxed">
                      • Forearm Hinge: -X Pure Flexion (No Elbow Twists)<br />
                      • Thumb Rig: 3-Joint Canonical Normalization Active<br />
                      • Platform: Concentric Holographic Ground Mounted
                    </div>
                  </div>

                  {/* Target Hand Selector */}
                  <div>
                    <p className="mb-1.5 font-mono text-[10px] uppercase tracking-[0.14em] text-slate-400">Target Hand</p>
                    <div className="grid grid-cols-3 gap-1.5">
                      {(["both", "left", "right"] as const).map((h) => (
                        <button
                          key={h}
                          onClick={() => setSelectedHand(h)}
                          className={`rounded-lg border px-2 py-1 font-mono text-[10px] uppercase transition-all ${
                            selectedHand === h
                              ? "border-secondary/60 bg-secondary/20 text-white shadow-[0_0_8px_hsl(var(--glow-purple)/0.3)]"
                              : "border-white/5 bg-white/[0.02] text-slate-400 hover:bg-white/5"
                          }`}
                        >
                          {h}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Hand Pose Presets */}
                  <div>
                    <p className="mb-1.5 font-mono text-[10px] uppercase tracking-[0.14em] text-slate-400">Hand Articulation Presets</p>
                    <div className="grid grid-cols-4 gap-1.5">
                      {[
                        { id: "relaxed", label: "Relaxed" },
                        { id: "fist", label: "Fist" },
                        { id: "point", label: "Point" },
                        { id: "peace", label: "Peace" },
                        { id: "open_palm", label: "Open" },
                        { id: "thumbs_up", label: "Thumb 👍" },
                        { id: "ok_sign", label: "OK 👌" },
                        { id: "pinch", label: "Pinch" },
                      ].map((p) => (
                        <button
                          key={p.id}
                          onClick={() => onHandPoseChange?.(selectedHand, p.id)}
                          className="rounded-lg border border-white/5 bg-white/[0.02] px-2 py-1.5 text-center font-mono text-[9px] uppercase text-slate-300 hover:border-secondary/50 hover:bg-secondary/10 hover:text-white transition-all"
                        >
                          {p.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* 5-Finger Granular Curl Sliders */}
                  <div className="space-y-2">
                    <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-slate-400">Individual Finger Curl</p>
                    {["thumb", "index", "middle", "ring", "little"].map((finger) => {
                      const curlVal = Math.round(
                        ((fingerCurls?.[selectedHand === "right" ? "right" : "left"]?.[finger] ?? 0.25) * 100)
                      );
                      return (
                        <div key={finger} className="flex items-center gap-2 font-mono text-[9px]">
                          <span className="w-12 text-slate-300 uppercase">{finger}</span>
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.05"
                            value={fingerCurls?.[selectedHand === "right" ? "right" : "left"]?.[finger] ?? 0.25}
                            onChange={(e) => onFingerCurlChange?.(selectedHand, finger, parseFloat(e.target.value))}
                            className="flex-1 accent-secondary cursor-pointer h-1 rounded bg-white/10"
                          />
                          <span className="w-8 text-right text-secondary font-semibold">{curlVal}%</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {activeTab === "cue" && (
                <section className="space-y-2">
                  <div className="flex items-center justify-between">
                    <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-slate-400">LLM Prompt Cue</p>
                    <span className="rounded-full bg-white/5 px-2 py-0.5 font-mono text-[8px] text-slate-300 truncate max-w-[120px]">
                      {lastCue}
                    </span>
                  </div>
                  <textarea
                    value={cue}
                    onChange={(event) => setCue(event.target.value)}
                    rows={3}
                    spellCheck={false}
                    className="w-full resize-none rounded-xl border border-white/10 bg-black/40 px-3 py-2 font-mono text-xs leading-relaxed text-slate-200 outline-none transition placeholder:text-slate-600 focus:border-secondary/50"
                    placeholder='{"emotion":"sad","gesture":"walk","audio_url":"..."}'
                  />
                  <button
                    className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-secondary via-fuchsia-600 to-secondary px-3 py-2 font-mono text-[10px] font-semibold uppercase tracking-wider text-white transition hover:brightness-110 shadow-[0_0_15px_hsl(var(--glow-purple)/0.3)]"
                    onClick={applyCue}
                  >
                    <Sparkles className="h-3.5 w-3.5" /> Execute Cue
                  </button>
                </section>
              )}

              {activeTab === "wardrobe" && (
                <section className="space-y-2.5">
                  <div className="flex items-center justify-between">
                    <p className="flex items-center gap-1 font-mono text-[10px] uppercase tracking-[0.14em] text-slate-400">
                      <Shirt className="h-3.5 w-3.5" /> Wardrobe Selection
                    </p>
                    <button
                      className="flex items-center gap-1 text-[10px] font-mono text-secondary hover:underline"
                      onClick={() => uploadRef.current?.click()}
                    >
                      <Upload className="h-3 w-3" /> Load VRM
                    </button>
                    <input ref={uploadRef} onChange={handleVRMUpload} type="file" accept=".vrm,model/gltf-binary" className="hidden" />
                  </div>

                  <div className="space-y-1.5">
                    {AVATAR_WARDROBE.map((item) => (
                      <button
                        key={item.id}
                        onClick={() => onWardrobeChange(item)}
                        className={`flex w-full items-center gap-2.5 rounded-xl border p-2 text-left transition ${
                          activeWardrobe.id === item.id
                            ? "border-secondary/50 bg-secondary/15 shadow-[0_0_12px_hsl(var(--glow-purple)/0.25)]"
                            : "border-white/5 bg-white/[0.02] hover:border-white/15"
                        }`}
                      >
                        <span className="h-6 w-1 rounded-full shrink-0" style={{ background: item.accent }} />
                        <span className="min-w-0 flex-1">
                          <span className="block truncate font-mono text-[11px] text-slate-100 font-semibold">{item.name}</span>
                          <span className="block truncate text-[9px] text-slate-400">{item.description}</span>
                        </span>
                        {activeWardrobe.id === item.id && <Activity className="h-3.5 w-3.5 text-emerald-300 shrink-0" />}
                      </button>
                    ))}
                    {activeWardrobe.source === "local" && (
                      <div className="flex items-center gap-2.5 rounded-xl border border-secondary/40 bg-secondary/10 p-2">
                        <span className="h-6 w-1 rounded-full bg-secondary shrink-0" />
                        <span className="min-w-0 flex-1">
                          <span className="block truncate font-mono text-[11px] text-slate-100 font-semibold">{activeWardrobe.name}</span>
                          <span className="block text-[9px] text-slate-400">Local Custom Model</span>
                        </span>
                        <Activity className="h-3.5 w-3.5 text-emerald-300 shrink-0" />
                      </div>
                    )}
                  </div>
                </section>
              )}
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
};

export default AvatarDirector;
