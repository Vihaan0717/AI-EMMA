import logging
import os
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

logger = logging.getLogger("nexus.insight")

class InsightAgent:
    """
    NEXUS-X Insight Agent.
    Analyzes content patterns and behavioral trends to provide proactive suggestions.
    The 'Intuition' layer of the brain.
    """
    def __init__(self, brain=None):
        self.brain = brain
        self.behavior_db = "memory/behavior_habits.db"
        self.scholar_vault = "data/telugu_scholar_vault.json"
        
    async def generate_daily_insights(self) -> List[Dict]:
        """Analyzes recent logs to find patterns and suggest actions."""
        insights = []
        
        # 1. Analyze Behavioral Trends
        behavior_trends = self._analyze_behavior_patterns()
        if behavior_trends:
            insights.extend(behavior_trends)
            
        # 1.5. Analyze Social Media Preferences & Trends
        social_trends = self._analyze_social_patterns()
        if social_trends:
            insights.extend(social_trends)
            
        # 2. Analyze Linguistic Evolution
        linguistic_trends = self._analyze_linguistic_patterns()
        if linguistic_trends:
            insights.extend(linguistic_trends)
            
        # 3. Analyze Psychological Shifts
        psyche_trends = self._analyze_psyche_patterns()
        if psyche_trends:
            insights.extend(psyche_trends)
            
        # 4. Analyze Notifications (WhatsApp)
        notif_insights = await self._analyze_notifications()
        if notif_insights:
            insights.extend(notif_insights)
            
        return insights

    def _analyze_psyche_patterns(self) -> List[Dict]:
        """Detects psychological trends and cognitive load issues."""
        profile_path = "memory/psyche_profile.json"
        if not os.path.exists(profile_path): return []
        
        try:
            with open(profile_path, "r") as f:
                profile = json.load(f)
            
            history = profile.get("history", [])
            if not history: return []
            
            # Check for high cognitive load
            recent_load = sum(h.get("complexity", 0) for h in history[-5:]) / 5
            if recent_load > 2.5:
                return [{
                    "type": "cognitive_load_alert",
                    "content": "I've detected a high cognitive load in your recent interactions.",
                    "suggestion": "You might be overworking. I recommend a 15-minute 'Stoic Reflection' or a Flow-state reset. Should I schedule a break?",
                    "meta": {"load": recent_load}
                }]
            return []
        except Exception as e:
            logger.error(f"Psyche analysis failed: {e}")
            return []

    def _analyze_behavior_patterns(self) -> List[Dict]:
        """Detects recurring app usage or interest spikes."""
        if not os.path.exists(self.behavior_db): return []
        
        try:
            conn = sqlite3.connect(self.behavior_db)
            c = conn.cursor()
            
            # Find top interests in the last 24 hours
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            c.execute("SELECT app_package, COUNT(*), SUM(dwell_time) FROM habits WHERE timestamp > ? GROUP BY app_package ORDER BY 3 DESC", (yesterday,))
            top_apps = c.fetchall()
            
            insights = []
            for app, count, total_time in top_apps[:3]:
                if total_time > 3600: # Over an hour
                    insights.append({
                        "type": "behavioral_pattern",
                        "content": f"I've noticed you've spent significant time on {app} today.",
                        "suggestion": f"Should I gather some research notes or organize your tasks related to {app}?",
                        "meta": {"app": app, "time_spent": total_time}
                    })
            
            conn.close()
            return insights
        except Exception as e:
            logger.error(f"Behavioral analysis failed: {e}")
            return []

    def _analyze_linguistic_patterns(self) -> List[Dict]:
        """Detects shifts in Telugu dialect or register usage."""
        if not os.path.exists(self.scholar_vault): return []
        
        try:
            with open(self.scholar_vault, "r", encoding="utf-8") as f:
                vault = json.load(f)
            
            terms = vault.get("terms", {})
            if not terms: return []
            
            # Count dialects
            dialect_counts = {}
            for term in terms.values():
                d = term.get("dialect")
                dialect_counts[d] = dialect_counts.get(d, 0) + 1
            
            # Find dominant dialect
            if dialect_counts:
                dominant = max(dialect_counts, key=dialect_counts.get)
                if dialect_counts[dominant] > 5:
                    return [{
                        "type": "linguistic_shift",
                        "content": f"Your vocabulary is trending strongly towards {dominant}.",
                        "suggestion": f"I can start stylizing my responses with more {dominant} idioms to match your vibe. Should I?",
                        "meta": {"dialect": dominant}
                    }]
            return []
        except Exception as e:
            logger.error(f"Linguistic analysis failed: {e}")
            return []

    async def propose_action(self, insight: Dict):
        """Asks the user for permission to take a proactive action."""
        if not self.brain: return
        
        # Use the Guardian Secure-Handshake for proactive actions
        approved = await self.brain.request_guardian_approval(
            event_type="PROACTIVE_ACTION",
            details=f"{insight['content']}\nSuggestion: {insight['suggestion']}"
        )
        
        if approved:
            await self._execute_action(insight)

    async def _execute_action(self, insight: Dict):
        """Executes the approved action."""
        logger.info(f"Executing proactive action: {insight['type']}")
        
        if insight["type"] == "linguistic_shift":
            # Update the preferred dialect in the Brain's context or persona
            dialect = insight["meta"]["dialect"]
            # Logic to set system-wide dialect preference
            pass
        elif insight["type"] == "behavioral_pattern":
            # Launch a search mission or create a reminder
            pass
            
    async def _analyze_notifications(self) -> List[Dict]:
        """Summarizes unread WhatsApp/Instagram messages."""
        # For now, we mock the retrieval. In full implementation, we'd query the MessageBus or DB.
        # This is the 'Notification Summary' requested by the user.
        return [{
            "type": "notification_summary",
            "content": "You have 5 unread messages on WhatsApp and 2 on Instagram.",
            "suggestion": "Should I read them out to you and tell you who sent them?",
            "meta": {"whatsapp_count": 5, "instagram_count": 2}
        }]

    def _analyze_social_patterns(self) -> List[Dict]:
        """Analyzes Instagram likes, reels, and feed posts to identify trends and preferences."""
        import re
        insights_path = "memory/social_insights.json"
        profile_path = "memory/psyche_profile.json"
        
        if not os.path.exists(insights_path):
            return []
            
        try:
            with open(insights_path, "r", encoding="utf-8") as f:
                insights_data = json.load(f)
                
            liked_items = insights_data.get("liked_items", [])
            if not liked_items:
                return []
                
            # Count common words/tags in captions
            word_counts = {}
            reels_count = 0
            feed_count = 0
            
            for item in liked_items:
                caption = item.get("caption") or ""
                product_type = item.get("product_type") or "feed"
                
                if product_type == "clips":
                    reels_count += 1
                else:
                    feed_count += 1
                    
                # Simple tokenization of words
                words = re.findall(r'#\w+|\b\w{4,}\b', caption.lower())
                for w in words:
                    word_counts[w] = word_counts.get(w, 0) + 1
                    
            if not word_counts:
                return []
                
            # Find top 3 trending tags/topics liked by user
            top_trends = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            top_tags = [t[0] for t in top_trends]
            
            # Formulate dynamic psyche profile update
            if os.path.exists(profile_path):
                with open(profile_path, "r", encoding="utf-8") as f:
                    profile = json.load(f)
                
                if "history" not in profile:
                    profile["history"] = []
                    
                # Update history with social interest shift
                profile["history"].append({
                    "timestamp": datetime.now().isoformat(),
                    "sentiment": "Interested",
                    "complexity": 0.7,
                    "detected_need": f"Social media focus: {', '.join(top_tags)}"
                })
                
                # Save updated profile
                with open(profile_path, "w", encoding="utf-8") as f:
                    json.dump(profile, f, indent=4)
                    
            # Propose dynamic suggestion
            dominant_format = "Reels" if reels_count > feed_count else "Feed Posts"
            return [{
                "type": "instagram_trend_insight",
                "content": f"I analyzed your Instagram activity. You've been liking a lot of {dominant_format} about: {', '.join(top_tags)}.",
                "suggestion": f"I've updated your dynamic psyche profile to focus more on {top_tags[0]}. Should I research new trends in this area?",
                "meta": {"trends": top_tags, "dominant_format": dominant_format}
            }]
            
        except Exception as e:
            logger.error(f"Instagram trend analysis failed: {e}")
            return []

    async def get_daily_greeting(self) -> str:
        """Generates a warm, proactive greeting with a summary of the day."""
        # Fetch data from Finance and DailyNote agents via brain
        finance_summary = "No data"
        daily_goals = "None"
        
        if self.brain:
            if hasattr(self.brain, 'finance'):
                finance_summary = str(self.brain.finance.get_summary())
            if hasattr(self.brain, 'daily_note'):
                daily_goals = str(self.brain.daily_note.get_today_summary()["goals"])

        prompt = f"""
Generate a warm, proactive morning greeting for 'Boss'.
Finance Summary: {finance_summary}
Daily Goals: {daily_goals}
Current Time: {datetime.now().strftime("%I:%M %p")}

The greeting should be in Tenglish (Telugu + English), sound like a personal assistant who cares about efficiency and goals.
Example: 'Good morning Boss! Ippude 7 ayyindi. Today we have 3 goals, and your spending is on track. EMI due date is coming up!'
"""
        return await self.brain.ai.generate(prompt=prompt, system="You are JARVIS, a proactive assistant.")
