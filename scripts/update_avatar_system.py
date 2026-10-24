import re

# 1. Update useJarvisSocket.ts
socket_path = r'c:\Users\anger\Desktop\AI JARVIS\JARVIS_Project\frontend\src\hooks\useJarvisSocket.ts'
with open(socket_path, 'r', encoding='utf-8') as f:
    socket_content = f.read()

new_ai_response = '''          case "AI_RESPONSE":
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
                seiza: "seiza", kneel: "seiza",
                agura: "agura", cross_legged: "agura",
                idle: "idle", relaxed_standing: "idle",
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
            break;'''

socket_content = re.sub(r'case "AI_RESPONSE":[\s\S]*?break;', new_ai_response.strip(), socket_content)
with open(socket_path, 'w', encoding='utf-8') as f:
    f.write(socket_content)
print("Updated useJarvisSocket.ts")

# 2. Update AvatarDirector.tsx
director_path = r'c:\Users\anger\Desktop\AI JARVIS\JARVIS_Project\frontend\src\components\AvatarDirector.tsx'
with open(director_path, 'r', encoding='utf-8') as f:
    director_content = f.read()

new_gestures = '''const gestures = [
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
  { id: "dance", label: "Dance" },
] as const;'''

director_content = re.sub(r'const gestures = \[[\s\S]*?\] as const;', new_gestures, director_content)
with open(director_path, 'w', encoding='utf-8') as f:
    f.write(director_content)
print("Updated AvatarDirector.tsx")
