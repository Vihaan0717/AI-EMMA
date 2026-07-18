import logging
from typing import Dict, Any
from tools.skills_framework import BaseSkill
from services.hand_service import HandService
from services.dome_service import DOMEService

logger = logging.getLogger("ConcreteSkills")

class LaunchAppSkill(BaseSkill):
    """Skill to safely open an application via cmd/start."""
    def __init__(self, hand_service: HandService):
        super().__init__(
            name="launch_app",
            description="Launches an OS application safely by name.",
            required_args=["app_name"]
        )
        self.hands = hand_service

    def run(self, args: Dict[str, Any]) -> str:
        return self.hands.open_app(args["app_name"])

class InspectUIElementsSkill(BaseSkill):
    """Skill to scan all child controls/windows on the desktop using DOMEService."""
    def __init__(self, dome_service: DOMEService):
        super().__init__(
            name="inspect_ui",
            description="Queries the Desktop Object Model tree of active windows.",
            required_args=[]
        )
        self.dome = dome_service

    def run(self, args: Dict[str, Any]) -> str:
        hierarchy = self.dome.get_window_hierarchy()
        output = [f"Found {len(hierarchy)} top-level windows:"]
        for idx, win in enumerate(hierarchy[:10]):
            output.append(f" {idx+1}. [{win['hwnd']}] Title: '{win['title']}' (Class: {win['class']})")
        if len(hierarchy) > 10:
            output.append(f"... and {len(hierarchy) - 10} more.")
        return "\n".join(output)

class TypeInWindowSkill(BaseSkill):
    """Skill to focus a window and type text safely."""
    def __init__(self, hand_service: HandService):
        super().__init__(
            name="type_in_window",
            description="Focuses/Maximizes a window and types requested text.",
            required_args=["window_title", "text_to_type"]
        )
        self.hands = hand_service

    def run(self, args: Dict[str, Any]) -> str:
        title = args["window_title"]
        text = args["text_to_type"]
        focus_res = self.hands.maximize_window(title)
        if "No window found" in focus_res:
            return focus_res
        
        # Type the text safely
        type_res = self.hands.type_text(text)
        return f"{focus_res}\nStatus: {type_res}"
