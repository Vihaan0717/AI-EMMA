import os
from datetime import datetime
from core.logger import get_logger

logger = get_logger("ObsidianAgent")

class ObsidianAgent:
    """
    JARVIS 2.0 Obsidian Integration Agent.
    Manages the connection between JARVIS's memory and an Obsidian vault.
    """
    def __init__(self, vault_path=None):
        # Default to a local directory if not provided
        self.vault_path = vault_path or os.environ.get("OBSIDIAN_VAULT_PATH", "memory/obsidian_vault")
        os.makedirs(self.vault_path, exist_ok=True)
        os.makedirs(os.path.join(self.vault_path, "Daily"), exist_ok=True)
        os.makedirs(os.path.join(self.vault_path, "Patterns"), exist_ok=True)
        os.makedirs(os.path.join(self.vault_path, "LTM"), exist_ok=True)
        logger.info(f"Obsidian Agent initialized at {self.vault_path}")

    def create_daily_note(self, summary, interactions):
        """Creates or updates the daily note with summaries and logs."""
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = os.path.join(self.vault_path, "Daily", f"{today}.md")

        content = f"# Daily Log: {today}\n\n"
        content += "## Summary\n"
        content += f"{summary}\n\n"
        content += "## Key Interactions\n"
        for inter in interactions:
            content += f"- **User:** {inter.get('user_input')}\n"
            content += f"  **Jarvis:** {inter.get('response')}\n"

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Daily note created: {filepath}")
        except Exception as e:
            logger.error(f"Failed to create daily note: {e}")

    def export_pattern(self, pattern_name, pattern_data):
        """Exports a learned pattern to a dedicated file."""
        filepath = os.path.join(self.vault_path, "Patterns", f"{pattern_name}.md")

        content = f"# Pattern: {pattern_name}\n\n"
        content += f"**Last Updated:** {datetime.now().isoformat()}\n\n"
        content += "## Data\n"
        if isinstance(pattern_data, dict):
            for k, v in pattern_data.items():
                content += f"- **{k}:** {v}\n"
        else:
            content += f"{pattern_data}\n"

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Pattern exported: {filepath}")
        except Exception as e:
            logger.error(f"Failed to export pattern: {e}")

    def update_ltm(self, topic, info):
        """Updates Long-Term Memory files in Obsidian."""
        filepath = os.path.join(self.vault_path, "LTM", f"{topic}.md")

        try:
            mode = "a" if os.path.exists(filepath) else "w"
            with open(filepath, mode, encoding="utf-8") as f:
                if mode == "w":
                    f.write(f"# Long-Term Memory: {topic}\n\n")
                f.write(f"- [{datetime.now().isoformat()}] {info}\n")
            logger.info(f"LTM updated: {filepath}")
        except Exception as e:
            logger.error(f"Failed to update LTM: {e}")
