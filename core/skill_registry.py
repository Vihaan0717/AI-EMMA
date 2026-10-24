import sqlite3
import json
import os
from typing import List, Optional
from core.skill_models import Skill, SkillStatus, CapabilityAction

class SkillRegistry:
    def __init__(self, db_path: str = "logs/skills.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                skill_id TEXT PRIMARY KEY,
                skill_name TEXT,
                agent TEXT,
                domain TEXT,
                version INTEGER,
                status TEXT,
                procedure_json TEXT,
                attempts INTEGER,
                successful_outcomes INTEGER,
                failed_outcomes INTEGER,
                verified_outcomes INTEGER,
                challenged_outcomes INTEGER,
                regressions INTEGER,
                benchmark_score REAL,
                created_at TEXT,
                last_used TEXT,
                last_verified TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def add_skill(self, skill: Skill):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        procedure_json = json.dumps([p.model_dump() for p in skill.procedure])
        c.execute('''
            INSERT OR REPLACE INTO skills (
                skill_id, skill_name, agent, domain, version, status,
                procedure_json, attempts, successful_outcomes, failed_outcomes,
                verified_outcomes, challenged_outcomes, regressions, benchmark_score,
                created_at, last_used, last_verified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            skill.skill_id, skill.skill_name, skill.agent, skill.domain, skill.version, skill.status.value,
            procedure_json, skill.attempts, skill.successful_outcomes, skill.failed_outcomes,
            skill.verified_outcomes, skill.challenged_outcomes, skill.regressions, skill.benchmark_score,
            skill.created_at, skill.last_used, skill.last_verified
        ))
        conn.commit()
        conn.close()

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM skills WHERE skill_id = ?', (skill_id,))
        r = c.fetchone()
        conn.close()
        
        if not r:
            return None
            
        procedure = [CapabilityAction(**p) for p in json.loads(r[6])]
        
        return Skill(
            skill_id=r[0],
            skill_name=r[1],
            agent=r[2],
            domain=r[3],
            version=r[4],
            status=SkillStatus(r[5]),
            procedure=procedure,
            attempts=r[7],
            successful_outcomes=r[8],
            failed_outcomes=r[9],
            verified_outcomes=r[10],
            challenged_outcomes=r[11],
            regressions=r[12],
            benchmark_score=r[13],
            created_at=r[14],
            last_used=r[15],
            last_verified=r[16]
        )

    def get_active_skill(self, skill_name: str, agent: str) -> Optional[Skill]:
        """Gets the highest version ESTABLISHED skill for a given name and agent"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT * FROM skills 
            WHERE skill_name = ? AND agent = ? AND status = ? 
            ORDER BY version DESC LIMIT 1
        ''', (skill_name, agent, SkillStatus.ESTABLISHED.value))
        r = c.fetchone()
        conn.close()
        
        if not r:
            return None
            
        procedure = [CapabilityAction(**p) for p in json.loads(r[6])]
        return Skill(
            skill_id=r[0], skill_name=r[1], agent=r[2], domain=r[3], version=r[4],
            status=SkillStatus(r[5]), procedure=procedure, attempts=r[7],
            successful_outcomes=r[8], failed_outcomes=r[9], verified_outcomes=r[10],
            challenged_outcomes=r[11], regressions=r[12], benchmark_score=r[13],
            created_at=r[14], last_used=r[15], last_verified=r[16]
        )

    def get_all_versions(self, skill_name: str, agent: str) -> List[Skill]:
        """Returns all versions of a specific skill name for an agent"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT skill_id FROM skills WHERE skill_name = ? AND agent = ? ORDER BY version ASC', (skill_name, agent))
        rows = c.fetchall()
        conn.close()
        return [self.get_skill(r[0]) for r in rows if r]

    def promote_skill(self, new_skill: Skill):
        """Promotes a candidate skill to established. Handles versioning."""
        # Find previous version
        active = self.get_active_skill(new_skill.skill_name, new_skill.agent)
        
        new_skill.status = SkillStatus.ESTABLISHED
        self.add_skill(new_skill)
        
        # We don't overwrite the old skill. It remains in the DB as ESTABLISHED or DEPRECATED.
        # But logically `get_active_skill` fetches the highest version that is ESTABLISHED.

    def rollback_skill(self, skill_name: str, agent: str):
        """Rolls back the current highest version of a skill by marking it DEPRECATED"""
        active = self.get_active_skill(skill_name, agent)
        if active:
            active.status = SkillStatus.DEPRECATED
            self.add_skill(active)
