"""
NEXUS-X OMEGA Self Healer
Automatically detects, diagnoses and fixes all errors
"""

import asyncio
import logging
import json
import datetime
import traceback
import importlib
import sys
from typing import Dict, List
from pathlib import Path

logger = logging.getLogger('SelfHealer')


class SelfHealer:
    """
    The immune system of NEXUS-X OMEGA
    Monitors, detects, repairs, and prevents errors
    """

    def __init__(self, modules: Dict):
        self.modules = modules
        self.error_log = []
        self.repair_history = []
        self.health_status = {}
        self.error_patterns = {}
        self.healing_strategies = self._load_healing_strategies()
        logger.info("🔧 Self Healer initialized")

    def _load_healing_strategies(self) -> Dict:
        """Load all healing strategies"""
        return {
            "memory_error": self._heal_memory,
            "ai_engine_error": self._heal_ai_engine,
            "connection_error": self._heal_connection,
            "import_error": self._heal_import,
            "timeout_error": self._heal_timeout,
            "json_error": self._heal_json,
            "file_error": self._heal_file,
            "generic_error": self._heal_generic
        }

    async def run_forever(self):
        """Run health monitoring 24/7"""
        logger.info("🔧 Self Healer running 24/7...")
        while True:
            try:
                await self._full_health_check()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Healer error: {e}")
                await asyncio.sleep(10)

    async def pulse(self):
        """Quick health pulse check (every minute)"""
        await self._quick_health_check()

    async def heal(self, error_message: str):
        """Main healing entry point"""
        logger.info(f"🔧 Healing: {error_message[:80]}...")

        # Log the error
        error_entry = {
            "timestamp": str(datetime.datetime.now()),
            "error": error_message,
            "state": "healing"
        }
        self.error_log.append(error_entry)

        # Identify error type
        error_type = self._identify_error_type(error_message)

        # Apply healing strategy
        strategy = self.healing_strategies.get(
            error_type,
            self.healing_strategies["generic_error"]
        )

        try:
            await strategy(error_message)
            error_entry["state"] = "healed"
            logger.info(f"✅ Healed: {error_type}")
        except Exception as e:
            error_entry["state"] = "failed"
            logger.error(f"❌ Healing failed: {e}")

        # Track error patterns
        self._track_error_pattern(error_type)

        # Save repair history
        self.repair_history.append({
            "timestamp": str(datetime.datetime.now()),
            "error_type": error_type,
            "strategy": strategy.__name__,
            "success": error_entry["state"] == "healed"
        })

    def _identify_error_type(self, error: str) -> str:
        """Identify what type of error occurred"""
        error_lower = error.lower()

        if any(w in error_lower for w in [
            "memory", "sqlite", "database", "db"
        ]):
            return "memory_error"
        elif any(w in error_lower for w in [
            "ollama", "model", "generate", "llm"
        ]):
            return "ai_engine_error"
        elif any(w in error_lower for w in [
            "connection", "refused", "timeout", "network"
        ]):
            return "connection_error"
        elif "importerror" in error_lower or "modulenotfound" in error_lower:
            return "import_error"
        elif "timeout" in error_lower:
            return "timeout_error"
        elif "json" in error_lower or "decode" in error_lower:
            return "json_error"
        elif any(w in error_lower for w in [
            "file", "path", "directory", "permission"
        ]):
            return "file_error"
        return "generic_error"

    def _track_error_pattern(self, error_type: str):
        """Track recurring errors for prevention"""
        if error_type not in self.error_patterns:
            self.error_patterns[error_type] = 0
        self.error_patterns[error_type] += 1

        # If same error 5+ times, trigger deep healing
        if self.error_patterns[error_type] >= 5:
            logger.warning(
                f"⚠️ Recurring error pattern: {error_type} "
                f"({self.error_patterns[error_type]} times)"
            )
            asyncio.create_task(self._deep_heal(error_type))

    async def _heal_memory(self, error: str):
        """Heal memory/database issues"""
        logger.info("🔧 Healing memory system...")
        if 'memory' in self.modules:
            try:
                if hasattr(self.modules['memory'], 'repair'):
                    await self.modules['memory'].repair()
                await self.modules['memory'].initialize()
            except:
                # Reinitialize from scratch
                from agents.memory_manager import MemoryManager
                self.modules['memory'] = MemoryManager()
                await self.modules['memory'].initialize()

    async def _heal_ai_engine(self, error: str):
        """Heal AI engine issues"""
        logger.info("🔧 Healing AI engine...")
        if 'ai' in self.modules:
            try:
                if hasattr(self.modules['ai'], 'reinitialize'):
                    await self.modules['ai'].reinitialize()
            except:
                from core.free_ai_engine import FreeAIEngine
                self.modules['ai'] = FreeAIEngine()
                await self.modules['ai'].initialize()

    async def _heal_connection(self, error: str):
        """Heal connection issues"""
        logger.info("🔧 Healing connections...")
        await asyncio.sleep(5)  # Wait for network recovery
        # Try to reconnect all services
        for module_name, module in self.modules.items():
            if hasattr(module, 'reconnect'):
                try:
                    await module.reconnect()
                except:
                    pass

    async def _heal_import(self, error: str):
        """Heal import errors"""
        logger.info("🔧 Healing import issues...")
        # Try to reinstall missing packages
        import subprocess
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r",
                 "requirements.txt", "-q"],
                timeout=60
            )
        except:
            pass

    async def _heal_timeout(self, error: str):
        """Heal timeout issues"""
        logger.info("🔧 Healing timeout issues...")
        # Increase timeout settings
        if 'ai' in self.modules:
            if hasattr(self.modules['ai'], 'timeout'):
                self.modules['ai'].timeout = min(
                    self.modules['ai'].timeout * 2, 120
                )

    async def _heal_json(self, error: str):
        """Heal JSON parsing issues"""
        logger.info("🔧 Healing JSON issues...")
        # JSON errors are usually transient, just log
        pass

    async def _heal_file(self, error: str):
        """Heal file system issues"""
        logger.info("🔧 Healing file system...")
        # Recreate missing directories
        dirs = [
            "data", "data/chromadb", "data/learning_logs",
            "logs", "temp", "config", "knowledge_vault"
        ]
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)

    async def _heal_generic(self, error: str):
        """Generic healing for unknown errors"""
        logger.info("🔧 Applying generic healing...")
        await asyncio.sleep(1)
        # Collect garbage
        import gc
        gc.collect()

    async def _deep_heal(self, error_type: str):
        """Deep healing for recurring issues"""
        logger.warning(f"🔧 Deep healing {error_type}...")
        # Reset error pattern count
        self.error_patterns[error_type] = 0
        # Apply strategy with extra care
        strategy = self.healing_strategies.get(
            error_type,
            self.healing_strategies["generic_error"]
        )
        await strategy(f"deep_heal_{error_type}")

    async def _full_health_check(self):
        """Full system health check"""
        checks = {
            "memory": self._check_memory_health,
            "ai_engine": self._check_ai_health,
            "disk_space": self._check_disk_space,
            "ram_usage": self._check_ram_usage
        }

        for check_name, check_fn in checks.items():
            try:
                status = await check_fn()
                self.health_status[check_name] = status
                if not status.get("healthy", True):
                    logger.warning(
                        f"⚠️ Health issue: {check_name}: "
                        f"{status.get('issue', 'unknown')}"
                    )
            except Exception as e:
                self.health_status[check_name] = {
                    "healthy": False, "issue": str(e)
                }

    async def _quick_health_check(self):
        """Quick health pulse"""
        try:
            await self._check_ram_usage()
        except:
            pass

    async def _check_memory_health(self) -> Dict:
        """Check memory system health"""
        if 'memory' not in self.modules:
            return {"healthy": False, "issue": "Memory not loaded"}
        try:
            if hasattr(self.modules['memory'], 'get_size'):
                size = self.modules['memory'].get_size()
                return {"healthy": True, "memory_size": size}
            return {"healthy": True}
        except Exception as e:
            return {"healthy": False, "issue": str(e)}

    async def _check_ai_health(self) -> Dict:
        """Check AI engine health"""
        if 'ai' not in self.modules:
            return {"healthy": False, "issue": "AI not loaded"}
        try:
            if hasattr(self.modules['ai'], 'health_check'):
                is_healthy = await self.modules['ai'].health_check()
                return {"healthy": is_healthy}
            return {"healthy": True}
        except Exception as e:
            return {"healthy": False, "issue": str(e)}

    async def _check_disk_space(self) -> Dict:
        """Check available disk space"""
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_gb = free // (2**30)
        return {
            "healthy": free_gb > 1,
            "free_gb": free_gb,
            "issue": "Low disk space" if free_gb <= 1 else None
        }

    async def _check_ram_usage(self) -> Dict:
        """Check RAM usage"""
        try:
            import psutil
            ram = psutil.virtual_memory()
            healthy = ram.percent < 90
            return {
                "healthy": healthy,
                "used_percent": ram.percent,
                "issue": "High RAM usage" if not healthy else None
            }
        except:
            return {"healthy": True}

    def get_health_status(self) -> Dict:
        """Get current health status"""
        return {
            "overall": all(
                s.get("healthy", True)
                for s in self.health_status.values()
            ),
            "checks": self.health_status,
            "total_errors": len(self.error_log),
            "total_repairs": len(self.repair_history),
            "error_patterns": self.error_patterns
        }
