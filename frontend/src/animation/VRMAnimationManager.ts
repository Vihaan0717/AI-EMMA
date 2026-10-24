/**
 * VRMAnimationManager — Single-file facade for the entire VRM animation system.
 *
 * Usage:
 *   import { VRMAnimationManager } from '@/animation/VRMAnimationManager';
 *
 *   const manager = new VRMAnimationManager();
 *   manager.attach(vrm);
 *
 *   // Simple API
 *   manager.playAction('wave');
 *   manager.setEmotion('thinking');
 *   manager.setPosture('seiza');
 *   manager.speakVowel('a');
 *   manager.setLookAt(0.5, -0.2);
 *   manager.setExertion(0.7);
 *
 *   // Call every frame
 *   manager.update(delta);
 */

import * as THREE from 'three';
import { VRM, VRMHumanBoneName, VRMExpressionPresetName } from '@pixiv/three-vrm';
import { POSE_LIBRARY, ALL_BONE_NAMES, ARM_REST_DEFAULTS } from './poses';
import { getEmotionModifiers } from './emotionModifiers';
import { computeBreathing } from './breathing';
import { EyeController } from './eyeController';
import { LipSyncController } from './lipSync';
import { initializeSpringBones, updateSpringBones } from './springBoneDamper';
import type { AvatarFeatures } from '@/lib/avatar';

// ── Re-export types so consumers only need this one file ────────────────
export type { AnimationAPI, PoseDefinition, EmotionModifiers } from './types';
export type { EmotionType, PoseType, Vowel } from './types';

// ── Constants ───────────────────────────────────────────────────────────
const TRANSITION_SPEED = 3.0; // Responsive, smooth crossfade

// ── Helpers ─────────────────────────────────────────────────────────────
const BONE_NAME_ALIASES: Record<string, string> = {
  leftThumbIntermediate: 'leftThumbProximal',
  leftThumbProximal: 'leftThumbMetacarpal',
  rightThumbIntermediate: 'rightThumbProximal',
  rightThumbProximal: 'rightThumbMetacarpal',
};

function getVRMBone(vrm: VRM, name: string): THREE.Object3D | null {
  const primary = vrm.humanoid?.getNormalizedBoneNode(name as VRMHumanBoneName)
    ?? vrm.humanoid?.getRawBoneNode(name as VRMHumanBoneName);
  if (primary) return primary;

  const alias = BONE_NAME_ALIASES[name];
  if (alias) {
    return vrm.humanoid?.getNormalizedBoneNode(alias as VRMHumanBoneName)
      ?? vrm.humanoid?.getRawBoneNode(alias as VRMHumanBoneName)
      ?? null;
  }
  return null;
}

const POSE_EXERTION: Partial<Record<string, number>> = {
  run: 0.7, walk: 0.3, dance: 0.5, jump: 0.8, cry: 0.3, peekaboo: 0.2, cheer: 0.4,
};

const POSE_AUTO_EMOTION: Partial<Record<string, string>> = {
  think: 'thinking', cry: 'sad_severe',
  hug_self: 'cold', gasp: 'surprised', peace_sign: 'happy',
  peekaboo: 'surprised', cheer: 'happy', clap: 'happy',
  nod: 'happy', disagree: 'serious', confusion: 'surprised',
  reassure: 'relaxed', listen: 'relaxed',
};

export interface CompoundExpression {
  /** Target weights for standard VRM expression presets (0.0 to 1.0) */
  presets: Record<string, number>;
  /** Eyelid squint or asymmetric base blink (0.0 to 1.0) */
  eyelids?: { left: number; right: number };
  /** Eye gaze directional offset (x: yaw, y: pitch) */
  gaze?: { x: number; y: number };
  /** Optional mouth vowel blend (e.g. slight parted lips in surprise or thinking) */
  mouthViseme?: { viseme: string; weight: number };
}

export const COMPOUND_EMOTIONS: Record<string, CompoundExpression> = {
  neutral: {
    presets: { neutral: 1.0, happy: 0, angry: 0, sad: 0, surprised: 0, relaxed: 0 },
    eyelids: { left: 0, right: 0 },
    gaze: { x: 0, y: 0 },
  },
  happy: {
    presets: { happy: 0.85, relaxed: 0.20, neutral: 0 },
    eyelids: { left: 0, right: 0 },
    gaze: { x: 0, y: 0.05 },
  },
  thinking: {
    // Cognitive search: relaxed mouth with slight pursed lips, quizzical eyes, looking up-left
    presets: { relaxed: 0.35, happy: 0.05, neutral: 0.3 },
    eyelids: { left: 0.15, right: 0.30 }, // Asymmetric quizzical squint
    gaze: { x: -0.22, y: 0.30 }, // Eyes glance upward & to side
    mouthViseme: { viseme: 'ou', weight: 0.08 },
  },
  surprised: {
    // Wide open eyes, lifted brows, slightly parted lips
    presets: { surprised: 0.95, relaxed: 0, neutral: 0 },
    eyelids: { left: 0, right: 0 },
    gaze: { x: 0, y: 0.12 },
    mouthViseme: { viseme: 'aa', weight: 0.18 },
  },
  sad: {
    presets: { sad: 0.85, neutral: 0 },
    eyelids: { left: 0.15, right: 0.15 },
    gaze: { x: 0, y: -0.28 },
  },
  sad_mild: {
    presets: { sad: 0.40, neutral: 0.5 },
    eyelids: { left: 0.08, right: 0.08 },
    gaze: { x: 0, y: -0.15 },
  },
  sad_moderate: {
    presets: { sad: 0.70, neutral: 0.2 },
    eyelids: { left: 0.15, right: 0.15 },
    gaze: { x: 0, y: -0.25 },
  },
  sad_severe: {
    presets: { sad: 1.0, neutral: 0 },
    eyelids: { left: 0.30, right: 0.30 },
    gaze: { x: 0, y: -0.38 },
    mouthViseme: { viseme: 'aa', weight: 0.12 },
  },
  angry: {
    presets: { angry: 0.90, neutral: 0 },
    eyelids: { left: 0.12, right: 0.12 },
    gaze: { x: 0, y: 0 },
  },
  relaxed: {
    presets: { relaxed: 0.85, happy: 0.20, neutral: 0 },
    eyelids: { left: 0.25, right: 0.25 }, // Serene half-lidded eyes
    gaze: { x: 0, y: -0.08 },
  },
  wink: {
    // Playful right eye closed, warm smile, left eye sparkling
    presets: { happy: 0.80, relaxed: 0.25, neutral: 0 },
    eyelids: { left: 0.0, right: 1.0 },
    gaze: { x: 0, y: 0.04 },
  },
  smug: {
    // Confident smirk, narrow sly eyes, tilted chin
    presets: { happy: 0.45, relaxed: 0.35, angry: 0.10, neutral: 0 },
    eyelids: { left: 0.22, right: 0.15 },
    gaze: { x: 0.08, y: 0.12 },
  },
  shy: {
    // Modest smile, bashful downward glance
    presets: { happy: 0.40, relaxed: 0.25, neutral: 0.3 },
    eyelids: { left: 0.15, right: 0.15 },
    gaze: { x: 0.18, y: -0.32 },
  },
  serious: {
    presets: { angry: 0.30, neutral: 0.70 },
    eyelids: { left: 0.14, right: 0.14 },
    gaze: { x: 0, y: 0 },
  },
  fever: {
    presets: { sad: 0.35, relaxed: 0.25, neutral: 0 },
    eyelids: { left: 0.55, right: 0.55 },
    gaze: { x: 0, y: -0.20 },
  },
  cold: {
    presets: { sad: 0.45, neutral: 0 },
    eyelids: { left: 0.35, right: 0.35 },
    gaze: { x: 0, y: -0.15 },
  },
};

export function setVRMExpression(vrm: VRM, name: string, value: number): void {
  if (!vrm.expressionManager) return;
  if (vrm.expressionManager.getExpression(name)) {
    vrm.expressionManager.setValue(name, value);
    return;
  }
  const lower = name.toLowerCase();
  for (const expr of vrm.expressionManager.expressions) {
    if (expr.expressionName.toLowerCase() === lower) {
      vrm.expressionManager.setValue(expr.expressionName, value);
      return;
    }
  }
}

const STATIC_POSES = new Set(['idle', 'sit', 'seiza', 'agura', 'think', 'hug_self', 'listen', 'reassure']);

export type HandPoseType = 'relaxed' | 'fist' | 'point' | 'peace' | 'open_palm' | 'thumbs_up' | 'ok_sign' | 'pinch';

export const HAND_POSE_PRESETS: Record<HandPoseType, Record<string, number>> = {
  relaxed: { thumb: 0.15, index: 0.25, middle: 0.28, ring: 0.32, little: 0.35 },
  fist: { thumb: 0.95, index: 1.0, middle: 1.0, ring: 1.0, little: 1.0 },
  point: { thumb: 0.85, index: 0.0, middle: 1.0, ring: 1.0, little: 1.0 },
  peace: { thumb: 0.85, index: 0.0, middle: 0.0, ring: 1.0, little: 1.0 },
  open_palm: { thumb: 0.0, index: 0.0, middle: 0.0, ring: 0.0, little: 0.0 },
  thumbs_up: { thumb: -0.2, index: 1.0, middle: 1.0, ring: 1.0, little: 1.0 },
  ok_sign: { thumb: 0.65, index: 0.7, middle: 0.05, ring: 0.1, little: 0.15 },
  pinch: { thumb: 0.6, index: 0.6, middle: 0.3, ring: 0.5, little: 0.7 },
};

function computeFingerBoneEuler(boneName: string, curls: Record<string, number>): { x: number; y: number; z: number } | null {
  const isLeft = boneName.startsWith('left');
  const sign = isLeft ? 1 : -1;

  if (boneName.includes('Thumb')) {
    const curl = curls.thumb ?? 0.15;
    if (boneName.includes('Metacarpal')) {
      return { x: curl * 0.25, y: sign * curl * 0.45, z: sign * curl * 0.3 };
    }
    if (boneName.includes('Proximal')) {
      return { x: curl * 0.35, y: sign * curl * 0.2, z: sign * curl * 0.1 };
    }
    if (boneName.includes('Distal') || boneName.includes('Intermediate')) {
      return { x: curl * 0.6, y: 0, z: 0 };
    }
  }

  let fingerName = '';
  if (boneName.includes('Index')) fingerName = 'index';
  else if (boneName.includes('Middle')) fingerName = 'middle';
  else if (boneName.includes('Ring')) fingerName = 'ring';
  else if (boneName.includes('Little')) fingerName = 'little';

  if (!fingerName) return null;
  const curl = curls[fingerName] ?? 0.25;

  if (boneName.includes('Proximal')) {
    let splay = 0;
    if (fingerName === 'index') {
      splay = (curl < 0.1 && (curls.middle ?? 1) < 0.1) ? -sign * 0.16 : -sign * 0.05;
    }
    if (fingerName === 'middle') {
      splay = (curl < 0.1 && (curls.index ?? 1) < 0.1) ? sign * 0.12 : 0;
    }
    if (fingerName === 'ring') splay = sign * 0.03;
    if (fingerName === 'little') splay = sign * 0.08;
    return { x: curl * 1.35, y: 0, z: splay };
  }
  if (boneName.includes('Intermediate')) {
    return { x: curl * 1.4, y: 0, z: 0 };
  }
  if (boneName.includes('Distal')) {
    return { x: curl * 0.9, y: 0, z: 0 };
  }
  return null;
}

// ═══════════════════════════════════════════════════════════════════════
// ██  VRMAnimationManager  ██
// ═══════════════════════════════════════════════════════════════════════

export class VRMAnimationManager {
  private vrm: VRM | null = null;
  private currentPose: string = 'idle';
  private currentEmotion: string = 'neutral';
  private exertion = 0;
  private phase = 0;
  private transitionProgress = 1;
  private features: AvatarFeatures = {
    breathing: true,
    hairPhysics: true,
    eyeTracking: true,
    lipSync: true,
  };

  public readonly eye = new EyeController();
  public readonly lip = new LipSyncController();

  // Track the current LookAt coordinates to apply to head/neck
  private currentHeadTarget = { yaw: 0, pitch: 0 };
  private initialHipsPosition: THREE.Vector3 | null = null;
  private isVrm0: boolean = false;

  // Granular finger curls and hand pose state
  private fingerCurls: { left: Record<string, number>; right: Record<string, number> } = {
    left: { ...HAND_POSE_PRESETS.relaxed },
    right: { ...HAND_POSE_PRESETS.relaxed },
  };
  private activeHandPose: { left: string; right: string } = { left: 'relaxed', right: 'relaxed' };
  private boneOverrides: Map<string, { euler: { x: number; y: number; z: number }; weight: number }> = new Map();

  // ── Lifecycle ─────────────────────────────────────────────────────────

  /** Attach a loaded VRM model. Call once after loading. */
  attach(vrm: VRM): void {
    this.vrm = vrm;
    this.isVrm0 = (vrm.meta as any)?.metaVersion === '0';
    const hipsNode = getVRMBone(vrm, 'hips');
    if (hipsNode) {
      this.initialHipsPosition = hipsNode.position.clone();
    }
    initializeSpringBones(vrm);
  }

  /** Detach the current model. */
  detach(): void {
    this.vrm = null;
    this.initialHipsPosition = null;
    this.boneOverrides.clear();
  }

  /** Whether a VRM is currently attached. */
  get isAttached(): boolean {
    return this.vrm !== null;
  }

  /** Set finger articulation by hand pose preset */
  setHandPose(hand: 'left' | 'right' | 'both', pose: HandPoseType): void {
    const preset = HAND_POSE_PRESETS[pose] ?? HAND_POSE_PRESETS.relaxed;
    if (hand === 'left' || hand === 'both') {
      this.fingerCurls.left = { ...preset };
      this.activeHandPose.left = pose;
    }
    if (hand === 'right' || hand === 'both') {
      this.fingerCurls.right = { ...preset };
      this.activeHandPose.right = pose;
    }
  }

  /** Set individual finger curl amount (0.0 to 1.0) */
  setFingerCurl(hand: 'left' | 'right' | 'both', finger: string, amount: number): void {
    const clamped = Math.max(0, Math.min(1, amount));
    const fingers = finger === 'all' ? ['thumb', 'index', 'middle', 'ring', 'little'] : [finger];
    if (hand === 'left' || hand === 'both') {
      fingers.forEach(f => { this.fingerCurls.left[f] = clamped; });
    }
    if (hand === 'right' || hand === 'both') {
      fingers.forEach(f => { this.fingerCurls.right[f] = clamped; });
    }
  }

  /** Set fine-grained Euler angle override on any bone */
  setBoneOverride(boneName: string, euler: { x?: number; y?: number; z?: number }, weight = 1.0): void {
    this.boneOverrides.set(boneName, {
      euler: { x: euler.x ?? 0, y: euler.y ?? 0, z: euler.z ?? 0 },
      weight: Math.max(0, Math.min(1, weight)),
    });
  }

  /** Clear all bone overrides */
  clearBoneOverrides(): void {
    this.boneOverrides.clear();
  }

  // ── Public API ────────────────────────────────────────────────────────

  /**
   * Play an action/pose.
   * Actions: 'idle' | 'walk' | 'run' | 'jump' | 'sit' | 'seiza' | 'agura'
   *        | 'dance' | 'wave' | 'bow' | 'think' | 'cry'
   *        | 'hug_self' | 'gasp' | 'peace_sign' | 'explain' | 'cheer' | 'clap'
   */
  playAction(action: string): void {
    if (action === this.currentPose) return;
    this.transitionProgress = 0;
    this.currentPose = action;
    this.exertion = POSE_EXERTION[action] ?? 0;
    this.clearBoneOverrides();

    const autoEmotion = POSE_AUTO_EMOTION[action];
    if (autoEmotion) this.setEmotion(autoEmotion);

    // Auto-configure biomechanical hand poses for specific movement actions
    if (action === 'run') {
      this.setHandPose('both', 'fist');
    } else if (action === 'peace_sign') {
      this.setHandPose('right', 'peace');
      this.setHandPose('left', 'relaxed');
    } else if (action === 'point') {
      this.setHandPose('right', 'point');
      this.setHandPose('left', 'relaxed');
    } else if (action === 'think') {
      this.setHandPose('right', 'point');
      this.setHandPose('left', 'relaxed');
    } else if (action === 'wave') {
      this.setHandPose('right', 'open_palm');
      this.setHandPose('left', 'relaxed');
    } else if (action === 'cheer' || action === 'clap' || action === 'explain') {
      this.setHandPose('both', 'relaxed');
    } else if (action === 'idle' || action === 'walk') {
      this.setHandPose('both', 'relaxed');
    }
  }

  public emotionWeight: number = 1.0;
  private targetExpressions: Record<string, number> = {};
  private currentExpressions: Record<string, number> = {};
  private microExpressionTimer: number = 0;
  private nextMicroExpression: number = 4.0;
  private microHappy: number = 0;

  /**
   * Set the character's emotional expression with optional intensity weight (0.0 to 1.0).
   * Emotions: 'neutral' | 'happy' | 'thinking' | 'surprised' | 'sad' | 'angry'
   *         | 'wink' | 'smug' | 'shy' | 'relaxed' | 'serious'
   *         | 'sad_mild' | 'sad_moderate' | 'sad_severe' | 'fever' | 'cold'
   */
  setEmotion(emotion: string, weight = 1.0): void {
    this.currentEmotion = emotion;
    this.emotionWeight = Math.max(0, Math.min(1, weight));
    if (!this.vrm?.expressionManager) return;

    const compound = COMPOUND_EMOTIONS[emotion] ?? COMPOUND_EMOTIONS.neutral;

    // Reset current target weights
    for (const key of Object.keys(this.targetExpressions)) {
      this.targetExpressions[key] = 0;
    }

    // Set new compound targets scaled by emotionWeight
    for (const [preset, val] of Object.entries(compound.presets)) {
      this.targetExpressions[preset] = val * this.emotionWeight;
      if (this.currentExpressions[preset] === undefined) {
        this.currentExpressions[preset] = 0;
      }
    }

    // Configure base eyelid state on EyeController (for wink / squint)
    const leftEyelid = (compound.eyelids?.left ?? 0) * this.emotionWeight;
    const rightEyelid = (compound.eyelids?.right ?? 0) * this.emotionWeight;
    this.eye.setBaseEyelids(leftEyelid, rightEyelid);

    // Configure gaze direction offset
    const gazeX = (compound.gaze?.x ?? 0) * this.emotionWeight;
    const gazeY = (compound.gaze?.y ?? 0) * this.emotionWeight;
    this.eye.setGazeOffset(gazeX, gazeY);

    // Set mouth viseme if specified
    if (compound.mouthViseme && this.emotionWeight > 0.1) {
      this.targetExpressions[compound.mouthViseme.viseme] = compound.mouthViseme.weight * this.emotionWeight;
    }
  }

  /** Set a seated/standing posture (convenience alias for playAction). */
  setPosture(posture: string): void {
    this.playAction(posture);
  }

  /** Set exertion level (0-1). Affects breathing rate and amplitude. */
  setExertion(level: number): void {
    this.exertion = Math.max(0, Math.min(1, level));
  }

  /** Enable or disable independently controllable real-time performance layers. */
  setFeatures(features: AvatarFeatures): void {
    this.features = { ...features };
  }

  /** Trigger a lip-sync vowel: 'a' | 'i' | 'u' | 'e' | 'o' | 'silent' */
  speakVowel(vowel: string): void {
    this.lip.setVowel(vowel as any);
  }

  /** Set eye-tracking and head tracking targets. Values are normalized via yaw/pitch. */
  setLookAt(headYaw: number, headPitch: number, eyeYaw: number, eyePitch: number): void {
    this.eye.setLookAt(eyeYaw, eyePitch);
    this.currentHeadTarget = { yaw: headYaw, pitch: headPitch };
  }

  /** Override blink amount (0-1). */
  setBlink(v: number): void {
    this.eye.setBlinkOverride(v);
  }

  /** Set exact blink signals tracked by backend */
  setBlinkExact(left?: number, right?: number): void {
    this.eye.setBlinkExact(left, right);
  }

  /** Set mouth-open amount (0-1). */
  setMouthOpen(v: number): void {
    this.lip.setManualAmplitude(v);
  }

  // ── Getters ───────────────────────────────────────────────────────────

  get action(): string { return this.currentPose; }
  get emotion(): string { return this.currentEmotion; }

  // ── Frame update ──────────────────────────────────────────────────────

  /** Call every frame with delta time in seconds. */
  update(delta: number): void {
    if (!this.vrm) return;

    // Clamp delta to prevent massive physics explosions on frame drops
    const safeDelta = Math.min(delta, 0.033);

    this.phase += safeDelta;

    // Transition progress
    const isTransitioning = this.transitionProgress < 1;
    if (isTransitioning) {
      this.transitionProgress = Math.min(1, this.transitionProgress + safeDelta * TRANSITION_SPEED);
    }

    // Spring bone physics
    if (this.features.hairPhysics && delta < 0.05) {
      updateSpringBones(this.vrm, safeDelta, isTransitioning, STATIC_POSES.has(this.currentPose));
    }

    // Emotion modifiers
    const emotionMod = getEmotionModifiers(this.currentEmotion as any);

    // Breathing
    const breathing = this.features.breathing ? computeBreathing({
      phase: this.phase,
      exertion: this.exertion,
      emotionScale: emotionMod.breatheScale,
    }) : {};

    // Pose definition from POSE_LIBRARY
    const poseDef = (POSE_LIBRARY as any)[this.currentPose] ?? POSE_LIBRARY.idle;

    // Per-bone update
    ALL_BONE_NAMES.forEach(boneName => {
      const node = getVRMBone(this.vrm!, boneName);
      if (!node) return;

      // Resolve euler:
      // 1. Check if finger bone and calculate from granular fingerCurls
      // 2. Pose definition -> arm/finger defaults -> zero
      const isLeft = boneName.startsWith('left');
      const curls = isLeft ? this.fingerCurls.left : this.fingerCurls.right;
      const fingerEuler = computeFingerBoneEuler(boneName, curls);

      let ex: number, ey: number, ez: number;

      if (fingerEuler) {
        ex = fingerEuler.x;
        ey = fingerEuler.y;
        ez = fingerEuler.z;
      } else {
        const poseFn = poseDef[boneName] ?? (ARM_REST_DEFAULTS as any)[boneName];
        const euler = poseFn ? poseFn(this.phase) : { x: 0, y: 0, z: 0 };
        ex = euler.x;
        ey = euler.y;
        ez = euler.z;
      }


      // Emotion modifiers scaled by emotionWeight
      const weight = this.emotionWeight;
      if (boneName === 'spine') ex += emotionMod.spineForwardLean * weight;
      if (boneName === 'head') {
        ex += emotionMod.headTilt * weight;
        if (emotionMod.headRoll) ez += emotionMod.headRoll * weight;
        if (emotionMod.headYaw) ey += emotionMod.headYaw * weight;
      }
      if (boneName === 'leftShoulder' || boneName === 'rightShoulder') {
        ex += emotionMod.shoulderHeightOffset * weight;
      }

      // Breathing additive to spine and chest
      const breathKey = boneName as keyof typeof breathing;
      if (breathKey in breathing) {
        const b = breathing[breathKey] as { x: number; y?: number; z: number };
        ex += b.x;
        if ('y' in b && b.y !== undefined) ey += b.y;
        ez += b.z;
      }

      // Apply Head and Neck tracking via Euler interpolation
      if (boneName === 'head' || boneName === 'neck') {
        const rotationFactor = boneName === 'head' ? 0.85 : 0.45;
        const yawLimit = Math.PI / 4;
        const targetYaw = -Math.max(-2, Math.min(2, this.currentHeadTarget.yaw)) * yawLimit * rotationFactor;
        const pitchLimit = Math.PI / 6;
        const targetPitch = Math.max(-2, Math.min(2, this.currentHeadTarget.pitch)) * pitchLimit * rotationFactor;

        ey += targetYaw;
        ex -= targetPitch;
      }

      // Eye tracking
      if (boneName === 'leftEye' || boneName === 'rightEye') {
        const eyeYaw = -this.eye.currentX * 1.5;
        const eyePitch = -this.eye.currentY * 1.5;
        ey += eyeYaw;
        ex -= eyePitch;
      }

      // Bone override blending
      const override = this.boneOverrides.get(boneName);
      if (override && override.weight > 0) {
        ex = ex * (1 - override.weight) + override.euler.x * override.weight;
        ey = ey * (1 - override.weight) + override.euler.y * override.weight;
        ez = ez * (1 - override.weight) + override.euler.z * override.weight;
      }

      const isNativeAvaSitPose = this.currentPose === 'sit' || this.currentPose === 'seiza' || this.currentPose === 'agura';

      // Anatomical Elbow Hinge Normalizer:
      // Forearm bones in VRM normalized humanoid space extend longitudinally along local X.
      // Rotating around X produces zero forearm deflection (only axial twist).
      // Forward elbow hinge bending is around the local Y-axis.
      // (Native Ava sit poses already include explicit authored elbow hinge angles).
      if (!isNativeAvaSitPose && (boneName === 'leftLowerArm' || boneName === 'rightLowerArm')) {
        if (Math.abs(ex) > 0.01 && Math.abs(ey) < 0.01) {
          const flexion = ex; // negative angle authored in poses.ts (e.g. -0.85 to -1.6 rad)
          ey = boneName === 'leftLowerArm' ? flexion : -flexion;
          ex = 0;
        }
      }

      // Unified Biomechanical Humanoid Retargeter:
      // Canonical library poses are authored in standard humanoid space.
      // VRM 0.0 models (Ava Custom) have their scene root rotated by 180° around Y (Math.PI).
      // Ava's starting sit poses were authored natively in VRM 0.0 space;
      // for these, VRM 0.0 receives the authored angles directly without inversion.
      if (isNativeAvaSitPose) {
        if (!this.isVrm0) {
          ex = -ex;
          ez = -ez;
        }
      } else {
        if (this.isVrm0) {
          ex = -ex;
          // ey is invariant under Ry(180°) rotation and must NOT be negated
          ez = -ez;
        }
      }

      const targetQ = new THREE.Quaternion().setFromEuler(new THREE.Euler(ex, ey, ez));

      // Slerp factor for smooth organic transitions
      const slerpFactor = isTransitioning
        ? Math.min(1, safeDelta * TRANSITION_SPEED * 2.5)
        : (1.0 - Math.exp(-8 * safeDelta));

      node.quaternion.slerp(targetQ, slerpFactor);
    });

    // --- Dynamic Root/Hips Vertical & Lateral Translation (Bobbing / Sitting / Weight shift) ---
    const hipsNode = getVRMBone(this.vrm, 'hips');
    if (hipsNode && this.initialHipsPosition) {
      const hipsOffsetFn = poseDef.hipsOffset;
      const offset = hipsOffsetFn ? hipsOffsetFn(this.phase) : { x: 0, y: 0, z: 0 };
      const targetPos = new THREE.Vector3(
        this.initialHipsPosition.x + (this.isVrm0 ? -(offset.x ?? 0) : (offset.x ?? 0)),
        this.initialHipsPosition.y + (offset.y ?? 0),
        this.initialHipsPosition.z + (this.isVrm0 ? -(offset.z ?? 0) : (offset.z ?? 0))
      );
      const posLerpFactor = isTransitioning
        ? Math.min(1, safeDelta * TRANSITION_SPEED * 2.5)
        : (1.0 - Math.exp(-12 * safeDelta));
      hipsNode.position.lerp(targetPos, posLerpFactor);
    }

    // --- Smooth Compound Expression Lerping ---
    if (this.vrm.expressionManager) {
      const lerpFactor = Math.min(1, safeDelta * 6.5);

      // Micro-expressions: organic, subtle spontaneous twitches during idle
      if (this.currentPose === 'idle' && this.currentEmotion === 'neutral') {
        this.microExpressionTimer += safeDelta;
        if (this.microExpressionTimer >= this.nextMicroExpression) {
          this.microHappy = 0.08 + Math.random() * 0.06;
          this.microExpressionTimer = 0;
          this.nextMicroExpression = 4.0 + Math.random() * 4.0;
        }
        if (this.microHappy > 0) {
          this.microHappy = Math.max(0, this.microHappy - safeDelta * 0.2);
        }
      } else {
        this.microHappy = 0;
      }

      for (const [exprName, target] of Object.entries(this.targetExpressions)) {
        let finalTarget = target;
        if (exprName === 'happy' && this.microHappy > 0) {
          finalTarget = Math.max(finalTarget, this.microHappy);
        }

        let current = this.currentExpressions[exprName] ?? 0;
        current += (finalTarget - current) * lerpFactor;
        if (Math.abs(current) < 0.001) current = 0;
        this.currentExpressions[exprName] = current;
        setVRMExpression(this.vrm, exprName, current);
      }
    }

    // Sub-systems (eyes, lips, spring bones)
    if (this.features.eyeTracking) {
      this.eye.update(this.vrm, safeDelta);
    }
    if (this.features.lipSync) {
      this.lip.update(this.vrm, safeDelta);
    } else {
      this.lip.setManualAmplitude(0);
      this.lip.update(this.vrm, safeDelta);
    }
    this.vrm.update(safeDelta);
  }
}
