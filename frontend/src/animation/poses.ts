import { PoseDefinition, PoseType } from './types';

// Each pose returns Euler angles (x, y, z) for each bone as a function of phase (seconds).
// ALL rotations are in LOCAL SPACE relative to parent bone's rest orientation.
// In VRM humanoid bind pose (T-pose):
//   - Left arm points along +X. Rotating around Z by -1.32 rad (~-76°) brings it down to the side.
//   - Right arm points along -X. Rotating around Z by +1.32 rad (~+76°) brings it down to the side.
//   - Lower arms bend at elbow around -X (flexion).
//   - Fingers curl around X axis (positive X curls inward toward palm).

const staticPose = (x = 0, y = 0, z = 0) => (_phase: number) => ({ x, y, z });

// ─── Natural Resting Hand & Finger Pose ──────────────────────────────────
// Returns subtle natural flexion so hands never look like stiff wooden boards.
function makeNaturalFingers(side: 'left' | 'right', curl = 1.0): Record<string, (p: number) => { x: number; y: number; z: number }> {
  const isLeft = side === 'left';
  const ySign = isLeft ? 1 : -1;

  return {
    // Thumb: natural CMC opposition & gentle MCP/IP curl
    [`${side}ThumbMetacarpal`]: staticPose(0.12 * curl, 0.14 * ySign * curl, 0.10 * ySign * curl),
    [`${side}ThumbProximal`]: staticPose(0.20 * curl, 0, 0),
    [`${side}ThumbIntermediate`]: staticPose(0.20 * curl, 0, 0), // fallback alias
    [`${side}ThumbDistal`]: staticPose(0.16 * curl, 0, 0),

    // Index: relaxed inward curl
    [`${side}IndexProximal`]: staticPose(0.20 * curl, 0, 0),
    [`${side}IndexIntermediate`]: staticPose(0.30 * curl, 0, 0),
    [`${side}IndexDistal`]: staticPose(0.18 * curl, 0, 0),

    // Middle: slightly deeper curl following hand arch
    [`${side}MiddleProximal`]: staticPose(0.24 * curl, 0, 0),
    [`${side}MiddleIntermediate`]: staticPose(0.34 * curl, 0, 0),
    [`${side}MiddleDistal`]: staticPose(0.20 * curl, 0, 0),

    // Ring: natural curl
    [`${side}RingProximal`]: staticPose(0.28 * curl, 0, 0),
    [`${side}RingIntermediate`]: staticPose(0.38 * curl, 0, 0),
    [`${side}RingDistal`]: staticPose(0.22 * curl, 0, 0),

    // Little: deepest resting curl
    [`${side}LittleProximal`]: staticPose(0.32 * curl, 0, 0),
    [`${side}LittleIntermediate`]: staticPose(0.42 * curl, 0, 0),
    [`${side}LittleDistal`]: staticPose(0.25 * curl, 0, 0),
  };
}

const LEFT_RELAXED_FINGERS = makeNaturalFingers('left', 1.0);
const RIGHT_RELAXED_FINGERS = makeNaturalFingers('right', 1.0);

// ─── Resting Arm Defaults (Anatomically pure hinge elbow & untwisted wrist) ───
export const ARM_REST_DEFAULTS = {
  leftUpperArm: staticPose(0.08, 0.04, -1.30),
  rightUpperArm: staticPose(0.08, -0.04, 1.30),
  leftLowerArm: staticPose(-0.16, 0, 0),  // pure hinge elbow flexion, zero twist
  rightLowerArm: staticPose(-0.16, 0, 0), // pure hinge elbow flexion, zero twist
  leftHand: staticPose(0, 0, 0),          // naturally continues forearm line
  rightHand: staticPose(0, 0, 0),         // naturally continues forearm line
  leftShoulder: staticPose(0, 0, 0),
  rightShoulder: staticPose(0, 0, 0),
  ...LEFT_RELAXED_FINGERS,
  ...RIGHT_RELAXED_FINGERS,
};

// ─── IDLE: Natural breathing, subtle weight shifts, relaxed posture ───────
const idlePose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  spine: (p) => ({
    x: Math.sin(p * 1.4) * 0.012 + Math.sin(p * 0.7) * 0.015,
    y: Math.sin(p * 0.5) * 0.01,
    z: Math.sin(p * 0.8) * 0.008,
  }),
  chest: (p) => ({
    x: Math.sin(p * 1.4) * 0.018,
    y: 0,
    z: Math.sin(p * 0.8) * 0.006,
  }),
  upperChest: (p) => ({
    x: Math.sin(p * 1.4) * 0.014,
    y: 0,
    z: 0,
  }),
  head: (p) => ({
    x: Math.sin(p * 0.6) * 0.012,
    y: Math.sin(p * 0.35) * 0.015,
    z: Math.sin(p * 0.5) * 0.008,
  }),
  // Arms hang naturally at sides with subtle breathing response
  leftUpperArm: (p) => ({
    x: 0.08 + Math.sin(p * 1.4) * 0.01,
    y: 0.05,
    z: -1.32 + Math.sin(p * 1.4) * 0.012,
  }),
  rightUpperArm: (p) => ({
    x: 0.08 + Math.sin(p * 1.4) * 0.01,
    y: -0.05,
    z: 1.32 - Math.sin(p * 1.4) * 0.012,
  }),
  leftLowerArm: staticPose(-0.22, 0, 0),   // pure hinge, zero twist
  rightLowerArm: staticPose(-0.22, 0, 0),  // pure hinge, zero twist
  leftHand: staticPose(0, 0, 0),            // neutral aligned with forearm
  rightHand: staticPose(0, 0, 0),           // neutral aligned with forearm
};

// ─── WAVE: Warm, friendly greeting gesture ──────────────────────────────
const wavePose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  // Left arm rests comfortably at side
  leftUpperArm: staticPose(0.08, 0.04, -1.30),
  leftLowerArm: staticPose(-0.16, 0, 0),
  leftHand: staticPose(0, 0, 0),
  ...LEFT_RELAXED_FINGERS,

  // Torso leans slightly into the greeting with subtle rhythmic breathing
  spine: (p) => ({ x: 0.02, y: -0.04, z: -0.02 + Math.sin(p * 5.0) * 0.008 }),
  chest: staticPose(0.02, -0.02, -0.02),
  head: (p) => ({ x: -0.02, y: -0.04, z: 0.06 + Math.sin(p * 5.0) * 0.012 }),

  // Right arm raised cleanly with elbow close to torso, forearm upright beside cheek/ear
  rightShoulder: staticPose(-0.02, 0, 0.04),
  rightUpperArm: staticPose(-0.35, -0.22, 0.88),
  rightLowerArm: (p) => ({
    x: -2.05,
    y: Math.sin(p * 5.5) * 0.15,
    z: 0,
  }),
  // Open palm waving side-to-side at user with clear lateral wrist sweep
  rightHand: (p) => ({
    x: 0.12,
    y: 0.10,
    z: Math.sin(p * 5.5) * 0.25,
  }),
  ...makeNaturalFingers('right', 0.05), // Fully open friendly greeting palm
};

// ─── WALK: Professional Biomechanical Gait Cycle ─────────────────────────
// Full human gait cycle (cadence ~110 steps/min = ~1.85 Hz step rate, ~3.7 rad/s).
// Features: Pelvic list (trendelenburg drop), pelvic rotation, thoracic counter-rotation,
// heel-strike, mid-stance knee shock absorption, toe-off plantarflexion, and natural shoulder/arm opposition.
const walkPose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,

  // Root vertical bounce (double-bump per stride) and pelvic lateral shift
  hipsOffset: (p) => {
    const cycle = p * 3.8;
    return {
      x: Math.sin(cycle) * 0.018, // lateral weight shift over supporting leg
      y: -Math.abs(Math.sin(cycle)) * 0.025 + 0.008, // gentle vertical bounce
      z: 0,
    };
  },

  // Pelvis / Hips rotation: Yaw turns toward leading leg, Roll drops toward swing leg
  hips: (p) => {
    const cycle = p * 3.8;
    return {
      x: 0.03, // slight forward pelvic tilt
      y: Math.sin(cycle) * 0.06, // transverse pelvic rotation (~3-4 deg)
      z: Math.cos(cycle) * 0.035, // coronal pelvic list
    };
  },

  // Torso / Spine counter-rotation (shoulders twist opposite to hips to conserve angular momentum)
  spine: (p) => {
    const cycle = p * 3.8;
    return {
      x: -0.01,
      y: -Math.sin(cycle) * 0.045,
      z: -Math.cos(cycle) * 0.02,
    };
  },

  chest: (p) => {
    const cycle = p * 3.8;
    return {
      x: 0.01,
      y: -Math.sin(cycle) * 0.025,
      z: -Math.cos(cycle) * 0.01,
    };
  },

  head: (p) => {
    const cycle = p * 3.8;
    return {
      x: Math.sin(cycle * 2) * 0.01,
      y: Math.sin(cycle) * 0.015,
      z: 0,
    };
  },

  // Left Leg: Balanced natural human walking stride (gentle runway excursion)
  leftUpperLeg: (p) => {
    const cycle = p * 3.8;
    const s = Math.sin(cycle);
    return {
      x: s * 0.18, // Gliding stride angle (~10 deg)
      y: -s * 0.02,
      z: 0.02, // Subtle stance width
    };
  },

  rightUpperLeg: (p) => {
    const cycle = p * 3.8;
    const s = -Math.sin(cycle);
    return {
      x: s * 0.18,
      y: -s * 0.02,
      z: -0.02,
    };
  },

  // Knee Flexion: Soft ground-skimming knee flexion, trailing push-off only
  leftLowerLeg: (p) => {
    const cycle = p * 3.8;
    const s = Math.sin(cycle);
    const pushOff = Math.max(0, -s) * 0.38;
    return {
      x: -pushOff,
      y: 0,
      z: 0,
    };
  },

  rightLowerLeg: (p) => {
    const cycle = p * 3.8;
    const s = -Math.sin(cycle);
    const pushOff = Math.max(0, -s) * 0.38;
    return {
      x: -pushOff,
      y: 0,
      z: 0,
    };
  },

  // Ankle / Feet (Gentle heel strike and toe-off, stays level near ground)
  leftFoot: (p) => {
    const cycle = p * 3.8;
    const s = Math.sin(cycle);
    // Subtle ankle flexion: +0.08 at heel strike, -0.22 at toe push-off
    const footAngle = s * 0.15 - 0.07;
    return {
      x: footAngle,
      y: 0,
      z: 0,
    };
  },

  rightFoot: (p) => {
    const cycle = p * 3.8;
    const s = -Math.sin(cycle);
    const footAngle = s * 0.15 - 0.07;
    return {
      x: footAngle,
      y: 0,
      z: 0,
    };
  },

  // Left Arm (Swings in counter-phase to Left Leg: when left leg swings back, left arm swings forward)
  leftUpperArm: (p) => {
    const cycle = p * 3.8;
    const armSwing = -Math.sin(cycle) * 0.28;
    return {
      x: armSwing + 0.06,
      y: 0.05,
      z: -1.30 + Math.abs(armSwing) * 0.04, // stays down beside torso
    };
  },

  rightUpperArm: (p) => {
    const cycle = p * 3.8;
    const armSwing = Math.sin(cycle) * 0.28;
    return {
      x: armSwing + 0.06,
      y: -0.05,
      z: 1.30 - Math.abs(armSwing) * 0.04,
    };
  },

  // Forearms flex slightly on forward swing as pure anatomical hinge
  leftLowerArm: (p) => {
    const cycle = p * 3.8;
    const forwardSwing = Math.max(0, -Math.sin(cycle));
    return {
      x: -0.16 - forwardSwing * 0.24,
      y: 0,
      z: 0,
    };
  },

  rightLowerArm: (p) => {
    const cycle = p * 3.8;
    const forwardSwing = Math.max(0, Math.sin(cycle));
    return {
      x: -0.16 - forwardSwing * 0.24,
      y: 0,
      z: 0,
    };
  },

  // Gentle relaxed wrist follow-through aligned with forearm axis
  leftHand: (p) => {
    const cycle = p * 3.8;
    return {
      x: -Math.cos(cycle) * 0.05,
      y: 0,
      z: 0,
    };
  },

  rightHand: (p) => {
    const cycle = p * 3.8;
    return {
      x: Math.cos(cycle) * 0.05,
      y: 0,
      z: 0,
    };
  },

  ...makeNaturalFingers('left', 0.65),
  ...makeNaturalFingers('right', 0.65),
};

// ─── RUN: Energetic, Athletic Jog ─────────────────────────────────────────
const runPose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,

  hipsOffset: (p) => {
    const cycle = p * 6.2;
    // Energetic flight bounce: lowest on foot strikes, rises during flight phase
    const bounce = Math.abs(Math.sin(cycle)) * 0.055 - 0.025;
    return {
      x: Math.sin(cycle) * 0.018,
      y: bounce,
      z: 0,
    };
  },

  hips: (p) => {
    const cycle = p * 6.2;
    return {
      x: 0.06, // Forward athletic pelvic tilt
      y: Math.sin(cycle) * 0.08, // Pelvic axial rotation
      z: Math.cos(cycle) * 0.035, // Subtle lateral pelvic list
    };
  },

  spine: (p) => {
    const cycle = p * 6.2;
    return {
      x: 0.06, // Natural forward spine curve (flexion)
      y: -Math.sin(cycle) * 0.06, // Torso counter-twist
      z: 0,
    };
  },

  chest: (p) => {
    const cycle = p * 6.2;
    return {
      x: 0.04, // Upper torso forward inclination
      y: -Math.sin(cycle) * 0.04,
      z: 0,
    };
  },

  head: (p) => {
    const cycle = p * 6.2;
    return {
      // Compensate for trunk lean so gaze stays forward at horizon
      x: -0.12 + Math.sin(cycle * 2) * 0.02,
      y: Math.sin(cycle) * 0.02,
      z: 0,
    };
  },

  // Running leg strides: balanced athletic jog excursion
  leftUpperLeg: (p) => {
    const cycle = p * 6.2;
    const s = Math.sin(cycle);
    return {
      x: s * 0.22 + 0.02,
      y: 0,
      z: 0.03,
    };
  },
  rightUpperLeg: (p) => {
    const cycle = p * 6.2;
    const s = -Math.sin(cycle);
    return {
      x: s * 0.22 + 0.02,
      y: 0,
      z: -0.03,
    };
  },

  // Biomechanical running knees:
  // - Base flexion is 0.35 rad
  // - Trailing leg: high heel kick (back-kick) up to 1.15 rad
  // - Forward swing: calf tucks naturally (-0.75 rad)
  leftLowerLeg: (p) => {
    const cycle = p * 6.2;
    const s = Math.sin(cycle);
    const backKick = Math.max(0, -s) * 1.15;
    const swingTuck = Math.max(0, s) * 0.75;
    return {
      x: -(0.35 + backKick + swingTuck),
      y: 0,
      z: 0,
    };
  },
  rightLowerLeg: (p) => {
    const cycle = p * 6.2;
    const s = -Math.sin(cycle);
    const backKick = Math.max(0, -s) * 1.15;
    const swingTuck = Math.max(0, s) * 0.75;
    return {
      x: -(0.35 + backKick + swingTuck),
      y: 0,
      z: 0,
    };
  },

  // Feet: Negative X flexes ankle downward (plantarflexion), aligning boot with shin
  // and pointing sole completely backward/downward
  leftFoot: (p) => {
    const cycle = p * 6.2;
    const s = Math.sin(cycle);
    return {
      x: -0.85 - s * 0.25,
      y: 0,
      z: 0,
    };
  },
  rightFoot: (p) => {
    const cycle = p * 6.2;
    const s = -Math.sin(cycle);
    return {
      x: -0.85 - s * 0.25,
      y: 0,
      z: 0,
    };
  },

  // Athletic running arms:
  // - Kept snug to the ribcage (Z = ±1.35)
  // - Elbows held at ~90 degrees (-1.55 rad) with pure hinge motion and zero twist
  // - Loose athletic running fists
  leftUpperArm: (p) => {
    const cycle = p * 6.2;
    const s = Math.sin(cycle);
    return {
      x: -s * 0.45 - 0.08, // In opposition to left leg
      y: 0.04,
      z: -1.35, // Snug along ribcage
    };
  },
  rightUpperArm: (p) => {
    const cycle = p * 6.2;
    const s = -Math.sin(cycle);
    return {
      x: -s * 0.45 - 0.08, // In opposition to right leg
      y: -0.04,
      z: 1.35, // Snug along ribcage
    };
  },
  leftLowerArm: (p) => {
    const cycle = p * 6.2;
    const s = Math.sin(cycle);
    return {
      x: -1.55 - s * 0.15, // Pure hinge ~90 deg bend pumping
      y: 0, // Zero twist
      z: 0,
    };
  },
  rightLowerArm: (p) => {
    const cycle = p * 6.2;
    const s = -Math.sin(cycle);
    return {
      x: -1.55 - s * 0.15, // Pure hinge ~90 deg bend pumping
      y: 0, // Zero twist
      z: 0,
    };
  },
  leftHand: staticPose(0, 0, 0),
  rightHand: staticPose(0, 0, 0),
  ...makeNaturalFingers('left', 0.85),
  ...makeNaturalFingers('right', 0.85),
};

// ─── THINK: Inquisitive / contemplative body language ─────────────────────
const thinkPose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  // Weight subtly shifted to one foot
  hips: staticPose(0, 0.04, 0.02),
  spine: staticPose(0.04, 0, 0.02),
  chest: staticPose(0.02, 0, 0.02),
  // Thoughtful head tilt looking slightly up/aside
  head: (p) => ({
    x: -0.06 + Math.sin(p * 0.4) * 0.015,
    y: -0.08,
    z: 0.18, // pronounced inquisitive 10° head tilt
  }),

  // Left arm comfortably folded across waist/ribs in contemplative pose
  leftShoulder: staticPose(-0.02, 0.02, -0.04),
  leftUpperArm: staticPose(-0.35, 0.18, -1.05),
  leftLowerArm: staticPose(-1.42, 0, 0),
  leftHand: staticPose(0.05, 0, 0),
  ...LEFT_RELAXED_FINGERS,

  // Right arm raised with elbow tucked against chest, hand resting at chin/cheek
  rightShoulder: staticPose(-0.04, -0.04, 0.06),
  rightUpperArm: staticPose(-0.65, -0.35, 0.90),
  rightLowerArm: staticPose(-2.05, 0, 0),
  rightHand: staticPose(-0.12, 0.25, -0.05),

  // Thinking fingers: index finger poised at cheek, thumb under jaw, others curled
  rightThumbProximal: staticPose(0.25, -0.20, -0.10),
  rightThumbIntermediate: staticPose(0.35, 0, 0),
  rightThumbDistal: staticPose(0.25, 0, 0),
  rightIndexProximal: staticPose(0.05, 0, 0),
  rightIndexIntermediate: staticPose(0.05, 0, 0),
  rightIndexDistal: staticPose(0.05, 0, 0),
  rightMiddleProximal: staticPose(1.20, 0, 0),
  rightMiddleIntermediate: staticPose(1.30, 0, 0),
  rightMiddleDistal: staticPose(0.85, 0, 0),
  rightRingProximal: staticPose(1.25, 0, 0),
  rightRingIntermediate: staticPose(1.35, 0, 0),
  rightRingDistal: staticPose(0.85, 0, 0),
  rightLittleProximal: staticPose(1.30, 0, 0),
  rightLittleIntermediate: staticPose(1.40, 0, 0),
  rightLittleDistal: staticPose(0.90, 0, 0),
};

// ─── PEACE SIGN: Victory / cute anime peace pose ────────────────────────
const peaceSignPose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  // Cute, energetic head tilt towards the peace sign
  head: (p) => ({
    x: -0.02 + Math.sin(p * 1.5) * 0.008,
    y: -0.05,
    z: 0.18, // charming 10° head tilt
  }),
  spine: staticPose(0.02, -0.02, 0.02),
  chest: staticPose(0.02, -0.01, 0.01),

  // Left arm rests gracefully along side
  leftUpperArm: staticPose(0.08, 0.05, -1.30),
  leftLowerArm: staticPose(-0.16, 0, 0),
  leftHand: staticPose(0, 0, 0),
  ...LEFT_RELAXED_FINGERS,

  // Right arm raised with elbow tucked near ribcage, forearm pointing up beside cheek
  rightShoulder: staticPose(-0.04, -0.02, 0.06),
  rightUpperArm: staticPose(-0.35, -0.22, 0.88),
  rightLowerArm: staticPose(-2.05, 0, 0),
  rightHand: staticPose(0.18, 0.12, 0.28),

  // Peace sign fingers: Index & Middle form clear V, Ring & Little folded into fist
  rightThumbProximal: staticPose(0.35, -0.25, -0.15),
  rightThumbIntermediate: staticPose(0.55, 0, 0),
  rightThumbDistal: staticPose(0.40, 0, 0),
  rightIndexProximal: staticPose(0.0, 0, -0.12), // extended with outward V splay
  rightIndexIntermediate: staticPose(0.0, 0, 0),
  rightIndexDistal: staticPose(0.0, 0, 0),
  rightMiddleProximal: staticPose(0.0, 0, 0.08),  // extended with inward V splay
  rightMiddleIntermediate: staticPose(0.0, 0, 0),
  rightMiddleDistal: staticPose(0.0, 0, 0),
  rightRingProximal: staticPose(1.35, 0, 0),      // tightly curled
  rightRingIntermediate: staticPose(1.40, 0, 0),
  rightRingDistal: staticPose(0.90, 0, 0),
  rightLittleProximal: staticPose(1.35, 0, 0),    // tightly curled
  rightLittleIntermediate: staticPose(1.45, 0, 0),
  rightLittleDistal: staticPose(0.95, 0, 0),
};

// ─── BOW: Respectful, polite greeting ────────────────────────────────────
const bowPose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  // Clean 30-degree forward bend at waist (positive X = forward flexion)
  spine: staticPose(0.48, 0, 0),
  chest: staticPose(0.22, 0, 0),
  head: staticPose(0.12, 0, 0), // head aligned with spine, looking down

  // Arms hang straight alongside torso with slight forward drape — zero forearm twist
  leftUpperArm: staticPose(0.24, 0.04, -1.28),
  rightUpperArm: staticPose(0.24, -0.04, 1.28),
  leftLowerArm: staticPose(-0.18, 0, 0),   // pure hinge, zero twist
  rightLowerArm: staticPose(-0.18, 0, 0),  // pure hinge, zero twist
  leftHand: staticPose(-0.08, 0, 0),        // palms face inward naturally
  rightHand: staticPose(-0.08, 0, 0),
  ...makeNaturalFingers('left', 0.4),
  ...makeNaturalFingers('right', 0.4),
};

// ─── COMFORT / HUG SELF: Self-soothing warm embrace ─────────────────────
const hugSelfPose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  spine: (p) => ({ x: 0.08 + Math.sin(p * 1.5) * 0.01, y: 0, z: Math.sin(p * 1.5) * 0.015 }),
  chest: staticPose(0.06, 0, 0),
  head: (p) => ({ x: 0.04, y: 0, z: 0.08 + Math.sin(p * 1.5) * 0.01 }),

  // Arms crossed gently over chest holding opposite arms
  leftUpperArm: staticPose(-0.52, 0.32, -0.92),
  leftLowerArm: staticPose(-1.62, 0, 0),
  leftHand: staticPose(-0.15, 0, 0),
  rightUpperArm: staticPose(-0.52, -0.32, 0.92),
  rightLowerArm: staticPose(-1.62, 0, 0),
  rightHand: staticPose(-0.15, 0, 0),
  ...makeNaturalFingers('left', 0.6),
  ...makeNaturalFingers('right', 0.6),
};

// ─── EXPLAIN: Conversational open-hand communication ─────────────────────
// Organic conversational gestures: Ava emphasizes points with expressive hand elevation,
// wrist articulation, natural thoracic breathing sway, and receptive palm orientation.
const explainPose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  hips: (p) => ({
    x: 0.01,
    y: Math.sin(p * 1.6) * 0.02,
    z: Math.sin(p * 0.8) * 0.012, // subtle conversational weight shift
  }),
  spine: (p) => ({
    x: -0.01 + Math.sin(p * 2.2) * 0.012,
    y: Math.sin(p * 1.6) * 0.025,
    z: 0,
  }),
  chest: (p) => ({
    x: Math.sin(p * 2.2) * 0.015,
    y: Math.sin(p * 1.6) * 0.015,
    z: 0,
  }),
  head: (p) => ({
    x: 0.03 + Math.sin(p * 2.2) * 0.02, // empathetic conversational nods
    y: Math.sin(p * 1.1) * 0.035, // looking naturally between ideas
    z: Math.sin(p * 1.6) * 0.018, // subtle inquisitive head tilt
  }),

  // Left arm: Conversational gesturing (rising and opening toward listener)
  leftShoulder: (p) => ({ x: -0.02, y: 0.02, z: Math.sin(p * 1.8) * 0.03 }),
  leftUpperArm: (p) => ({
    x: -0.42 + Math.sin(p * 1.8) * 0.12,
    y: 0.22,
    z: -1.02 + Math.sin(p * 1.8) * 0.08,
  }),
  leftLowerArm: (p) => ({
    x: -1.22 + Math.sin(p * 1.8 + 0.3) * 0.18,
    y: 0,
    z: 0,
  }),
  leftHand: (p) => ({
    x: 0.22 + Math.sin(p * 1.8 + 0.6) * 0.12,
    y: 0.15,
    z: -0.08,
  }),

  // Right arm: Expressive hand opening with complementary cadence
  rightShoulder: (p) => ({ x: -0.02, y: -0.02, z: -Math.sin(p * 1.8 + 0.8) * 0.03 }),
  rightUpperArm: (p) => ({
    x: -0.45 + Math.sin(p * 1.8 + 0.8) * 0.14,
    y: -0.22,
    z: 1.02 - Math.sin(p * 1.8 + 0.8) * 0.08,
  }),
  rightLowerArm: (p) => ({
    x: -1.25 + Math.sin(p * 1.8 + 1.1) * 0.18,
    y: 0,
    z: 0,
  }),
  rightHand: (p) => ({
    x: 0.22 + Math.sin(p * 1.8 + 1.4) * 0.12,
    y: -0.15,
    z: 0.08,
  }),

  // Gentle, open receptive fingers (relaxed curve, not stiff boards)
  ...makeNaturalFingers('left', 0.32),
  ...makeNaturalFingers('right', 0.32),
};

// ─── NOD: Agreement and positive affirmation ────────────────────────────
const nodPose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  spine: (p) => ({ x: 0.02 + Math.sin(p * 3.5) * 0.01, y: 0, z: 0 }),
  head: (p) => ({
    x: 0.12 + Math.sin(p * 3.5) * 0.14, // clean rhythmic head nodding
    y: 0,
    z: 0,
  }),
  // Right hand gently rises in receptive acknowledgement
  rightUpperArm: (p) => ({ x: -0.25, y: -0.1, z: 1.15 }),
  rightLowerArm: (p) => ({ x: -0.65 + Math.sin(p * 3.5) * 0.08, y: 0, z: 0 }),
  rightHand: staticPose(0.08, 0, 0),
  ...makeNaturalFingers('left', 0.5),
  ...makeNaturalFingers('right', 0.4),
};

// ─── DISAGREE: Polite, gentle head shake and clarifying gesture ──────────
const disagreePose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  spine: (p) => ({ x: -0.02, y: 0, z: 0 }),
  head: (p) => ({
    x: 0.02,
    y: Math.sin(p * 3.2) * 0.18, // head shake side-to-side
    z: Math.sin(p * 3.2) * 0.04,
  }),
  // Right hand gently raises with slight clarifying palm tilt
  rightUpperArm: staticPose(-0.35, -0.12, 1.12),
  rightLowerArm: (p) => ({ x: -0.95, y: 0, z: 0 }),
  rightHand: (p) => ({ x: 0.12, y: -0.12 + Math.sin(p * 3.2) * 0.1, z: 0.04 }),
  ...makeNaturalFingers('right', 0.35),
};

// ─── POINT: Directing attention or highlighting a focus point ────────────
const pointPose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  head: (p) => ({ x: -0.04, y: -0.16, z: 0.02 }), // head turns with focus toward target
  spine: staticPose(0.02, -0.06, 0),
  chest: staticPose(0.02, -0.04, 0),

  // Left arm rests naturally at side
  leftUpperArm: staticPose(0.08, 0.04, -1.30),
  leftLowerArm: staticPose(-0.16, 0, 0),
  leftHand: staticPose(0, 0, 0),

  // Right arm raises and extends forward pointing directly at target
  rightShoulder: staticPose(-0.04, -0.02, 0.04),
  rightUpperArm: staticPose(-0.65, -0.35, 0.95), // Angled forward toward viewer/target
  rightLowerArm: staticPose(-0.50, 0, 0),          // Pure hinge extension, zero twist
  rightHand: staticPose(0.04, 0, 0),               // Neutral palm, aligned with forearm (no y/z twist)

  // Pointing finger gesture: Index straight, Thumb folded, others folded into tight fist
  rightThumbProximal: staticPose(0.35, -0.25, -0.15),
  rightThumbIntermediate: staticPose(0.55, 0, 0),
  rightThumbDistal: staticPose(0.40, 0, 0),
  rightIndexProximal: staticPose(0.0, 0, 0), // straight index
  rightIndexIntermediate: staticPose(0.0, 0, 0),
  rightIndexDistal: staticPose(0.0, 0, 0),
  rightMiddleProximal: staticPose(1.35, 0, 0),
  rightMiddleIntermediate: staticPose(1.40, 0, 0),
  rightMiddleDistal: staticPose(0.90, 0, 0),
  rightRingProximal: staticPose(1.35, 0, 0),
  rightRingIntermediate: staticPose(1.40, 0, 0),
  rightRingDistal: staticPose(0.90, 0, 0),
  rightLittleProximal: staticPose(1.35, 0, 0),
  rightLittleIntermediate: staticPose(1.45, 0, 0),
  rightLittleDistal: staticPose(0.95, 0, 0),
  ...makeNaturalFingers('left', 0.5),
};

// ─── LISTEN: Attentive, empathetic listening posture ─────────────────────
const listenPose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  hips: staticPose(0, 0.02, 0.01),
  spine: (p) => ({ x: 0.04 + Math.sin(p * 1.2) * 0.008, y: 0.02, z: 0.01 }), // attentive slight forward lean
  chest: staticPose(0.03, 0.02, 0),
  head: (p) => ({
    x: 0.04 + Math.sin(p * 1.8) * 0.015, // gentle slow listening nods
    y: 0.06,
    z: 0.12, // inquisitive head tilt towards user
  }),

  // Relaxed resting arms with natural breathing response
  leftUpperArm: staticPose(0.12, 0.05, -1.28),
  leftLowerArm: staticPose(-0.35, 0, 0),
  rightUpperArm: staticPose(0.12, -0.05, 1.28),
  rightLowerArm: staticPose(-0.35, 0, 0),
  ...makeNaturalFingers('left', 0.45),
  ...makeNaturalFingers('right', 0.45),
};

// ─── CONFUSION: Puzzled, seeking clarification ───────────────────────────
const confusionPose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  spine: staticPose(0.02, 0, 0.03),
  head: (p) => ({
    x: -0.04,
    y: Math.sin(p * 1.2) * 0.02,
    z: -0.22, // pronounced puzzled head tilt
  }),
  // Left arm slightly open in shrug
  leftShoulder: staticPose(-0.06, 0.02, -0.04),
  leftUpperArm: staticPose(-0.25, 0.15, -0.95),
  leftLowerArm: staticPose(-0.85, 0, 0),
  leftHand: staticPose(0.15, 0.15, 0),

  // Right hand elevated near chin
  rightShoulder: staticPose(-0.04, -0.02, 0.04),
  rightUpperArm: staticPose(-0.45, -0.15, 0.85),
  rightLowerArm: staticPose(-1.45, 0, 0),
  rightHand: staticPose(0.12, -0.1, 0),
  ...makeNaturalFingers('left', 0.4),
  ...makeNaturalFingers('right', 0.4),
};

// ─── REASSURE: Warm, comforting gesture with hand over heart ─────────────
const reassurePose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  spine: staticPose(0.04, 0, 0),
  head: staticPose(0.02, 0, 0.06), // warm head tilt
  // Right hand placed gently over heart/chest
  rightShoulder: staticPose(-0.03, -0.02, 0.04),
  rightUpperArm: staticPose(-0.52, -0.22, 0.72),
  rightLowerArm: staticPose(-1.65, 0, 0),
  rightHand: staticPose(-0.1, 0.15, 0.05), // flat against upper chest
  ...makeNaturalFingers('right', 0.25),
  ...makeNaturalFingers('left', 0.5),
};

// ─── CHEER: Joyful celebration ──────────────────────────────────────────
const cheerPose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  hips: (p) => ({ x: 0, y: Math.abs(Math.sin(p * 5)) * 0.04, z: 0 }),
  spine: (p) => ({ x: -0.08, y: 0, z: Math.sin(p * 5) * 0.02 }),
  chest: staticPose(-0.06, 0, 0),
  head: (p) => ({ x: -0.12, y: Math.sin(p * 5) * 0.03, z: 0 }),

  // Both arms joyfully raised with celebratory wave
  leftUpperArm: (p) => ({
    x: -0.45,
    y: 0.15,
    z: -0.35 + Math.sin(p * 5) * 0.1,
  }),
  rightUpperArm: (p) => ({
    x: -0.45,
    y: -0.15,
    z: 0.35 - Math.sin(p * 5) * 0.1,
  }),
  leftLowerArm: (p) => ({
    x: -1.25 + Math.sin(p * 5) * 0.18,
    y: 0,
    z: 0,
  }),
  rightLowerArm: (p) => ({
    x: -1.25 + Math.sin(p * 5) * 0.18,
    y: 0,
    z: 0,
  }),
  leftHand: staticPose(0.15, 0, 0),
  rightHand: staticPose(0.15, 0, 0),
  ...makeNaturalFingers('left', 0.25),
  ...makeNaturalFingers('right', 0.25),
};

// ─── CLAP: Cheerful applause ────────────────────────────────────────────
const clapPose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  spine: (p) => ({ x: 0.03 + Math.sin(p * 5.5) * 0.01, y: 0, z: 0 }), // subtle clap rhythm
  chest: staticPose(0.02, 0, 0),
  head: (p) => ({ x: 0.04 + Math.sin(p * 5.5) * 0.015, y: 0, z: Math.sin(p * 2.5) * 0.03 }), // slight enjoyment tilt

  // Both arms brought forward at chest level; upper arms pulse in/out for clap rhythm
  leftUpperArm: (p) => {
    const clap = Math.sin(p * 5.5);
    const meet = Math.max(0, clap);
    return {
      x: -0.45,
      y: 0.35 + meet * 0.06,
      z: -1.05,
    };
  },
  leftLowerArm: staticPose(-1.50, 0, 0),
  leftHand: staticPose(0, -0.30, 0.15),
  rightUpperArm: (p) => {
    const clap = Math.sin(p * 5.5);
    const meet = Math.max(0, clap);
    return {
      x: -0.45,
      y: -0.35 - meet * 0.06,
      z: 1.05,
    };
  },
  rightLowerArm: staticPose(-1.50, 0, 0),
  rightHand: staticPose(0, 0.30, -0.15),
  ...makeNaturalFingers('left', 0.12),      // open clap surfaces
  ...makeNaturalFingers('right', 0.12),
};

// ─── SIT (Chair) ─────────────────────────────────────────────────────────
const sitPose: PoseDefinition = {
  hips: staticPose(-0.08, 0, 0),
  leftUpperLeg: staticPose(1.5, 0, 0.06),    // ~86° forward
  rightUpperLeg: staticPose(1.5, 0, -0.06),
  leftLowerLeg: staticPose(-1.5, 0, 0),      // fold back ~86°
  rightLowerLeg: staticPose(-1.5, 0, 0),
  leftFoot: staticPose(0.1, 0, 0.04),
  rightFoot: staticPose(0.1, 0, -0.04),
  spine: staticPose(0.08, 0, 0),
  chest: staticPose(0.04, 0, 0),
  leftShoulder: staticPose(0, 0, 0),
  rightShoulder: staticPose(0, 0, 0),
  // Hands resting on thighs
  leftUpperArm: staticPose(0.3, 0.2, 0.8),
  rightUpperArm: staticPose(0.3, -0.2, -0.8),
  leftLowerArm: staticPose(-0.8, 0.15, 0),
  rightLowerArm: staticPose(-0.8, -0.15, 0),
  ...makeNaturalFingers('left', 0.4),
  ...makeNaturalFingers('right', 0.4),
};

// ─── SEIZA (正座) - Japanese formal kneeling ─────────────────────────────
// Knees forward, shins flat, hips 0.25 units above floor
const seizaPose: PoseDefinition = {
  hips: staticPose(-0.25, 0, 0),               // lowered toward floor
  leftUpperLeg: staticPose(1.8, 0, 0.04),      // thighs forward ~103°
  rightUpperLeg: staticPose(1.8, 0, -0.04),
  leftLowerLeg: staticPose(-2.6, 0, 0),        // fold back ~149° (shins flat)
  rightLowerLeg: staticPose(-2.6, 0, 0),
  leftFoot: staticPose(-0.5, 0, 0.06),         // toes pointing back, flat
  rightFoot: staticPose(-0.5, 0, -0.06),
  spine: staticPose(0.08, 0, 0),               // upright
  chest: staticPose(0.04, 0, 0),
  upperChest: staticPose(0.02, 0, 0),
  head: staticPose(-0.05, 0, 0),
  leftShoulder: staticPose(0, 0, 0),
  rightShoulder: staticPose(0, 0, 0),
  // Hands resting on thighs (corrected axes)
  leftUpperArm: staticPose(0.15, 0, 0.9),
  rightUpperArm: staticPose(0.15, 0, -0.9),
  leftLowerArm: staticPose(-0.6, 0.1, 0),
  rightLowerArm: staticPose(-0.6, -0.1, 0),
  leftHand: staticPose(-0.2, 0, 0),
  rightHand: staticPose(-0.2, 0, 0),
  ...makeNaturalFingers('left', 0.4),
  ...makeNaturalFingers('right', 0.4),
};

// ─── AGURA (胡座) - Cross-legged sitting ─────────────────────────────────
const aguraPose: PoseDefinition = {
  hips: staticPose(-0.12, 0, 0),
  leftUpperLeg: staticPose(1.4, -0.5, 0.6),    // thigh forward + rotated out
  rightUpperLeg: staticPose(1.4, 0.5, -0.6),
  leftLowerLeg: staticPose(-2.2, 0.3, 0),      // folded back tightly
  rightLowerLeg: staticPose(-2.2, -0.3, 0),
  leftFoot: staticPose(-0.2, 0, 0.15),
  rightFoot: staticPose(-0.2, 0, -0.15),
  spine: staticPose(0.05, 0, 0),
  chest: staticPose(0.03, 0, 0),
  leftShoulder: staticPose(0, 0, 0),
  rightShoulder: staticPose(0, 0, 0),
  leftUpperArm: staticPose(0.2, 0.1, 0.9),
  rightUpperArm: staticPose(0.2, -0.1, -0.9),
  leftLowerArm: staticPose(-0.7, 0.2, 0),
  rightLowerArm: staticPose(-0.7, -0.2, 0),
  ...makeNaturalFingers('left', 0.5),
  ...makeNaturalFingers('right', 0.5),
};

// ─── AFK IDLE: Relaxed contrapposto standing rest (AFK) ───────────────────
const afkIdlePose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  hipsOffset: (p) => ({ x: 0.018, y: -0.012 + Math.sin(p * 0.8) * 0.003, z: 0 }),
  hips: staticPose(0.02, 0.03, 0.045), // pelvis tilted over supporting leg
  spine: (p) => ({ x: 0.035, y: -0.025, z: -0.025 + Math.sin(p * 0.8) * 0.004 }),
  chest: staticPose(0.015, -0.015, -0.015),
  neck: staticPose(0.04, 0.05, 0.08),
  head: (p) => ({ x: 0.06 + Math.sin(p * 0.8) * 0.01, y: 0.06, z: 0.12 }), // resting head angle

  leftUpperLeg: staticPose(0.04, -0.03, 0.05), // relaxed leg
  leftLowerLeg: staticPose(-0.09, 0, 0),
  rightUpperLeg: staticPose(-0.02, 0.02, -0.03), // supporting leg
  rightLowerLeg: staticPose(0, 0, 0),

  leftUpperArm: staticPose(0.08, 0.04, -1.34),
  leftLowerArm: staticPose(-0.18, 0.02, 0),
  rightUpperArm: staticPose(0.06, -0.04, 1.34),
  rightLowerArm: staticPose(-0.18, -0.02, 0),
  ...makeNaturalFingers('left', 0.45),
  ...makeNaturalFingers('right', 0.45),
};

// ─── DANCE: Fluid rhythmic performance ──────────────────────────────────
const dancePose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  hips: (p) => ({ x: 0, y: Math.sin(p * 3) * 0.15, z: 0 }),
  spine: (p) => ({ x: Math.sin(p * 6) * 0.04, y: -Math.sin(p * 3) * 0.1, z: 0 }),
  chest: (p) => ({ x: 0, y: Math.sin(p * 3) * 0.12, z: 0 }),
  head: (p) => ({ x: Math.sin(p * 6) * 0.06, y: Math.sin(p * 3) * 0.1, z: 0 }),

  leftUpperArm: (p) => ({ x: Math.sin(p * 3) * 0.4, y: 0.1, z: -0.85 }),
  rightUpperArm: (p) => ({ x: Math.sin(p * 3 + Math.PI) * 0.4, y: -0.1, z: 0.85 }),
  leftLowerArm: (p) => ({ x: -0.8 - Math.abs(Math.sin(p * 3)) * 0.5, y: 0, z: 0 }),
  rightLowerArm: (p) => ({ x: -0.8 - Math.abs(Math.sin(p * 3 + Math.PI)) * 0.5, y: 0, z: 0 }),

  leftUpperLeg: (p) => ({ x: Math.sin(p * 6) * 0.2, y: 0, z: 0 }),
  rightUpperLeg: (p) => ({ x: -Math.sin(p * 6) * 0.2, y: 0, z: 0 }),
  leftLowerLeg: (p) => ({ x: -Math.max(0, Math.sin(p * 6)) * 0.35, y: 0, z: 0 }),
  rightLowerLeg: (p) => ({ x: -Math.max(0, -Math.sin(p * 6)) * 0.35, y: 0, z: 0 }),
  ...makeNaturalFingers('left', 0.35),
  ...makeNaturalFingers('right', 0.35),
};

// ─── JUMP: Joyful leap ──────────────────────────────────────────────────
const jumpPose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  hips: (p) => {
    const cycle = (p * 1.0) % 1;
    return cycle < 0.4 ? { x: 0, y: -0.1, z: 0 } : { x: 0, y: 0.15, z: 0 };
  },
  leftUpperLeg: (p) => {
    const cycle = (p * 1.0) % 1;
    return cycle < 0.4 ? { x: 0.35, y: 0, z: 0 } : { x: -0.2, y: 0, z: 0 };
  },
  rightUpperLeg: (p) => {
    const cycle = (p * 1.0) % 1;
    return cycle < 0.4 ? { x: 0.35, y: 0, z: 0 } : { x: -0.2, y: 0, z: 0 };
  },
  leftLowerLeg: (p) => {
    const cycle = (p * 1.0) % 1;
    return cycle < 0.4 ? { x: -0.6, y: 0, z: 0 } : { x: -0.2, y: 0, z: 0 };
  },
  rightLowerLeg: (p) => {
    const cycle = (p * 1.0) % 1;
    return cycle < 0.4 ? { x: -0.6, y: 0, z: 0 } : { x: -0.2, y: 0, z: 0 };
  },
  leftUpperArm: (p) => {
    const cycle = (p * 1.0) % 1;
    return cycle < 0.4 ? { x: 0.1, y: 0, z: -1.2 } : { x: -0.5, y: 0, z: -0.5 };
  },
  rightUpperArm: (p) => {
    const cycle = (p * 1.0) % 1;
    return cycle < 0.4 ? { x: 0.1, y: 0, z: 1.2 } : { x: -0.5, y: 0, z: 0.5 };
  },
  leftLowerArm: staticPose(-0.35, 0, 0),
  rightLowerArm: staticPose(-0.35, 0, 0),
};

// ─── CRY: Sad emotional posture ─────────────────────────────────────────
const cryPose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  spine: (p) => ({
    x: 0.18 + Math.sin(p * 8) * 0.02, // sobbing tremor
    y: 0,
    z: 0,
  }),
  chest: (p) => ({
    x: 0.12 + Math.sin(p * 8 + 0.5) * 0.02,
    y: 0,
    z: 0,
  }),
  head: staticPose(0.35, 0, 0), // head hung down

  // Both hands up to face covering eyes
  leftUpperArm: staticPose(-0.85, 0.25, -0.65),
  rightUpperArm: staticPose(-0.85, -0.25, 0.65),
  leftLowerArm: staticPose(-1.85, 0, 0),
  rightLowerArm: staticPose(-1.85, 0, 0),
  leftHand: staticPose(-0.25, 0, 0),
  rightHand: staticPose(-0.25, 0, 0),
  ...makeNaturalFingers('left', 0.8),
  ...makeNaturalFingers('right', 0.8),
};

// ─── GASP: Surprised intake of breath ───────────────────────────────────
const gaspPose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  spine: staticPose(-0.06, 0, 0),
  head: staticPose(-0.08, 0, 0), // head pulls back slightly

  // Both hands over mouth
  leftUpperArm: staticPose(-0.82, 0.22, -0.68),
  rightUpperArm: staticPose(-0.82, -0.22, 0.68),
  leftLowerArm: staticPose(-1.75, 0, 0),
  rightLowerArm: staticPose(-1.75, 0, 0),
  leftHand: staticPose(-0.15, 0, 0),
  rightHand: staticPose(-0.15, 0, 0),
  ...makeNaturalFingers('left', 0.4),
  ...makeNaturalFingers('right', 0.4),
};

// ─── PEEKABOO: Playful hiding then popping out ───────────────────────────
const peekabooPose: PoseDefinition = {
  ...ARM_REST_DEFAULTS,
  hips: (p: number) => {
    const cycle = p % 4;
    return cycle < 2 ? { x: 0, y: -0.15, z: 0 } : { x: 0, y: 0.04, z: 0 };
  },
  spine: (p: number) => {
    const cycle = p % 4;
    return cycle < 2 ? { x: 0.25, y: 0, z: 0 } : { x: -0.08, y: 0, z: 0 };
  },
  head: (p: number) => {
    const cycle = p % 4;
    return cycle < 2 ? { x: 0.2, y: 0, z: 0 } : { x: -0.1, y: Math.sin(cycle * 6) * 0.04, z: 0 };
  },
  // Hands cover face during cycle < 2, then fling open
  leftUpperArm: (p: number) => {
    const cycle = p % 4;
    return cycle < 2 ? { x: -0.85, y: 0.25, z: -0.65 } : { x: -0.4, y: 0.2, z: -0.4 };
  },
  rightUpperArm: (p: number) => {
    const cycle = p % 4;
    return cycle < 2 ? { x: -0.85, y: -0.25, z: 0.65 } : { x: -0.4, y: -0.2, z: 0.4 };
  },
  leftLowerArm: (p: number) => {
    const cycle = p % 4;
    return cycle < 2 ? { x: -1.8, y: 0, z: 0 } : { x: -1.1, y: 0, z: 0 };
  },
  rightLowerArm: (p: number) => {
    const cycle = p % 4;
    return cycle < 2 ? { x: -1.8, y: 0, z: 0 } : { x: -1.1, y: 0, z: 0 };
  },
  ...makeNaturalFingers('left', 0.3),
  ...makeNaturalFingers('right', 0.3),
};

// ─── FINGER COUNTING POSES (1–5) ─────────────────────────────────────────
const FINGER_BONE_PREFIXES = ['rightThumb', 'rightIndex', 'rightMiddle', 'rightRing', 'rightLittle'];
const FINGER_JOINTS = ['Proximal', 'Intermediate', 'Distal'];
const COUNT_FINGER_STATES: Record<string, boolean[]> = {
  count_1: [false, true, false, false, false],
  count_2: [false, true, true, false, false],
  count_3: [false, true, true, true, false],
  count_4: [false, true, true, true, true],
  count_5: [true, true, true, true, true],
};

function makeCountPose(countKey: string): PoseDefinition {
  const states = COUNT_FINGER_STATES[countKey];
  const pose: PoseDefinition = {
    ...ARM_REST_DEFAULTS,
    // Right hand presented clearly forward at chest level
    rightShoulder: staticPose(-0.04, 0, 0.05),
    rightUpperArm: staticPose(-0.65, 0.05, 0.35),
    rightLowerArm: staticPose(-1.45, 0.12, 0),
    rightHand: staticPose(0.08, 0.25, 0.05),
  };

  FINGER_BONE_PREFIXES.forEach((prefix, fi) => {
    const isOpen = states[fi];
    FINGER_JOINTS.forEach((joint) => {
      const boneName = prefix + joint;
      if (prefix === 'rightThumb') {
        pose[boneName] = staticPose(isOpen ? 0.05 : 0.45, isOpen ? -0.15 : -0.3, isOpen ? -0.05 : -0.2);
      } else {
        pose[boneName] = staticPose(isOpen ? 0.04 : 1.25, 0, 0);
      }
    });
  });

  return pose;
}

export const POSE_LIBRARY: Record<PoseType, PoseDefinition> = {
  idle: idlePose,
  walk: walkPose,
  run: runPose,
  jump: jumpPose,
  sit: sitPose,
  seiza: seizaPose,
  agura: aguraPose,
  afk_idle: afkIdlePose,
  dance: dancePose,
  wave: wavePose,
  bow: bowPose,
  think: thinkPose,
  cry: cryPose,
  hug_self: hugSelfPose,
  gasp: gaspPose,
  peace_sign: peaceSignPose,
  peekaboo: peekabooPose,
  explain: explainPose,
  cheer: cheerPose,
  clap: clapPose,
  nod: nodPose,
  disagree: disagreePose,
  point: pointPose,
  listen: listenPose,
  confusion: confusionPose,
  reassure: reassurePose,
  count_1: makeCountPose('count_1'),
  count_2: makeCountPose('count_2'),
  count_3: makeCountPose('count_3'),
  count_4: makeCountPose('count_4'),
  count_5: makeCountPose('count_5'),
};

export const ALL_BONE_NAMES = [
  'hips', 'spine', 'chest', 'upperChest', 'neck', 'head',
  'leftUpperArm', 'leftLowerArm', 'leftHand',
  'rightUpperArm', 'rightLowerArm', 'rightHand',
  'leftUpperLeg', 'leftLowerLeg', 'leftFoot',
  'rightUpperLeg', 'rightLowerLeg', 'rightFoot',
  'leftShoulder', 'rightShoulder',
  // Left Hand & Fingers
  'leftThumbMetacarpal', 'leftThumbProximal', 'leftThumbIntermediate', 'leftThumbDistal',
  'leftIndexProximal', 'leftIndexIntermediate', 'leftIndexDistal',
  'leftMiddleProximal', 'leftMiddleIntermediate', 'leftMiddleDistal',
  'leftRingProximal', 'leftRingIntermediate', 'leftRingDistal',
  'leftLittleProximal', 'leftLittleIntermediate', 'leftLittleDistal',
  // Right Hand & Fingers
  'rightThumbMetacarpal', 'rightThumbProximal', 'rightThumbIntermediate', 'rightThumbDistal',
  'rightIndexProximal', 'rightIndexIntermediate', 'rightIndexDistal',
  'rightMiddleProximal', 'rightMiddleIntermediate', 'rightMiddleDistal',
  'rightRingProximal', 'rightRingIntermediate', 'rightRingDistal',
  'rightLittleProximal', 'rightLittleIntermediate', 'rightLittleDistal',
];
