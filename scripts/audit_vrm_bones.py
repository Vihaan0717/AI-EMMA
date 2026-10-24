import json
import struct
import os

def audit_vrm(model_path):
    print("="*60)
    print(f"AUDITING VRM: {os.path.basename(model_path)}")
    print("="*60)
    data = open(model_path, 'rb').read()
    magic, ver, length = struct.unpack('<III', data[:12])
    chunk_len, chunk_type = struct.unpack('<II', data[12:20])
    gltf = json.loads(data[20:20+chunk_len].decode('utf-8'))
    
    nodes = gltf.get('nodes', [])
    extensions = gltf.get('extensions', {})
    vrmc = extensions.get('VRMC_vrm', {})
    legacy_vrm = extensions.get('VRM', {})
    
    # 1. Spec Version
    if vrmc:
        spec = f"VRM 1.0 (VRMC_vrm specVersion {vrmc.get('specVersion')})"
        humanoid = vrmc.get('humanoid', {})
        human_bones = humanoid.get('humanBones', {}) # dict of boneName -> { node: int }
    elif legacy_vrm:
        spec = f"VRM 0.x (VRM specVersion {legacy_vrm.get('specVersion')})"
        humanoid = legacy_vrm.get('humanoid', {})
        raw_hb = humanoid.get('humanBones', [])
        human_bones = {b.get('bone'): {'node': b.get('node')} for b in raw_hb}
    else:
        spec = "Raw glTF (No VRM Extension)"
        human_bones = {}
        
    print(f"Specification: {spec}")
    print(f"Total glTF Nodes: {len(nodes)}")
    print(f"Mapped Humanoid Bones: {len(human_bones)}")
    
    # Required Humanoid Bones in VRM Spec
    required_bones = [
        'hips', 'spine', 'head',
        'leftUpperArm', 'leftLowerArm', 'leftHand',
        'rightUpperArm', 'rightLowerArm', 'rightHand',
        'leftUpperLeg', 'leftLowerLeg', 'leftFoot',
        'rightUpperLeg', 'rightLowerLeg', 'rightFoot'
    ]
    
    optional_bones = [
        'chest', 'upperChest', 'neck', 'leftEye', 'rightEye', 'jaw',
        'leftToes', 'rightToes', 'leftShoulder', 'rightShoulder',
        # Fingers Left
        'leftThumbMetacarpal', 'leftThumbProximal', 'leftThumbDistal',
        'leftIndexProximal', 'leftIndexIntermediate', 'leftIndexDistal',
        'leftMiddleProximal', 'leftMiddleIntermediate', 'leftMiddleDistal',
        'leftRingProximal', 'leftRingIntermediate', 'leftRingDistal',
        'leftLittleProximal', 'leftLittleIntermediate', 'leftLittleDistal',
        # Fingers Right
        'rightThumbMetacarpal', 'rightThumbProximal', 'rightThumbDistal',
        'rightIndexProximal', 'rightIndexIntermediate', 'rightIndexDistal',
        'rightMiddleProximal', 'rightMiddleIntermediate', 'rightMiddleDistal',
        'rightRingProximal', 'rightRingIntermediate', 'rightRingDistal',
        'rightLittleProximal', 'rightLittleIntermediate', 'rightLittleDistal'
    ]
    
    print("\n[1] REQUIRED BONES CHECK:")
    missing_required = []
    for b in required_bones:
        if b in human_bones:
            node_idx = human_bones[b].get('node')
            node_name = nodes[node_idx].get('name', f'node_{node_idx}') if node_idx is not None else 'N/A'
            print(f"  [OK] {b:<15} -> Node #{node_idx} ({node_name})")
        else:
            missing_required.append(b)
            print(f"  [MISSING] {b:<15}")
            
    print(f"\nRequired Bones Status: {'ALL PRESENT' if not missing_required else 'FAIL - Missing: ' + str(missing_required)}")
    
    print("\n[2] OPTIONAL & FINGER BONES CHECK:")
    present_optional = []
    missing_optional = []
    for b in optional_bones:
        if b in human_bones:
            present_optional.append(b)
        else:
            missing_optional.append(b)
    print(f"  Present: {len(present_optional)}/{len(optional_bones)}")
    if missing_optional:
        print(f"  Missing optional: {missing_optional}")
    else:
        print("  [OK] Full 54-bone humanoid skeleton complete including all 10 fingers & eyes!")

    print("\n[3] BONE ALIGNMENT & REST TRANSFORMS (Sample Hierarchies):")
    # Verify hips, upper arms, lower arms rest position/rotation
    sample_check = ['hips', 'spine', 'chest', 'leftUpperArm', 'rightUpperArm', 'leftLowerArm', 'rightLowerArm', 'leftUpperLeg', 'rightUpperLeg']
    for b in sample_check:
        if b in human_bones:
            idx = human_bones[b].get('node')
            n = nodes[idx]
            pos = n.get('translation', [0, 0, 0])
            rot = n.get('rotation', [0, 0, 0, 1])
            scale = n.get('scale', [1, 1, 1])
            print(f"  Bone: {b:<14} Pos: {[round(x, 4) for x in pos]} Rot(quat): {[round(x, 4) for x in rot]} Scale: {scale}")

    # Symmetry Check between Left and Right arms & legs
    print("\n[4] BILATERAL SYMMETRY ANALYSIS:")
    pairs = [
        ('leftUpperArm', 'rightUpperArm'),
        ('leftLowerArm', 'rightLowerArm'),
        ('leftUpperLeg', 'rightUpperLeg'),
        ('leftLowerLeg', 'rightLowerLeg')
    ]
    for left_b, right_b in pairs:
        if left_b in human_bones and right_b in human_bones:
            n_l = nodes[human_bones[left_b]['node']]
            n_r = nodes[human_bones[right_b]['node']]
            p_l = n_l.get('translation', [0,0,0])
            p_r = n_r.get('translation', [0,0,0])
            x_sym = abs(abs(p_l[0]) - abs(p_r[0])) < 0.005
            y_sym = abs(p_l[1] - p_r[1]) < 0.005
            z_sym = abs(p_l[2] - p_r[2]) < 0.005
            is_sym = x_sym and y_sym and z_sym
            print(f"  Pair {left_b} vs {right_b}: X-mirrored? {p_l[0]:.4f} vs {p_r[0]:.4f} | Y-aligned? {p_l[1]:.4f} vs {p_r[1]:.4f} -> {'SYMMETRIC [OK]' if is_sym else 'ASYMMETRIC'}")

models = [
    r'c:\Users\anger\Desktop\AI JARVIS\JARVIS_Project\frontend\public\avatars\vroid-studio-avatar.vrm',
    r'c:\Users\anger\Desktop\AI JARVIS\JARVIS_Project\frontend\public\avatars\jarvis-neural.vrm',
    r'c:\Users\anger\Desktop\AI JARVIS\JARVIS_Project\frontend\public\avatars\ava-custom.vrm',
    r'c:\Users\anger\Desktop\AI JARVIS\AvatarSample_D.vrm',
]

for m in models:
    if os.path.exists(m):
        audit_vrm(m)
    else:
        print(f"File not found: {m}")

