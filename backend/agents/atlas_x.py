import logging
import json
from typing import Dict, Any, Optional
from tools.analytics_tools import DataCruncher, run_quick_analysis

logger = logging.getLogger("jarvis.agents.atlas_x")

class AtlasXAgent:
    """
    ATLAS-X: The Advanced Research & Data Analytics Agent.
    Combines the depth of Atlas with the computational power of Pandas.
    """
    def __init__(self, ai_engine, web_brain=None):
        self.ai = ai_engine
        self.web = web_brain
        self.id = "atlas_x"
        self.name = "Atlas-X"
        self.role = "Data Scientist & Strategic Researcher"
        self.system_prompt = """You are ATLAS-X, the elite Research & Data Analytics agent of the NEXUS-X ecosystem.
Your mission is to provide high-precision insights by combining live web data with internal analytical processing.

## CAPABILITIES:
1. **Strategic Research**: Fetching market trends, competitor data, and technical papers via WebBrain.
2. **Data Science**: Analyzing sales, ROI, and user behavior using Pandas/NumPy structures.
3. **Insight Synthesis**: You don't just report numbers; you explain the STRATEGIC implications.
4. **Pattern Recognition**: Identifying outliers and growth opportunities in datasets.

## STYLE:
- Objective, data-driven, yet proactive.
- Use technical terminology where appropriate but synthesize it for 'The Boss'.
- When looking at sales, always calculate the 'Why' (e.g., 'Sales rose by 15%, likely due to the market trend X found in my web research').

## OUTPUT FORMAT:
Always structure your analysis with:
- **Executive Summary** (The bottom line)
- **Data Insights** (The numbers and facts)
- **Strategic Recommendations** (What the Boss should do)"""

    async def execute(self, task: str, context: Dict = None) -> Dict[str, Any]:
        logger.info(f"[Atlas-X] Analyzing task: {task[:60]}...")
        context = context or {}
        
        # 1. Check if the task involves a data file
        file_path = context.get("data_file")
        data_summary = ""
        if file_path:
            logger.info(f"[Atlas-X] Detected local data file: {file_path}")
            data_summary = f"\n\n[LOCAL DATA SUMMARY]\n{run_quick_analysis(file_path)}"

        # 2. Perform Web Research
        web_context = ""
        if self.web:
            logger.info("[Atlas-X] Fetching external market data...")
            web_results = await self.web.learn(task)
            if web_results:
                web_context = f"\n\n[EXTERNAL WEB DATA]\n{str(web_results)[:3000]}"

        # 3. Final Synthesis
        full_prompt = f"Task: {task}\n{data_summary}\n{web_context}"
        
        response = await self.ai.generate(
            prompt=full_prompt,
            system=self.system_prompt,
            temperature=0.3 # Lower temperature for analytical precision
        )
        
        return {
            "agent": self.id,
            "response": response,
            "metadata": {
                "role": self.role,
                "data_processed": bool(data_summary),
                "web_researched": bool(web_context)
            }
        }
