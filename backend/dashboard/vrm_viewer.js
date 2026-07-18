import * as THREE from 'https://unpkg.com/three@0.146.0/build/three.module.js';
import { GLTFLoader } from 'https://unpkg.com/three@0.146.0/examples/jsm/loaders/GLTFLoader.js';
import { VRMLoaderPlugin } from 'https://unpkg.com/@pixiv/three-vrm@1.0.9/lib/three-vrm.module.js';

let currentVrm = null;

// Initialize Three.js scene
const canvas = document.getElementById('vrm-canvas');
const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);

const scene = new THREE.Scene();

// Add camera
const camera = new THREE.PerspectiveCamera(30, window.innerWidth / window.innerHeight, 0.1, 20);
camera.position.set(0, 1.4, 2.5); // Position to focus on upper body/face

// Add lighting
const light = new THREE.DirectionalLight(0xffffff, 1.2);
light.position.set(1.0, 1.0, 1.0).normalize();
scene.add(light);
const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
scene.add(ambientLight);

// Load VRM model
const loader = new GLTFLoader();
loader.crossOrigin = 'anonymous';
loader.register((parser) => new VRMLoaderPlugin(parser));

loader.load(
    'assets/JarvisVrmm.vrm', // We will load JarvisVrmm.vrm for now
    (gltf) => {
        const vrm = gltf.userData.vrm;
        scene.add(vrm.scene);
        currentVrm = vrm;
        
        // Face the camera initially
        vrm.scene.rotation.y = Math.PI;

        console.log("VRM Avatar Loaded successfully!");
    },
    (progress) => console.log('Loading model...', 100.0 * (progress.loaded / progress.total), '%'),
    (error) => console.error(error)
);

// Animation Loop
const clock = new THREE.Clock();
function animate() {
    requestAnimationFrame(animate);
    const deltaTime = clock.getDelta();
    
    if (currentVrm) {
        currentVrm.update(deltaTime);
    }
    
    renderer.render(scene, camera);
}
animate();

// Handle Window Resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// WebSocket for Motion Mimicry
const ws = new WebSocket('ws://localhost:8001');

ws.onopen = () => {
    console.log("VRM Motion WebSocket Connected.");
};

ws.onmessage = (event) => {
    if (!currentVrm) return;
    
    try {
        const data = JSON.parse(event.data);
        
        // Data format expects { boneName: {x, y, z, w}, blendshapes: { name: value } }
        // Apply Bone Rotations (DigiHuman mapping)
        if (data.bones) {
            for (const [boneName, rotation] of Object.entries(data.bones)) {
                const node = currentVrm.humanoid.getRawBoneNode(boneName);
                if (node) {
                    node.quaternion.set(rotation.x, rotation.y, rotation.z, rotation.w);
                }
            }
        }
        
        // Apply Blendshapes (Facial expressions)
        if (data.blendshapes && currentVrm.expressionManager) {
            for (const [shapeName, value] of Object.entries(data.blendshapes)) {
                currentVrm.expressionManager.setValue(shapeName, value);
            }
            currentVrm.expressionManager.update();
        }
    } catch (e) {
        console.error("Error applying motion data:", e);
    }
};
