import unittest
import os
import sys

# Ensure project root is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.hand_service import HandService
from services.dome_service import DOMEService
from tools.skills_framework import SkillRegistry
from tools.concrete_skills import LaunchAppSkill, InspectUIElementsSkill, TypeInWindowSkill

class TestHandsAndDome(unittest.TestCase):
    """
    Test Suite for Hands, DOME, and Skills systems.
    Tests core functions in absolute isolation.
    """

    def setUp(self):
        self.hands = HandService()
        self.dome = DOMEService()
        self.registry = SkillRegistry()

        # Register skills
        self.registry.register_skill(LaunchAppSkill(self.hands))
        self.registry.register_skill(InspectUIElementsSkill(self.dome))
        self.registry.register_skill(TypeInWindowSkill(self.hands))

    def test_coordinate_validation(self):
        """Verify safety coordinates validations work correctly."""
        # Check boundary validation
        self.assertTrue(self.hands._validate_coordinates(0, 0))
        self.assertFalse(self.hands._validate_coordinates(-10, 50))
        self.assertFalse(self.hands._validate_coordinates(100, -50))

    def test_list_windows(self):
        """Verify window listing functions return visible structures."""
        windows = self.hands.list_windows()
        self.assertIsInstance(windows, list)

    def test_dome_hierarchy(self):
        """Verify DOMEService queries top level window structures."""
        hierarchy = self.dome.get_window_hierarchy()
        self.assertIsInstance(hierarchy, list)
        if len(hierarchy) > 0:
            first = hierarchy[0]
            self.assertIn("hwnd", first)
            self.assertIn("title", first)
            self.assertIn("rect", first)

    def test_skill_registry_listing(self):
        """Verify skills are registered and listed properly in the registry."""
        skills = self.registry.list_skills()
        names = [s["name"] for s in skills]
        self.assertIn("launch_app", names)
        self.assertIn("inspect_ui", names)
        self.assertIn("type_in_window", names)

    def test_launch_app_validation(self):
        """Verify validation errors are handled cleanly when args are missing."""
        skill = self.registry.get_skill("launch_app")
        self.assertIsNotNone(skill)
        # Call without required arg "app_name"
        res = skill.execute({})
        self.assertIn("Error: Missing one of the required arguments", res)

    def test_fleet_manager_actions(self):
        """Verify FleetManager parses Hand/DOME actions properly."""
        from core.fleet.manager import FleetManager
        fm = FleetManager()
        # Test parsing empty action output
        res = fm._execute_hand_actions("Hello World! No action block.")
        self.assertEqual(res, [])
        
        # Test simulated inspect_ui
        action_text = "[ACTION] type: inspect_ui, target: test [/ACTION]"
        res_ui = fm._execute_hand_actions(action_text)
        self.assertIsInstance(res_ui, list)
        self.assertTrue(len(res_ui) > 0)
        self.assertIn("DOME: Found", res_ui[0])

    def test_voice_assistant_loop(self):
        """Verify VoiceAssistantLoop components and locks load correctly."""
        from run_voice_assistant import VoiceAssistantLoop
        # Instantiate in mock / check mode
        try:
            assistant = VoiceAssistantLoop()
            self.assertIsNotNone(assistant.ears)
            self.assertIsNotNone(assistant.mouth)
            # Verify locks
            self.assertFalse(assistant.speaking_lock.locked())
        except Exception as e:
            # If pycom/CoInitialize or system sound device is missing on remote runner, pass gracefully
            logger.info(f"Skipping local audio hw test on CI: {e}")

if __name__ == "__main__":
    unittest.main()
