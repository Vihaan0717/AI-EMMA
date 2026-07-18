import os
import aiofiles
from datetime import datetime
import json
import httpx
import logging

logger = logging.getLogger("JARVIS.SentinelSummarizer")

# Paths mapping directly to your directory structure
VAULT_LOGS_PATH = "knowledge_vault/logs/sentinel_audits"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

async def log_to_obsidian(target: str, scan_type: str, raw_output: str, summary: str) -> str:
    """
    Asynchronously writes the complete audit log into the Obsidian Knowledge Vault.
    Returns the path of the created file.
    """
    os.makedirs(VAULT_LOGS_PATH, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"audit_{target}_{timestamp}.md"
    file_path = os.path.join(VAULT_LOGS_PATH, filename)
    
    # Obsidian Markdown Format with Frontmatter Metadata
    markdown_content = f"""---
type: security_audit
target: {target}
scan_type: {scan_type}
timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
tags: [sentinel, audit, network]
---

# Sentinel Security Audit: {target}

## Vocal Summary
> {summary}

## Raw Subprocess Output
```text
{raw_output}
```

"""

    async with aiofiles.open(file_path, mode='w', encoding='utf-8') as f:
        await f.write(markdown_content)
        
    return file_path

async def generate_vocal_summary(scan_type: str, raw_output: str) -> str:
    """
    Pipes the massive raw output to the ultra-fast local router model
    to extract a 2-sentence human-readable summary.
    """
    # Strict prompt layout keeping the local context constrained
    system_instruction = (
        "You are Sentinel's insight processor. Analyze the raw terminal data and compress it "
        "into exactly one or two short sentences for a voice assistant. Focus strictly on whether "
        "the system is safe or if anomalies/open ports were found. Do not list raw numbers, hashes, "
        "or IP lists unless critical. Be concise and crisp."
    )

    prompt = f"Scan Type: {scan_type}\n\nRaw Output Data:\n{raw_output[:4000]}" # Truncate to avoid VRAM overflow

    payload = {
        "model": "qwen2.5:1.5b", # Using fast local router model
        "prompt": f"{system_instruction}\n\nUser Output:\n{prompt}",
        "stream": False,
        "options": {
            "temperature": 0.3,
            "keep_alive": "30s" # Keep it hot for sequential updates
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OLLAMA_API_URL, json=payload, timeout=15.0)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Audit processed, but summary generation failed.").strip()
            else:
                return f"Audit complete. System reported status code {response.status_code} during processing."
    except Exception as e:
        logger.error(f"Error calling local inference for summary: {e}")
        return "Audit complete. Local reasoning engine timed out, but logs have been preserved safely."

async def process_sentinel_output(target: str, scan_type: str, raw_output: str) -> dict:
    """
    The orchestrator function called by your main execution bus.
    """
    if "[ERROR]" in raw_output or "[SECURITY BLOCK]" in raw_output:
        return {"vocal_response": raw_output, "vault_path": None}

    # 1. Compress into a vocalizable format 
    vocal_brief = await generate_vocal_summary(scan_type, raw_output)

    # 2. Silently commit the full block to the Obsidian graph
    vault_file = await log_to_obsidian(target, scan_type, raw_output, vocal_brief)

    return {
        "vocal_response": vocal_brief,
        "vault_path": vault_file
    }
