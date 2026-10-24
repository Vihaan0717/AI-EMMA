from typing import List, Optional
from pydantic import BaseModel, Field

class MessageContract(BaseModel):
    """
    The typed inter-agent protocol. 
    Agents communicate using this compact structure rather than raw context windows.
    """
    task_id: str
    sender: str
    receiver: str
    objective: str
    conclusion: str
    evidence: List[str] = Field(default_factory=list)
    uncertainty: str = ""
    assumptions: List[str] = Field(default_factory=list)
    unresolved_questions: List[str] = Field(default_factory=list)
    requested_action: str = ""
    provenance: str = ""
