export type AvatarFeature = "breathing" | "hairPhysics" | "eyeTracking" | "lipSync";

export type AvatarFeatures = Record<AvatarFeature, boolean>;

export interface AvatarControl {
  emotion?: string;
  emotionWeight?: number;
  gesture?: string;
  speech?: string;
  audioUrl?: string;
  features?: Partial<AvatarFeatures>;
}

export interface AvatarWardrobe {
  id: string;
  name: string;
  description: string;
  modelUrl: string;
  accent: string;
  source: "bundled" | "local";
}

export const DEFAULT_AVATAR_FEATURES: AvatarFeatures = {
  breathing: true,
  hairPhysics: true,
  eyeTracking: true,
  lipSync: true,
};

// A wardrobe item is a complete VRM. It keeps body, outfit, hair physics, and
// blendshapes together instead of attempting to repaint clothing at runtime.
export const AVATAR_WARDROBE: AvatarWardrobe[] = [
  {
    id: "studio-avatar",
    name: "Studio Avatar",
    description: "VRoid character with long-hair and clothing physics",
    modelUrl: "/avatars/vroid-studio-avatar.vrm",
    accent: "#f472b6",
    source: "bundled",
  },
  {
    id: "neural-avatar",
    name: "Neural Avatar",
    description: "JARVIS VRM character preset",
    modelUrl: "/avatars/jarvis-neural.vrm",
    accent: "#22d3ee",
    source: "bundled",
  },
  {
    id: "ava-custom",
    name: "Ava Custom",
    description: "Custom uploaded 3D VRM character with full rigging",
    modelUrl: "/avatars/ava-custom.vrm",
    accent: "#a855f7",
    source: "local",
  },
];

export const DEFAULT_WARDROBE = AVATAR_WARDROBE[2];
