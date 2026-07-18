# Case Study: Langchain & VRM Avatar WebSocket Thread Collision

**Date:** April 2026
**Subject:** Resolving spurious `[Errno 11001] getaddrinfo failed` errors caused by concurrency conflicts between 3D VRM interface loops and Langchain architectures on Windows.

## 1. The Symptom
During routine integration testing of the JARVIS-X Hybrid Architecture, the system successfully loaded local inference models (Ollama/whisper) but repeatedly failed when issuing cloud-bound API calls to Google's Gemini servers via the UI. 
The logged error was:
```
ERROR | ResearchAgent | Langchain Cloud connection failed: [Errno 11001] getaddrinfo failed.
```
Curiously, running the exact same Gemini authentication script (`test_gemini.py`) explicitly outside the JARVIS boot cycle resulted in a fast, 100% successful connection. The local network environment was perfectly healthy, leaving the application layer as the culprit.

## 2. The Architecture 
The JARVIS-X system utilizes a highly concurrent pipeline:
- **The Avatar Server (`core/avatar_server.py`)**: Runs an actively polling `asyncio` Event Loop executing Pythons' `websockets` engine at 30+ frames per second to stream live face-tracking data to the React (Three.js/VRM) frontend.
- **The Cloud Brain (`agents/research_agent.py`)**: Designed originally using `langchain_google_genai`, which wraps the `google-generativeai` SDK.

## 3. Root Cause Analysis
The conflict originated from the intersection of **Thread Contexts** and **Asynchronous Event Loops**. 

When a user submitted a command via the UI (e.g., `> hi jarvis`), the Avatar Server received the WebSocket payload and spawned a detached Python thread (`threading.Thread(target=run_ai)`) to prevent blocking the high-refresh VRM tracking loop. 
However, Langchain's Google implementations inherently rely on `grpcio` (gRPC) rather than standard HTTP/1.1 for transport. 

When gRPC attempted to resolve the `googleapis.com` hostname using Windows Kernel's `getaddrinfo` API, it realized it was executing inside a detached child thread that lacked an associated asynchronous loop context. The gRPC resolver context forcefully dropped the connection attempt to protect against memory deadlocks, falsely bubbling up a `DNS Resolution Failure` (`11001`) to the Python surface layer.

**In summary:** The intense, high-frequency async demands of keeping the VRM model perfectly in sync physically conflicted with Langchain's highly sensitive background Thread resolution requirements.

## 4. The Engineering Fix
Rather than re-architecting the entire WebSocket lifecycle (which would severely degrade the Avatar's frame rate and lip-sync capabilities), we aggressively pruned the dependency tree:

1. **Decoupling from the Framework:** We stripped away the heavy `langchain_google_genai` dependency inside the `ResearchAgent`'s fallback sequence.
2. **Implementing Pure REST:** We replaced the complex gRPC bindings with standard, thread-safe `requests.post()` calls. The pure HTTP/1.1 transport (`urllib3`) operates natively and safely across any Python thread without relying on the Host's event loop structure.

**The Result:** The Avatar maintains its fluid 60FPS asynchronous frame rate to the frontend, and the backend HTTP threads cleanly map their sockets to the Cloud APIs without triggering Windows threading exceptions.
