from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class CandidateManifest:
    candidate_id: str
    hypothesis_id: str
    parent_commit: str
    target_files: List[str]
    modified_files: List[str]
    created_files: List[str]
    deleted_files: List[str]
    generator: str
    analysis_version: str
    status: str # e.g., GENERATED, REJECTED, READY_FOR_VALIDATION
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "hypothesis_id": self.hypothesis_id,
            "parent_commit": self.parent_commit,
            "target_files": self.target_files,
            "modified_files": self.modified_files,
            "created_files": self.created_files,
            "deleted_files": self.deleted_files,
            "generator": self.generator,
            "analysis_version": self.analysis_version,
            "status": self.status
        }

@dataclass
class CandidatePatch:
    relative_path: str
    content: str
