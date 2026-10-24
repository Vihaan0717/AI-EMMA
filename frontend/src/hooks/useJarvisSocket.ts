import { useState, useEffect, useCallback } from "react";
import type { AvatarControl } from "@/lib/avatar";

type AvatarState = "idle" | "listening" | "thinking" | "scanning";

interface JarvisData {
  weather?: any;
  news?: any[];
  movies?: any[];
  os_context?: {
    active_window: string;
    cpu_percent: number;
    memory_percent: number;
    battery_percent?: number;
    is_plugged_in?: boolean;
    biological_state?: string;
    timestamp: string;
  };
  system_config?: {
    environment: string;
    model: string;
  };
  file_change?: {
    path: string;
    event: string;
  };
  biometric?: {
    status: string;
    user?: string;
  };
  tracking?: {
    headPitch: number;
    headYaw: number;
    eyePitch: number;
    eyeYaw: number;
    blinkLeft?: number;
    blinkRight?: number;
  };
  code_result?: string;
  audioAmplitude?: number;
  currentGesture?: string;
  currentEmotion?: string;
  currentSpeech?: string;
  handPose?: { left?: string; right?: string };
  fingerCurls?: { left?: Record<string, number>; right?: Record<string, number> };
}

export const useJarvisSocket = (url: string = "ws://127.0.0.1:8765") => {
  const [data, setData] = useState<JarvisData>({});
  const [avatarState, setAvatarState] = useState<AvatarState>("idle");
  const [socket, setSocket] = useState<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(url);
    
    ws.onopen = () => {
      console.log("Connected to JARVIS Backend");
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        console.log("JARVIS Message:", msg.type, msg);

        switch (msg.type) {
          case "INIT_DATA":
            setData(prev => ({ 
              ...prev, 
              ...msg,
              system_config: msg.system_config || prev.system_config 
            }));
            break;
          case "OS_CONTEXT":
            setData(prev => ({ 
              ...prev, 
              os_context: {
                ...msg.context,
                timestamp: msg.timestamp
              } 
            }));
            break;
          case "FILE_CHANGE":
            setData(prev => ({ ...prev, file_change: msg }));
            break;
          case "BIOMETRIC_EVENT":
            if (msg.status === "SCANNING") setAvatarState("scanning");
            else if (msg.status === "VERIFIED") setAvatarState("idle");
            break;
          case "CODE_RESULT":
            setData(prev => ({ ...prev, code_result: msg.code }));
            setAvatarState("idle");
            break;
          case "VISION_TRACKING":
          case "TRACKING":
            if (msg.detected) {
              const bl = msg.blink_left;
              const br = msg.blink_right;
              
              if (msg.yaw !== undefined) {
                // Decouple head movement from eye movement
                const headP = msg.pitch ?? 0;
                const headY = msg.yaw ?? 0;
                // Use explicit eye tracking if available, else infer slightly from head
                const eyeP = msg.eye_pitch ?? (headP * 0.3);
                const eyeY = msg.eye_yaw ?? (headY * 0.3);

                setData(prev => ({ 
                  ...prev, 
                  tracking: { 
                    headPitch: headP, 
                    headYaw: -headY, // Invert yaw
                    eyePitch: eyeP,
                    eyeYaw: -eyeY,
                    blinkLeft: bl, 
                    blinkRight: br 
                  } 
                }));
              }
            } else {
              // Not detected, clear tracking so it falls back to mouse tracking
              setData(prev => ({ ...prev, tracking: undefined }));
            }
            break;
          case "PLAY_AUDIO":
            if (msg.url) {
              const audio = new Audio(msg.url);
              
              // Setup Audio Analysis for Lip Sync
              const AudioContextClass = (window.AudioContext || (window as any).webkitAudioContext);
              const audioCtx = new AudioContextClass();
              const source = audioCtx.createMediaElementSource(audio);
              const analyser = audioCtx.createAnalyser();
              analyser.fftSize = 256;
              source.connect(analyser);
              analyser.connect(audioCtx.destination);
              
              const bufferLength = analyser.frequencyBinCount;
              const dataArray = new Uint8Array(bufferLength);
              
              const updateAmplitude = () => {
                if (audio.paused || audio.ended) {
                  setData(prev => ({ ...prev, audioAmplitude: 0 }));
                  audioCtx.close();
                  return;
                }
                
                analyser.getByteFrequencyData(dataArray);
                let sum = 0;
                for (let i = 0; i < bufferLength; i++) {
                  sum += dataArray[i];
                }
                const average = sum / bufferLength;
                const normalized = Math.min(1.0, average / 40.0); // Adjust sensitivity
                
                setData(prev => ({ ...prev, audioAmplitude: normalized }));
                requestAnimationFrame(updateAmplitude);
              };
              
              audio.play().then(() => {
                if (audioCtx.state === 'suspended') {
                  audioCtx.resume();
                }
                updateAmplitude();
              }).catch(e => console.error("Audio playback failed:", e));
            }
            break;
          case "ANIMATION":
            // Map backend animation commands to avatar states
            if (msg.action === "TALKING") {
              setAvatarState("listening");  // triggers mouth/body activity
            } else if (msg.action === "STOP_TALKING") {
              setAvatarState("idle");
              setData(prev => ({ ...prev, audioAmplitude: 0 }));
            } else if (msg.action === "WAVE") {
              setAvatarState("idle"); // wave is handled by pose below
              // Trigger a temporary wave action via data
              setData(prev => ({ ...prev, currentGesture: "wave" }));
            } else if (msg.action === "WHISPER") {
              setAvatarState("thinking");
            } else {
              // Pose names sent directly (e.g. sitting, walk, idle, thinking etc.)
              setData(prev => ({ ...prev, currentGesture: msg.action }));
            }
            break;
          case "AI_RESPONSE":
            // Map emotion and gesture from backend AI response with safe allowlist validation
            {
              const emotionMap: Record<string, string> = {
                joy: "happy", happy: "happy", cheerful: "happy",
                sorrow: "sad", sad: "sad", grief: "sad_severe",
                neutral: "neutral", calm: "neutral",
                angry: "angry", frustration: "angry",
                surprised: "surprised", surprise: "surprised", curiosity: "surprised",
                relaxed: "relaxed", content: "relaxed",
                thinking: "thinking", thoughtful: "thinking", contemplative: "thinking",
                serious: "serious", confidence: "neutral", concern: "thinking",
                empathy: "relaxed", uncertainty: "thinking",
              };
              const poseMap: Record<string, string> = {
                // Conversational
                explain: "explain", explaining: "explain", open_hands: "explain",
                nod: "nod", agree: "nod", agreement: "nod", yes: "nod",
                disagree: "disagree", disagreement: "disagree", no: "disagree",
                point: "point", pointing: "point", focus: "point",
                listen: "listen", listening: "listen", attentive: "listen",
                confusion: "confusion", confused: "confusion", puzzle: "confusion",
                reassure: "reassure", reassuring: "reassure", comfort: "hug_self",
                think: "think", thinking: "think", ponder: "think",
                wave: "wave", waving: "wave", greeting: "wave", hello: "wave",
                bow: "bow", respect: "bow", apologize: "bow",
                cheer: "cheer", celebrate: "cheer", victory: "peace_sign", peace: "peace_sign",
                clap: "clap", applause: "clap",
                // Locomotion & Postures
                walk: "walk", walking: "walk",
                run: "run", jog: "run", jogging: "run",
                sit: "sit", sitting: "sit",
                sit_feminine: "sit_feminine", girly_sit: "sit_feminine",
                sit_relaxed: "sit_relaxed", casual_sit: "sit_relaxed",
                seiza: "seiza", kneel: "seiza",
                agura: "agura", cross_legged: "agura",
                idle: "idle", relaxed_standing: "idle", afk: "afk_idle", afk_idle: "afk_idle",
              };

              const rawEmotion = (msg.emotion ?? "").toString().toLowerCase().trim();
              const rawGesture = (msg.gesture ?? "").toString().toLowerCase().trim();

              const mappedEmotion = emotionMap[rawEmotion] || "neutral";
              const mappedPose = poseMap[rawGesture] || (rawGesture in poseMap ? rawGesture : "idle");

              setData(prev => ({
                ...prev,
                currentEmotion: mappedEmotion,
                currentGesture: mappedPose,
                currentSpeech: msg.text ?? msg.speech ?? prev.currentSpeech,
              }));
            }
            break;
          case "BODY_CONTROL":
            if (msg.posture || msg.gesture || msg.action) {
              const act = msg.posture ?? msg.gesture ?? msg.action;
              setData(prev => ({
                ...prev,
                currentGesture: act,
                currentEmotion: msg.emotion ?? prev.currentEmotion
              }));
            }
            break;
          case "FINGER_CONTROL":
            setData(prev => {
              const hand = msg.hand || "both";
              const newHandPose = { ...(prev.handPose || { left: "relaxed", right: "relaxed" }) };
              const newFingerCurls = { 
                left: { ...(prev.fingerCurls?.left || {}) },
                right: { ...(prev.fingerCurls?.right || {}) }
              };

              if (msg.pose) {
                if (hand === "left" || hand === "both") newHandPose.left = msg.pose;
                if (hand === "right" || hand === "both") newHandPose.right = msg.pose;
              }
              if (msg.curls) {
                if (hand === "left" || hand === "both") Object.assign(newFingerCurls.left, msg.curls);
                if (hand === "right" || hand === "both") Object.assign(newFingerCurls.right, msg.curls);
              }

              return {
                ...prev,
                handPose: newHandPose,
                fingerCurls: newFingerCurls,
              };
            });
            break;
          case "LIMB_CONTROL":
            if (msg.head) {
              setData(prev => ({
                ...prev,
                tracking: {
                  headPitch: msg.head.pitch ?? 0,
                  headYaw: msg.head.yaw ?? 0,
                  eyePitch: (msg.head.pitch ?? 0) * 0.3,
                  eyeYaw: (msg.head.yaw ?? 0) * 0.3,
                }
              }));
            }
            break;
        }
      } catch (err) {
        console.error("Failed to parse JARVIS message", err);
      }
    };

    ws.onclose = () => {
      console.log("Disconnected from JARVIS Backend");
      setSocket(null);
      setAvatarState("idle");
    };

    return () => ws.close();
  }, [url]);

  const sendCommand = useCallback((type: string, payload: any) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(json.stringify({ type, ...payload }));
      if (type === "GET_CODE_GEN") setAvatarState("thinking");
    }
  }, [socket]);

  const controlAvatar = useCallback((control: AvatarControl) => {
    const emotion = control.emotion;
    const gesture = control.gesture;

    setData((previous) => ({
      ...previous,
      currentEmotion: emotion ?? previous.currentEmotion,
      currentGesture: gesture ?? previous.currentGesture,
      currentSpeech: control.speech ?? previous.currentSpeech,
    }));

    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: "AVATAR_CONTROL",
        emotion,
        gesture,
        text: control.speech,
        audio_url: control.audioUrl,
        features: control.features,
      }));
    }
  }, [socket]);

  const setHandPose = useCallback((hand: "left" | "right" | "both", pose: string) => {
    setData(prev => ({
      ...prev,
      handPose: {
        left: (hand === "left" || hand === "both") ? pose : prev.handPose?.left ?? "relaxed",
        right: (hand === "right" || hand === "both") ? pose : prev.handPose?.right ?? "relaxed",
      }
    }));
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: "FINGER_CONTROL", hand, pose }));
    }
  }, [socket]);

  const setFingerCurl = useCallback((hand: "left" | "right" | "both", finger: string, amount: number) => {
    setData(prev => {
      const leftCurls = { ...(prev.fingerCurls?.left || {}) };
      const rightCurls = { ...(prev.fingerCurls?.right || {}) };
      if (hand === "left" || hand === "both") leftCurls[finger] = amount;
      if (hand === "right" || hand === "both") rightCurls[finger] = amount;
      return {
        ...prev,
        fingerCurls: { left: leftCurls, right: rightCurls }
      };
    });
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: "FINGER_CONTROL", hand, curls: { [finger]: amount } }));
    }
  }, [socket]);

  return { data, avatarState, setAvatarState, sendCommand, controlAvatar, setHandPose, setFingerCurl };
};

const json = JSON; // Safety for minifiers if needed
