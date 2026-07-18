import json
import os
import logging
from pathlib import Path
from typing import Set, Dict, List

logger = logging.getLogger("PrivacyGuard")

class PrivacyGuard:
    """
    The Gatekeeper for JARVIS.
    Controls who is allowed to interact with the neural core.
    """
    def __init__(self):
        self.data_path = Path("data/privacy_permissions.json")
        self._ensure_data()
        self.authorized_users = self._load_permissions()
        
        # Always allow the admin
        self.admin_number = os.getenv("ADMIN_NUMBER", "").strip()
        if self.admin_number:
            self.authorized_users.add(self.admin_number)
            # Handle WhatsApp JID format
            if "@" not in self.admin_number:
                self.authorized_users.add(f"{self.admin_number}@c.us")
                self.authorized_users.add(f"{self.admin_number}@s.whatsapp.net")
        
        # Explicitly allow local/bridge owner identity
        self.authorized_users.add("Owner")
        self.authorized_users.add("owner")

    def _ensure_data(self):
        os.makedirs(self.data_path.parent, exist_ok=True)
        if not self.data_path.exists():
            with open(self.data_path, "w") as f:
                json.dump({"authorized": []}, f)

    def _load_permissions(self) -> Set[str]:
        try:
            with open(self.data_path, "r") as f:
                data = json.load(f)
                return set(data.get("authorized", []))
        except:
            return set()

    def _save_permissions(self):
        try:
            with open(self.data_path, "w") as f:
                json.dump({"authorized": list(self.authorized_users)}, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save permissions: {e}")

    def is_authorized(self, user_id: str) -> bool:
        """Check if a user (JID or phone) is allowed to talk to JARVIS."""
        return user_id in self.authorized_users

    def authorize(self, user_id: str):
        """Grant access to a user."""
        self.authorized_users.add(user_id)
        self._save_permissions()
        logger.info(f"User {user_id} has been AUTHORIZED.")

    def revoke(self, user_id: str):
        """Revoke access from a user."""
        if user_id in self.authorized_users and user_id != self.admin_number:
            self.authorized_users.remove(user_id)
            self._save_permissions()
            logger.info(f"User {user_id} access REVOKED.")

    def get_admin(self) -> str:
        return self.admin_number
