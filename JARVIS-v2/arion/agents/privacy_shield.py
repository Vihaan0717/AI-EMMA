"""
Privacy Shield — ARION's Loyalty Layer.

Protects the owner's personal information from contacts.
Classifies sensitivity in 4 tiers.
Deflects naturally. Alerts owner. Never exposes private data.
"""

import random
import re
import time
from typing import Optional
from core.base_agent import BaseAgent
from core.message_bus import Channel, Message


class PrivacyShield(BaseAgent):

    OWNER_JID = "919154716156@c.us"

    # ── Pending permissions: contact → {topic, expires_at} ──────────────────
    _pending_permissions: dict = {}
    _granted_permissions: dict = {}  # contact → [topics]

    # ── Sensitivity Map ──────────────────────────────────────────────────────
    TIERS = {

        1: {
            # Casual personal — ARION can answer vaguely from known context
            "label": "casual_personal",
            "keywords": [
                "what are you doing", "how are you", "you busy",
                "chilling", "what's up", "em chesthunnav",
                "you free", "mood emi"
            ],
            "action": "answer_vaguely",
            "notify": False,
            "deflections": []  # ARION answers, just not with specifics
        },

        2: {
            # Personal — deflect + silent owner notification
            "label": "personal",
            "keywords": [
                "your family", "amma", "nanna", "sister", "brother",
                "akka", "anna", "chelli", "tammudu",
                "where do you live", "your house", "home",
                "girlfriend", "boyfriend", "relationship", "love life",
                "who are your friends", "your friends",
                "health", "doctor", "hospital", "sick",
                "your plans", "weekend plans", "personal life"
            ],
            "action": "deflect",
            "notify": True,
            "escalate": False,
            "deflections": [
                "haha personal question ra 😏 why?",
                "arey naaku thelidu bro, topic change cheyyi 😂",
                "nenu cheppanu ra adhi 😎",
                "naake thelidu bro 🤷",
                "emanna cheppali ani ledu naku ra 😂"
            ]
        },

        3: {
            # Sensitive — hard block + owner permission request
            "label": "sensitive",
            "keywords": [
                "address", "exact location", "where exactly",
                "phone number", "contact number", "number ento",
                "project", "work project", "client", "your company",
                "salary", "income", "how much you earn", "pay",
                "personal details", "id proof", "aadhaar",
                "daily routine", "schedule", "when do you",
                "what time do you", "sleep time", "wake up"
            ],
            "action": "block_and_request_permission",
            "notify": True,
            "escalate": False,
            "deflections": [
                "bro that's private ra 😅",
                "nenu cheppanu ra adhi 😂",
                "naaku adi cheppali ani ledu bhai 🙏",
                "private ga undi ra adhi, ask cheyyakku 😐"
            ]
        },

        4: {
            # Critical — full shutdown, loud alert
            "label": "critical",
            "keywords": [
                "password", "otp", "one time password",
                "bank", "account number", "bank account",
                "send money", "upi", "gpay", "phonepe", "paytm",
                "transfer", "transaction",
                "credit card", "debit card", "cvv", "card number",
                "pin", "mpin", "atm pin",
                "social security", "pan card", "passport number"
            ],
            "action": "shutdown_and_alert",
            "notify": True,
            "escalate": True,
            "deflections": [
                "bro no. not happening. 🚫",
                "nenu adi cheppanu, em aipoindi neeku? 😐",
                "100% no ra. 🙅",
                "adhi nenu share cheyyanu. period. 🚫"
            ]
        }
    }

    def __init__(self):
        super().__init__("PrivacyShield", [Channel.PRIVACY])

    async def run_loop(self):
        while self.running:
            msg = await self.get_next_message(timeout=0.5)
            if msg:
                await self.handle_message(msg)

    async def handle_message(self, message: Message):
        if message.action == "check_privacy":
            result = self.check(
                text=message.payload.get("text", ""),
                semantic=message.payload.get("semantic_english", ""),
                contact=message.payload.get("contact", ""),
                is_owner=message.payload.get("is_owner", False)
            )
            if message.requires_response:
                await self.respond_to(message, "privacy_result", result)

        elif message.action == "grant_permission":
            # Owner sends "allow [contact] [topic]"
            contact = message.payload.get("contact", "")
            topic = message.payload.get("topic", "all")
            self._grant_permission(contact, topic)

    # ── Core Check ───────────────────────────────────────────────────────────

    def check(
        self,
        text: str,
        semantic: str,
        contact: str,
        is_owner: bool
    ) -> dict:
        """
        Returns privacy decision for this message.
        """

        # Owner always gets through
        if is_owner:
            return {
                "safe": True, "tier": 0,
                "action": "allow", "contact": contact
            }

        check_text = (text + " " + semantic).lower()

        # Check granted permissions first
        if self._has_permission(contact, check_text):
            return {
                "safe": True, "tier": 0,
                "action": "allow_by_permission", "contact": contact
            }

        # Scan tiers from most critical → least
        for tier_num in [4, 3, 2, 1]:
            tier = self.TIERS[tier_num]
            for keyword in tier["keywords"]:
                if keyword in check_text:
                    return {
                        "safe": False,
                        "tier": tier_num,
                        "label": tier["label"],
                        "matched_keyword": keyword,
                        "action": tier["action"],
                        "deflection": random.choice(tier["deflections"])
                        if tier["deflections"] else "",
                        "notify_owner": tier["notify"],
                        "escalate": tier.get("escalate", False),
                        "contact": contact,
                        "original_text": text
                    }

        return {"safe": True, "tier": 0, "action": "allow", "contact": contact}

    # ── Alert Builder ─────────────────────────────────────────────────────────

    def build_owner_alert(self, result: dict) -> str:
        tier = result["tier"]
        contact = result["contact"]
        keyword = result["matched_keyword"]
        text = result["original_text"]

        if result.get("escalate"):
            return (
                f"🚨 *CRITICAL PRIVACY ALERT*\n"
                f"──────────────────\n"
                f"Contact: *{contact}*\n"
                f"Asked about: `{keyword}`\n"
                f"Their exact message:\n_{text}_\n\n"
                f"I *blocked* this completely.\n"
                f"Reply `allow {contact} {keyword}` only if you trust them."
            )
        elif tier == 3:
            return (
                f"🔒 *Privacy Block — Sensitive*\n"
                f"──────────────────\n"
                f"Contact: *{contact}*\n"
                f"Topic: `{keyword}`\n"
                f"Message: _{text}_\n\n"
                f"I deflected. To allow:\n"
                f"Reply `allow {contact} {keyword}`"
            )
        else:
            return (
                f"🔔 *Privacy Notice*\n"
                f"Contact: *{contact}* asked about `{keyword}`\n"
                f"Message: _{text}_\n"
                f"I deflected casually."
            )

    # ── Permission Management ─────────────────────────────────────────────────

    def _grant_permission(self, contact: str, topic: str):
        if contact not in self._granted_permissions:
            self._granted_permissions[contact] = []
        self._granted_permissions[contact].append(topic.lower())
        print(
            f"[PrivacyShield] ✅ Permission granted: "
            f"{contact} → {topic}", flush=True
        )

    def _has_permission(self, contact: str, text: str) -> bool:
        granted = self._granted_permissions.get(contact, [])
        if "all" in granted:
            return True
        return any(g in text for g in granted)

    def parse_owner_permission_command(self, text: str) -> Optional[dict]:
        """
        Parses owner messages like:
        "allow 91xxxx@c.us address"
        "allow Rahul family questions"
        """
        match = re.match(
            r"allow\s+(\S+)\s+(.+)", text.strip(), re.IGNORECASE
        )
        if match:
            return {
                "contact": match.group(1).strip(),
                "topic": match.group(2).strip()
            }
        return None
