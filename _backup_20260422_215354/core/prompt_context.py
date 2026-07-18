from core.session_state import SessionState
from context.context_assembler import context_assembler
from services.data_layer import data_layer


class PromptContextBuilder:
    """Builds normalized session state for the local and cloud brains."""

    def build(self, user_input: str, memory_context: str, channel: str = "voice") -> SessionState:
        runtime = context_assembler.load_runtime_context()
        persona_style = data_layer.preferences.get(
            "persona_style",
            default="professional, witty, calm, supportive",
        )

        session = SessionState(
            channel=channel,
            user_input=user_input,
            active_app=runtime.get("active_app", "Unknown"),
            presence_status=runtime.get("presence_status", "Unknown"),
            user_idle_seconds=int(runtime.get("user_idle_seconds", 0) or 0),
            memory_context=memory_context,
            prompt_context=context_assembler.build_prompt_context(),
            persona_style=persona_style,
            metadata={"runtime": runtime},
        )
        return session


prompt_context_builder = PromptContextBuilder()
