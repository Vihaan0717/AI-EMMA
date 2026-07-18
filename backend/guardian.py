"""
NEXUS-X ULTIMATE Guardian
Process Guardian - Ensures 24/7 uptime
(Renamed from watchdog.py to avoid module shadowing)
"""

import os
import sys
import time
import subprocess
import logging
import psutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("logs/guardian.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Guardian")

class ProcessGuardian:
    def __init__(self):
        self.root = Path(__file__).parent
        self.env = os.environ.copy()
        self.env["PYTHONPATH"] = f"{self.root};{self.root.parent}"
        
        # Perform clean sweep before starting
        self._clean_sweep()
        
        # Get the python executable (should be from .venv if activated)
        py_exe = sys.executable

        self.processes = {
            "MONGODB": {
                "cmd": [str(self.root / "mongodb" / "mongodb-win32-x86_64-windows-7.0.8" / "bin" / "mongod.exe"), "--dbpath", "data/mongodb", "--port", "27017", "--quiet"],
                "restart_delay": 5,
                "max_restarts": 10,
                "restarts": 0
            },
            # NEXUS_MAIN owns the brain AND the bridge (services/bridge_server.py on 0.0.0.0:8000).
            # This prevents the double-brain / double-Telegram-bot problem.
            "NEXUS_MAIN": {
                "cmd": [py_exe, "main.py"],
                "restart_delay": 5,
                "max_restarts": 10,
                "restarts": 0
            },
            "FLEET_DASHBOARD": {
                "cmd": [py_exe, "-m", "streamlit", "run", "../ui/fleet_dashboard.py", "--server.port", "8501", "--server.headless", "true"],
                "restart_delay": 10,
                "max_restarts": 5,
                "restarts": 0
            },
            "KNOWLEDGE_WATCHER": {
                "cmd": [py_exe, "core/fleet/obsidian_watcher.py"],
                "restart_delay": 5,
                "max_restarts": 5,
                "restarts": 0
            },
            "WHATSAPP_LISTENER": {
                "cmd": ["cmd", "/c", "set NODE_OPTIONS=--max-old-space-size=4096 && npm start"],
                "cwd": str(self.root.parent / "JARVIS-v2" / "arion" / "whatsapp"),
                "restart_delay": 15,
                "max_restarts": 999,  # Never give up on WhatsApp
                "restarts": 0
            }
        }
        self.active_procs = {}

    def _kill_proc_tree(self, pid, including_parent=True):
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    pass
            psutil.wait_procs(children, timeout=5)
            if including_parent:
                try:
                    parent.kill()
                    parent.wait(5)
                except psutil.NoSuchProcess:
                    pass
        except psutil.NoSuchProcess:
            pass
        except Exception as e:
            logger.debug(f"Kill tree error: {e}")

    def _clean_sweep(self):
        """Kills any process blocking port 8501 or orphan python instances."""
        logger.info("Performing pre-flight clean sweep...")
        try:
            if sys.platform == "win32":
                # 1. Clear lingering ports
                for port in ["8000", "8501", "27017"]:
                    self._clear_port(port)

                # 2. Kill WhatsApp-linked Chromium by tracing node.exe → chrome.exe tree
                # Child Chrome processes don't inherit cmdline args, so we hunt via parent tree.
                wa_node_pids = set()
                wa_chrome_pids = set()
                try:
                    # Find node.exe processes whose cwd contains the whatsapp directory
                    wa_path_marker = str(self.root / "JARVIS-v2" / "arion" / "whatsapp").lower()
                    for proc in psutil.process_iter(['pid', 'name', 'cwd', 'cmdline']):
                        try:
                            if proc.info['name'] and 'node' in proc.info['name'].lower():
                                cwd = (proc.info['cwd'] or '').lower()
                                cmdline = ' '.join(proc.info['cmdline'] or []).lower()
                                if 'whatsapp' in cwd or 'whatsapp' in cmdline or 'wwebjs' in cmdline:
                                    wa_node_pids.add(proc.pid)
                                    # Also mark all Chrome children of this node process
                                    for child in proc.children(recursive=True):
                                        if 'chrome' in child.name().lower():
                                            wa_chrome_pids.add(child.pid)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass

                    # Also find Chrome processes whose cmdline contains .wwebjs_auth
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        try:
                            if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                                cmdline = ' '.join(proc.info['cmdline'] or [])
                                if '.wwebjs_auth' in cmdline or 'wwebjs' in cmdline.lower():
                                    wa_chrome_pids.add(proc.pid)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass

                    # Kill all identified pids
                    for pid in wa_chrome_pids | wa_node_pids:
                        try:
                            psutil.Process(pid).kill()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                except Exception as e:
                    logger.debug(f"WhatsApp Chrome sweep error: {e}")

                # Still kill streamlit orphans from previous run
                subprocess.run("taskkill /F /IM streamlit.exe /T", shell=True, capture_output=True)


                # 3. Smash all locks
                logger.info("Smashing all session and database locks...")
                
                # MongoDB Lock
                mongo_lock = self.root / "data" / "mongodb" / "mongod.lock"
                if mongo_lock.exists(): 
                    try: mongo_lock.unlink()
                    except: pass
                
                # WhatsApp Locks
                session_dir = self.root / "JARVIS-v2" / "arion" / "whatsapp" / ".wwebjs_auth" / "session"
                auth_dir = self.root / "JARVIS-v2" / "arion" / "whatsapp" / ".wwebjs_auth"
                lock_files = ["lockfile", "DevToolsActivePort", "SingletonLock", "SingletonCookie"]
                
                for base_dir in [session_dir, auth_dir]:
                    if not base_dir.exists(): continue
                    for lock in lock_files:
                        lock_path = base_dir / lock
                        if lock_path.exists():
                            try: lock_path.unlink()
                            except: pass
                
                time.sleep(2) 

        except Exception as e:
            logger.debug(f"Clean sweep note: {e}")

    def _clear_port(self, port):
        """Clears a port using both psutil (surgical) and PowerShell (fallback)."""
        port = int(port)
        # 1. Surgical kill via psutil
        try:
            import psutil
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr.port == port and conn.status in ('LISTEN', 'ESTABLISHED'):
                    try:
                        p = psutil.Process(conn.pid)
                        logger.warning(f"[Guardian] Force-clearing port {port}: killing PID {conn.pid} ({p.name()})")
                        p.kill()
                        p.wait(timeout=3)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                        pass
        except Exception as e:
            logger.debug(f"psutil port clear error: {e}")

        # 2. PowerShell fallback
        try:
            cmd = f'powershell -Command "Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object {{ Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }}"'
            subprocess.run(cmd, shell=True, capture_output=True)
        except:
            pass

        # 3. Wait for OS to release the socket (TIME_WAIT)
        # IMPORTANT: do NOT use SO_REUSEADDR here — we want to test
        # the same conditions that uvicorn uses when it binds.
        import socket
        for _ in range(20):   # up to 10 seconds
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('0.0.0.0', port))
                s.close()
                logger.info(f"[Guardian] Port {port} confirmed free.")
                return  # Port is free!
            except OSError:
                time.sleep(0.5)
        logger.warning(f"[Guardian] Port {port} may still be busy after clearing.")

    def start_all(self):
        logger.info("Starting NEXUS-X ULTIMATE Guardian...")
        for name, cfg in self.processes.items():
            if name == "NEXUS_MAIN": self._clear_port("8000")
            if name == "FLEET_DASHBOARD": self._clear_port("8501")
            
            self._spawn(name)
            # Staggered startup to prevent RAM spike
            delay = 25 if name == "MONGODB" else 15
            logger.info(f"Waiting {delay}s for {name} to stabilize...")
            time.sleep(delay)

    def _spawn(self, name):
        cfg = self.processes[name]
        logger.info(f"Launching {name}...")
        try:
            # Build per-process environment
            proc_env = self.env.copy()
            proc_env.update(cfg.get("env", {}))
            # On Windows, we use CREATE_NO_WINDOW if we don't want popups, 
            # but for debugging it's better to let them run.
            proc = subprocess.Popen(
                cfg["cmd"],
                cwd=cfg.get("cwd", str(self.root)),
                env=proc_env
            )
            self.active_procs[name] = proc
        except Exception as e:
            logger.error(f"Failed to launch {name}: {e}")

    def monitor(self):
        logger.info("Monitoring processes...")
        start_times = {}  # Track when each process last started
        while True:
            try:
                for name, proc in list(self.active_procs.items()):
                    poll = proc.poll()
                    if poll is not None:
                        cfg = self.processes[name]
                        uptime = time.time() - start_times.get(name, time.time())
                        # If process ran > 60s before dying, reset its restart counter
                        if uptime > 60:
                            cfg["restarts"] = 0
                            logger.info(f"{name} ran for {uptime:.0f}s — resetting restart counter.")
                        logger.warning(f"{name} died (exit={poll}, restarts={cfg['restarts']}/{cfg['max_restarts']})")
                        if cfg["restarts"] < cfg["max_restarts"]:
                            cfg["restarts"] += 1
                            self._kill_proc_tree(proc.pid)
                            if name == "NEXUS_MAIN":
                                # Wait for process tree to fully die, THEN clear the port
                                time.sleep(2)
                                self._clear_port(8000)
                            if name == "FLEET_DASHBOARD": self._clear_port(8501)
                            
                            # WhatsApp lock wipe on restart
                            if name == "WHATSAPP_LISTENER":
                                self._wipe_whatsapp_locks()
                                
                            time.sleep(cfg["restart_delay"])
                            self._spawn(name)
                            start_times[name] = time.time()
                        else:
                            logger.error(f"{name} reached max restarts. Manual intervention needed.")
                            del self.active_procs[name]
                    else:
                        # Record start time on first healthy poll
                        if name not in start_times:
                            start_times[name] = time.time()

                # ── WHATSAPP HEARTBEAT WATCHDOG ──────────────────────────
                heartbeat_file = self.root / "JARVIS-v2" / "arion" / "data" / "bridge_queue" / "heartbeat.json"
                if heartbeat_file.exists():
                    try:
                        import json as _json
                        hb = _json.loads(heartbeat_file.read_text())
                        hb_age = time.time() - (hb.get("timestamp", 0) / 1000)
                        hb_status = hb.get("status", "unknown")
                        
                        # Grace periods: 5 mins for initializing (QR scan), 2 mins for online
                        grace_period = 300 if hb_status == "initializing" else 120
                        
                        if hb_age > grace_period and "WHATSAPP_LISTENER" in self.active_procs:
                            logger.warning(f"WhatsApp heartbeat stale ({hb_age:.0f}s, status={hb_status}). Force-restarting listener...")
                            proc = self.active_procs["WHATSAPP_LISTENER"]
                            self._kill_proc_tree(proc.pid)
                            self._wipe_whatsapp_locks()
                            time.sleep(3)
                            self._spawn("WHATSAPP_LISTENER")
                            start_times["WHATSAPP_LISTENER"] = time.time()
                            # Do NOT unlink, let the new process overwrite it
                    except Exception as hb_err:
                        logger.debug(f"Heartbeat check error: {hb_err}")

                time.sleep(10)  # Poll every 10s for faster reconnect
            except KeyboardInterrupt:
                logger.info("Shutting down Guardian...")
                self.stop_all()
                break
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(5)

    def _wipe_whatsapp_locks(self):
        try:
            session_dir = self.root / "JARVIS-v2" / "arion" / "whatsapp" / ".wwebjs_auth" / "session"
            auth_dir = self.root / "JARVIS-v2" / "arion" / "whatsapp" / ".wwebjs_auth"
            lock_files = ["lockfile", "DevToolsActivePort", "SingletonLock", "SingletonCookie"]
            for base_dir in [session_dir, auth_dir]:
                if not base_dir.exists(): continue
                for lock in lock_files:
                    lock_path = base_dir / lock
                    if lock_path.exists():
                        try: lock_path.unlink()
                        except: pass
            
            # Additional sweep for chrome processes
            subprocess.run("taskkill /F /IM chrome.exe /T", shell=True, capture_output=True)
        except Exception as e:
            logger.debug(f"WhatsApp wipe error: {e}")

    def stop_all(self):
        for name, proc in self.active_procs.items():
            logger.info(f"Stopping {name}...")
            self._kill_proc_tree(proc.pid)

if __name__ == "__main__":
    guardian = ProcessGuardian()
    guardian.start_all()
    guardian.monitor()
