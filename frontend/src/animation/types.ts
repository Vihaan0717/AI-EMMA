export type EmotionType =
  | 'neutral' | 'happy' | 'angry' | 'sad' | 'surprised'
  | 'relaxed' | 'thinking' | 'serious'
  | 'wink' | 'smug' | 'shy'
  | 'sad_mild' | 'sad_moderate' | 'sad_severe'
  | 'fever' | 'cold';

export type PoseType =
  | 'idle' | 'walk' | 'run' | 'jump'
  | 'sit' | 'seiza' | 'agura' | 'afk_idle'
  | 'dance' | 'wave' | 'bow'
  | 'think' | 'cry' | 'hug_self'
  | 'gasp' | 'peace_sign' | 'peekaboo'
  | 'explain' | 'cheer' | 'clap'
  | 'nod' | 'disagree' | 'point' | 'listen' | 'confusion' | 'reassure'
  | 'count_1' | 'count_2' | 'count_3' | 'count_4' | 'count_5';

export type Vowel = 'a' | 'i' | 'u' | 'e' | 'o' | 'silent';

export interface AnimationAPI {
  play: (pose: PoseType) => void;
  setEmotion: (emotion: EmotionType, weight?: number) => void;
  setExertion: (level: number) => void; // 0-1
  speakVowel: (vowel: Vowel) => void;
  setLookAt: (x: number, y: number) => void;
  setBlink: (v: number) => void;
  setMouthOpen: (v: number) => void;
}

export interface PoseDefinition {
  hipsOffset?: (phase: number) => { x: number; y: number; z: number };
  [boneName: string]: any;
}

export interface EmotionModifiers {
  shoulderHeightOffset: number;
  spineForwardLean: number;
  headTilt: number;
  headRoll?: number;
  headYaw?: number;
  /** Modifier for breathing amplitude */
  breatheScale?: number;
  /** 0-1: controls half-closed eyes for exhaustion/fever */
  eyeSquint?: number;
  /** Offset for eye gaze target */
  gazeOffset?: { x: number; y: number };
}
