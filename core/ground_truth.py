from core.metacognitive_state import OperationalState, MetacognitiveVariable, Provenance

class GroundTruthAPI:
    """
    Single authoritative interface for retrieving the verifiable OperationalState.
    """
    def __init__(self):
        self._history = []
        
    def get_current_state(self) -> OperationalState:
        state = OperationalState()
        
        # Mocking telemetry queries
        state.resource_state["cpu_pressure"] = MetacognitiveVariable(
            value="HIGH", 
            provenance=Provenance(source="os.psutil", confidence=1.0)
        )
        
        state.dependency_state["api_status"] = MetacognitiveVariable(
            value="DEGRADED", 
            provenance=Provenance(source="network.ping", confidence=1.0)
        )
        
        state.safety_state["sandbox_enabled"] = MetacognitiveVariable(
            value=True, 
            provenance=Provenance(source="security.sandbox.daemon", confidence=1.0)
        )
        
        state.contradiction_state["active_conflicts"] = MetacognitiveVariable(
            value=3, 
            provenance=Provenance(source="agent_bus.debate_monitor", confidence=0.95)
        )
        
        self._history.append(state)
        return state

    def verify_claim(self, claim_key: str, claim_value: str, category: str) -> bool:
        """
        Cross-checks an LLM claim against the ground truth.
        """
        state = self.get_current_state()
        category_dict = getattr(state, category, {})
        
        if claim_key in category_dict:
            actual_val = str(category_dict[claim_key].value)
            return actual_val.upper() == str(claim_value).upper()
        return False
