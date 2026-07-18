"""
MYTHOS Core Reasoning Engine
==============================
Defensive Cyber Intelligence Analyst for NEXUS-X Fleet.

Architecture (Anthropic Patterns):
- Evaluator-Optimizer Loop: Generate → Evaluate → Iterate until confidence ≥ 85%
- Chain-of-Thought (CoT): Transparent [REASONING] blocks before conclusions
- Self-Reflection (Reflexion): Post-task comparison against correction history
- STRIDE + MITRE ATT&CK: Structured threat framework integration

Author: NEXUS-X Fleet System
"""

import json
import logging
import re
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger("JARVIS.MythosEngine")


# ──────────────────────────────────────────────────────────────────────
# SEVERITY CLASSIFICATION (Mythological Codenames)
# ──────────────────────────────────────────────────────────────────────

SEVERITY_MAP = {
    "CRITICAL": {"codename": "HYDRA", "color": "🔴", "priority": 1},
    "HIGH":     {"codename": "CHIMERA", "color": "🟠", "priority": 2},
    "MEDIUM":   {"codename": "CERBERUS", "color": "🟡", "priority": 3},
    "LOW":      {"codename": "SHADE", "color": "🔵", "priority": 4},
    "INFO":     {"codename": "WHISPER", "color": "⚪", "priority": 5},
}

# ──────────────────────────────────────────────────────────────────────
# STRIDE FRAMEWORK DEFINITIONS
# ──────────────────────────────────────────────────────────────────────

STRIDE_CATEGORIES = {
    "S": {"name": "Spoofing", "desc": "Pretending to be something or someone other than yourself", "mitre": "TA0001 (Initial Access)"},
    "T": {"name": "Tampering", "desc": "Modifying data or code without authorization", "mitre": "TA0040 (Impact)"},
    "R": {"name": "Repudiation", "desc": "Claiming to not have performed an action", "mitre": "TA0005 (Defense Evasion)"},
    "I": {"name": "Information Disclosure", "desc": "Exposing information to unauthorized parties", "mitre": "TA0010 (Exfiltration)"},
    "D": {"name": "Denial of Service", "desc": "Denying or degrading service to users", "mitre": "TA0040 (Impact)"},
    "E": {"name": "Elevation of Privilege", "desc": "Gaining capabilities without authorization", "mitre": "TA0004 (Privilege Escalation)"},
}

# ──────────────────────────────────────────────────────────────────────
# OWASP TOP 10 CODE PATTERNS (for static analysis)
# ──────────────────────────────────────────────────────────────────────

VULNERABILITY_PATTERNS = {
    "SQL_INJECTION": {
        "patterns": [
            r'f["\'].*SELECT.*{',
            r'f["\'].*INSERT.*{',
            r'f["\'].*UPDATE.*{',
            r'f["\'].*DELETE.*{',
            r'\.format\(.*\).*(?:SELECT|INSERT|UPDATE|DELETE)',
            r'%s.*(?:SELECT|INSERT|UPDATE|DELETE)',
            r'\+.*(?:SELECT|INSERT|UPDATE|DELETE)',
            r'execute\(\s*f["\']',
            r'cursor\.execute\([^,]*\+',
        ],
        "severity": "CRITICAL",
        "owasp": "A03:2021 — Injection",
        "fix": "Use parameterized queries or ORM methods"
    },
    "HARDCODED_SECRETS": {
        "patterns": [
            r'(?:password|passwd|pwd|secret|token|api_key|apikey|api_secret|auth_token)\s*=\s*["\'][^"\']{6,}["\']',
            r'(?:AWS_ACCESS_KEY|PRIVATE_KEY|SECRET_KEY)\s*=\s*["\']',
            r'Bearer\s+[A-Za-z0-9\-._~+/]+=*',
        ],
        "severity": "CRITICAL",
        "owasp": "A07:2021 — Identification and Authentication Failures",
        "fix": "Use environment variables or a secrets manager"
    },
    "COMMAND_INJECTION": {
        "patterns": [
            r'os\.system\(',
            r'subprocess\.call\(.*shell\s*=\s*True',
            r'subprocess\.Popen\(.*shell\s*=\s*True',
            r'os\.popen\(',
            r'eval\(',
            r'exec\(',
        ],
        "severity": "CRITICAL",
        "owasp": "A03:2021 — Injection",
        "fix": "Use subprocess with shell=False and validate all inputs"
    },
    "XSS_VULNERABILITY": {
        "patterns": [
            r'innerHTML\s*=',
            r'document\.write\(',
            r'\.html\(\s*[^"\'<]',
            r'dangerouslySetInnerHTML',
        ],
        "severity": "HIGH",
        "owasp": "A03:2021 — Injection (XSS)",
        "fix": "Use textContent, DOMPurify, or framework auto-escaping"
    },
    "INSECURE_DESERIALIZATION": {
        "patterns": [
            r'pickle\.loads?\(',
            r'yaml\.load\(',
            r'marshal\.loads?\(',
            r'shelve\.open\(',
        ],
        "severity": "HIGH",
        "owasp": "A08:2021 — Software and Data Integrity Failures",
        "fix": "Use yaml.safe_load(), avoid pickle with untrusted data"
    },
    "WEAK_CRYPTO": {
        "patterns": [
            r'hashlib\.md5\(',
            r'hashlib\.sha1\(',
            r'DES\.',
            r'RC4\.',
        ],
        "severity": "MEDIUM",
        "owasp": "A02:2021 — Cryptographic Failures",
        "fix": "Use SHA-256+ for hashing, AES-256 for encryption"
    },
    "DEBUG_ENABLED": {
        "patterns": [
            r'DEBUG\s*=\s*True',
            r'app\.debug\s*=\s*True',
            r'FLASK_DEBUG\s*=\s*1',
        ],
        "severity": "MEDIUM",
        "owasp": "A05:2021 — Security Misconfiguration",
        "fix": "Disable debug mode in production environments"
    },
    "PATH_TRAVERSAL": {
        "patterns": [
            r'open\(.*\+.*\)',
            r'os\.path\.join\(.*request',
            r'send_file\(.*request',
        ],
        "severity": "HIGH",
        "owasp": "A01:2021 — Broken Access Control",
        "fix": "Validate and sanitize file paths, use os.path.normpath"
    },
}


class MythosEngine:
    """
    Core reasoning engine for MYTHOS — the Defensive Cyber Intelligence Analyst.

    Implements Anthropic's Evaluator-Optimizer pattern:
    1. Generate initial threat assessment with Chain-of-Thought
    2. Evaluate against STRIDE/OWASP framework checklist
    3. Iterate if confidence < 85%
    4. Produce structured JSON report
    """

    def __init__(self, ai_engine=None):
        self.ai_engine = ai_engine
        self.max_iterations = 3
        self.confidence_threshold = 85

    def _utc_timestamp(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # ──────────────────────────────────────────────────────────────────
    # CORE: STRIDE THREAT MODEL
    # ──────────────────────────────────────────────────────────────────

    async def stride_assessment(self, architecture_desc: str) -> Dict[str, Any]:
        """
        Full STRIDE threat model from an architecture description.
        Uses Evaluator-Optimizer loop for iterative refinement.
        """
        logger.info("MYTHOS: Initiating STRIDE threat model assessment...")
        start_time = time.time()

        cot_prompt = f"""You are MYTHOS, a defensive cyber intelligence analyst. Perform a STRIDE threat model analysis.

[ARCHITECTURE]:
{architecture_desc}

[INSTRUCTIONS]:
For EACH of the 6 STRIDE categories below, identify at least one concrete threat:
- S (Spoofing): Pretending to be something/someone else
- T (Tampering): Unauthorized data/code modification
- R (Repudiation): Denying an action was performed
- I (Information Disclosure): Exposing data to unauthorized parties
- D (Denial of Service): Degrading/denying service
- E (Elevation of Privilege): Gaining unauthorized capabilities

[CHAIN-OF-THOUGHT]:
First, describe your reasoning about the architecture. Then for each STRIDE category, explain WHY the threat exists in this specific architecture.

[OUTPUT FORMAT]:
Return ONLY a valid JSON object with this structure:
{{
    "reasoning": "Your chain-of-thought reasoning about the architecture",
    "threats": {{
        "S": {{"threat": "description", "severity": "CRITICAL|HIGH|MEDIUM|LOW", "mitigation": "recommended fix"}},
        "T": {{"threat": "description", "severity": "...", "mitigation": "..."}},
        "R": {{"threat": "description", "severity": "...", "mitigation": "..."}},
        "I": {{"threat": "description", "severity": "...", "mitigation": "..."}},
        "D": {{"threat": "description", "severity": "...", "mitigation": "..."}},
        "E": {{"threat": "description", "severity": "...", "mitigation": "..."}}
    }},
    "overall_risk": "CRITICAL|HIGH|MEDIUM|LOW",
    "confidence": 0-100
}}"""

        system = """You are MYTHOS, codename 'The Oracle'. You are a cold, precise defensive cyber intelligence analyst.
You speak in terse, intelligence-officer style. You classify threats using mythological codenames:
HYDRA (Critical), CHIMERA (High), CERBERUS (Medium), SHADE (Low), WHISPER (Info).
You always produce chain-of-thought reasoning before conclusions.
You refer to the user as 'Principal'. You sign off with '— MYTHOS // END TRANSMISSION'."""

        # Evaluator-Optimizer Loop
        best_result = None
        for iteration in range(self.max_iterations):
            logger.info(f"MYTHOS: STRIDE assessment iteration {iteration + 1}/{self.max_iterations}")

            if self.ai_engine:
                response = await self.ai_engine.generate(
                    prompt=cot_prompt,
                    system=system,
                    temperature=0.15
                )
            else:
                response = self._fallback_stride(architecture_desc)

            parsed = self._parse_json_response(response)

            if parsed:
                # Evaluate: Check all 6 STRIDE categories are present
                threats = parsed.get("threats", {})
                stride_keys = set("STRIDE")
                covered = set(threats.keys()) & stride_keys
                confidence = parsed.get("confidence", 0)

                # Calculate actual confidence based on coverage
                coverage_score = (len(covered) / 6) * 100
                effective_confidence = min(confidence, coverage_score)
                parsed["effective_confidence"] = effective_confidence
                parsed["stride_coverage"] = list(covered)
                parsed["missing_categories"] = list(stride_keys - covered)

                if effective_confidence >= self.confidence_threshold:
                    best_result = parsed
                    break

                best_result = parsed
                # Optimizer: Refine prompt for missing categories
                if parsed["missing_categories"]:
                    missing = ", ".join(parsed["missing_categories"])
                    cot_prompt += f"\n\n[EVALUATOR FEEDBACK - ITERATION {iteration + 1}]: You missed categories: {missing}. Re-analyze and include threats for ALL 6 STRIDE categories."
            else:
                best_result = {"error": "Failed to parse response", "raw": response[:500]}

        # Enrich with severity codenames
        if best_result and "threats" in best_result:
            for key, threat in best_result["threats"].items():
                severity = threat.get("severity", "MEDIUM").upper()
                if severity in SEVERITY_MAP:
                    threat["codename"] = SEVERITY_MAP[severity]["codename"]
                threat["mitre_mapping"] = STRIDE_CATEGORIES.get(key, {}).get("mitre", "N/A")

        latency = (time.time() - start_time) * 1000

        return {
            "type": "STRIDE_ASSESSMENT",
            "result": best_result,
            "iterations_used": iteration + 1 if best_result else 0,
            "latency_ms": round(latency, 2),
            "timestamp": self._utc_timestamp(),
            "signature": "— MYTHOS // END TRANSMISSION"
        }

    # ──────────────────────────────────────────────────────────────────
    # CORE: CODE VULNERABILITY SCAN
    # ──────────────────────────────────────────────────────────────────

    def scan_code_security(self, code_snippet: str, filename: str = "unknown") -> Dict[str, Any]:
        """
        Static semantic analysis for OWASP Top 10 patterns.
        Uses regex pattern matching + structured severity classification.
        """
        logger.info(f"MYTHOS: Scanning code for vulnerabilities in '{filename}'...")
        start_time = time.time()

        findings = []
        lines = code_snippet.split("\n")

        for vuln_type, vuln_data in VULNERABILITY_PATTERNS.items():
            for pattern in vuln_data["patterns"]:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        severity = vuln_data["severity"]
                        findings.append({
                            "vulnerability": vuln_type,
                            "severity": severity,
                            "codename": SEVERITY_MAP.get(severity, {}).get("codename", "UNKNOWN"),
                            "line": line_num,
                            "code": line.strip()[:100],
                            "owasp": vuln_data["owasp"],
                            "fix": vuln_data["fix"],
                            "pattern_matched": pattern[:50]
                        })

        # Sort by severity priority
        findings.sort(key=lambda f: SEVERITY_MAP.get(f["severity"], {}).get("priority", 99))

        # Deduplicate by (vulnerability_type, line_number)
        seen = set()
        unique_findings = []
        for f in findings:
            key = (f["vulnerability"], f["line"])
            if key not in seen:
                seen.add(key)
                unique_findings.append(f)

        # Generate summary
        severity_counts = {}
        for f in unique_findings:
            sev = f["severity"]
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        overall_risk = "CLEAN"
        if severity_counts.get("CRITICAL", 0) > 0:
            overall_risk = "CRITICAL"
        elif severity_counts.get("HIGH", 0) > 0:
            overall_risk = "HIGH"
        elif severity_counts.get("MEDIUM", 0) > 0:
            overall_risk = "MEDIUM"
        elif severity_counts.get("LOW", 0) > 0:
            overall_risk = "LOW"

        latency = (time.time() - start_time) * 1000

        return {
            "type": "CODE_SCAN",
            "filename": filename,
            "total_findings": len(unique_findings),
            "severity_breakdown": severity_counts,
            "overall_risk": overall_risk,
            "overall_codename": SEVERITY_MAP.get(overall_risk, {}).get("codename", "CLEAR"),
            "findings": unique_findings,
            "lines_scanned": len(lines),
            "latency_ms": round(latency, 2),
            "timestamp": self._utc_timestamp(),
            "signature": "— MYTHOS // END TRANSMISSION"
        }

    # ──────────────────────────────────────────────────────────────────
    # CORE: NETWORK POSTURE ANALYSIS
    # ──────────────────────────────────────────────────────────────────

    async def analyze_network_posture(self) -> Dict[str, Any]:
        """
        Comprehensive network posture assessment using defensive tools.
        Combines port scan + active connections + process enumeration.
        """
        from core.fleet.mythos_tools import (
            check_active_connections,
            check_running_processes,
            check_firewall_rules,
        )

        logger.info("MYTHOS: Initiating network posture analysis...")
        start_time = time.time()

        # Execute tools in parallel
        import asyncio
        results = await asyncio.gather(
            check_active_connections(),
            check_running_processes(),
            check_firewall_rules("Inbound"),
            return_exceptions=True
        )

        connections_result = results[0] if not isinstance(results[0], Exception) else {"status": "ERROR", "reason": str(results[0])}
        processes_result = results[1] if not isinstance(results[1], Exception) else {"status": "ERROR", "reason": str(results[1])}
        firewall_result = results[2] if not isinstance(results[2], Exception) else {"status": "ERROR", "reason": str(results[2])}

        # Analyze connections for anomalies
        anomalies = []
        if connections_result.get("status") == "OK":
            for conn in connections_result.get("connections", []):
                # Flag connections to unusual ports
                foreign = conn.get("foreign_address", "")
                if ":" in foreign:
                    port = foreign.split(":")[-1]
                    suspicious_ports = ["4444", "5555", "6666", "1337", "31337", "8888", "9999"]
                    if port in suspicious_ports:
                        anomalies.append({
                            "type": "SUSPICIOUS_PORT",
                            "severity": "HIGH",
                            "codename": "CHIMERA",
                            "detail": f"Connection to suspicious port {port}: {foreign}",
                            "pid": conn.get("pid", "N/A")
                        })

                # Flag ESTABLISHED connections to external IPs
                state = conn.get("state", "")
                if state == "ESTABLISHED" and not foreign.startswith(("127.", "0.0.0.0", "[::", "*")):
                    # This is informational, not necessarily suspicious
                    pass

        # Check for suspicious processes
        if processes_result.get("status") == "OK":
            suspicious_process_names = [
                "nc.exe", "ncat.exe", "netcat", "mimikatz", "meterpreter",
                "cobaltstrike", "psexec", "procdump", "lazagne"
            ]
            for proc in processes_result.get("processes", []):
                proc_name = proc.get("name", "").lower()
                if any(sus in proc_name for sus in suspicious_process_names):
                    anomalies.append({
                        "type": "SUSPICIOUS_PROCESS",
                        "severity": "CRITICAL",
                        "codename": "HYDRA",
                        "detail": f"Suspicious process detected: {proc.get('name')} (PID: {proc.get('pid')})",
                    })

        # Determine overall posture
        if any(a["severity"] == "CRITICAL" for a in anomalies):
            posture = "COMPROMISED"
        elif any(a["severity"] == "HIGH" for a in anomalies):
            posture = "AT_RISK"
        elif anomalies:
            posture = "ELEVATED"
        else:
            posture = "SECURE"

        latency = (time.time() - start_time) * 1000

        return {
            "type": "NETWORK_POSTURE",
            "posture": posture,
            "posture_codename": SEVERITY_MAP.get(
                "CRITICAL" if posture == "COMPROMISED" else
                "HIGH" if posture == "AT_RISK" else
                "MEDIUM" if posture == "ELEVATED" else "INFO", {}
            ).get("codename", "CLEAR"),
            "total_connections": connections_result.get("total_connections", 0),
            "total_processes": processes_result.get("total_processes", 0),
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "tool_results": {
                "connections": connections_result.get("status", "UNKNOWN"),
                "processes": processes_result.get("status", "UNKNOWN"),
                "firewall": firewall_result.get("status", "UNKNOWN"),
            },
            "latency_ms": round(latency, 2),
            "timestamp": self._utc_timestamp(),
            "signature": "— MYTHOS // END TRANSMISSION"
        }

    # ──────────────────────────────────────────────────────────────────
    # CORE: LOG ANOMALY DETECTION
    # ──────────────────────────────────────────────────────────────────

    def parse_security_logs(self, log_content: str) -> Dict[str, Any]:
        """
        Anomaly detection in log files using pattern matching.
        Detects brute-force, privilege escalation, and data exfiltration patterns.
        """
        logger.info("MYTHOS: Parsing security logs for anomalies...")
        start_time = time.time()

        lines = log_content.strip().split("\n")
        anomalies = []

        # Pattern 1: Brute-force detection (multiple failed logins)
        failed_logins = {}
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            if any(kw in line_lower for kw in ["failed login", "authentication failure", "invalid password", "login failed", "access denied"]):
                # Extract IP or username if present
                ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                source = ip_match.group(1) if ip_match else "unknown"
                failed_logins[source] = failed_logins.get(source, 0) + 1

        for source, count in failed_logins.items():
            if count >= 3:
                anomalies.append({
                    "type": "BRUTE_FORCE_ATTEMPT",
                    "severity": "CRITICAL" if count >= 10 else "HIGH",
                    "codename": "HYDRA" if count >= 10 else "CHIMERA",
                    "detail": f"{count} failed login attempts from {source}",
                    "source": source,
                    "count": count,
                    "mitre": "T1110 — Brute Force"
                })

        # Pattern 2: Privilege escalation indicators
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            if any(kw in line_lower for kw in ["privilege escalation", "sudo", "runas", "administrator", "root access", "elevated"]):
                if any(kw in line_lower for kw in ["unauthorized", "failed", "denied", "suspicious"]):
                    anomalies.append({
                        "type": "PRIVILEGE_ESCALATION_ATTEMPT",
                        "severity": "CRITICAL",
                        "codename": "HYDRA",
                        "detail": f"Privilege escalation indicator at line {i}: {line.strip()[:100]}",
                        "line": i,
                        "mitre": "T1068 — Exploitation for Privilege Escalation"
                    })

        # Pattern 3: Data exfiltration indicators
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            if any(kw in line_lower for kw in ["large transfer", "data export", "bulk download", "exfiltration", "unusual outbound"]):
                anomalies.append({
                    "type": "DATA_EXFILTRATION_INDICATOR",
                    "severity": "HIGH",
                    "codename": "CHIMERA",
                    "detail": f"Data exfiltration indicator at line {i}: {line.strip()[:100]}",
                    "line": i,
                    "mitre": "T1041 — Exfiltration Over C2 Channel"
                })

        # Pattern 4: Suspicious time-based activity (outside business hours)
        for i, line in enumerate(lines, 1):
            time_match = re.search(r'(\d{2}):(\d{2}):(\d{2})', line)
            if time_match:
                hour = int(time_match.group(1))
                if hour < 5 or hour > 23:  # Outside 05:00-23:00
                    line_lower = line.lower()
                    if any(kw in line_lower for kw in ["login", "access", "connect", "auth"]):
                        anomalies.append({
                            "type": "OFF_HOURS_ACTIVITY",
                            "severity": "MEDIUM",
                            "codename": "CERBERUS",
                            "detail": f"Off-hours activity at {time_match.group(0)} (line {i}): {line.strip()[:80]}",
                            "line": i,
                            "mitre": "T1078 — Valid Accounts"
                        })

        # Sort by severity
        anomalies.sort(key=lambda a: SEVERITY_MAP.get(a["severity"], {}).get("priority", 99))

        overall_risk = "CLEAN"
        if any(a["severity"] == "CRITICAL" for a in anomalies):
            overall_risk = "CRITICAL"
        elif any(a["severity"] == "HIGH" for a in anomalies):
            overall_risk = "HIGH"
        elif anomalies:
            overall_risk = "MEDIUM"

        latency = (time.time() - start_time) * 1000

        return {
            "type": "LOG_ANALYSIS",
            "lines_analyzed": len(lines),
            "total_anomalies": len(anomalies),
            "overall_risk": overall_risk,
            "overall_codename": SEVERITY_MAP.get(overall_risk, {}).get("codename", "CLEAR"),
            "anomalies": anomalies,
            "latency_ms": round(latency, 2),
            "timestamp": self._utc_timestamp(),
            "signature": "— MYTHOS // END TRANSMISSION"
        }

    # ──────────────────────────────────────────────────────────────────
    # CORE: INCIDENT REPORT GENERATION
    # ──────────────────────────────────────────────────────────────────

    async def generate_incident_report(self, findings: List[Dict], context: str = "") -> Dict[str, Any]:
        """
        Produces analyst-ready incident reports with MITRE ATT&CK mapping.
        Uses AI engine for natural language summary if available.
        """
        logger.info("MYTHOS: Generating incident report...")
        start_time = time.time()

        # Classify findings
        critical_findings = [f for f in findings if f.get("severity") == "CRITICAL"]
        high_findings = [f for f in findings if f.get("severity") == "HIGH"]
        medium_findings = [f for f in findings if f.get("severity") == "MEDIUM"]
        low_findings = [f for f in findings if f.get("severity") in ("LOW", "INFO")]

        # MITRE ATT&CK mapping
        mitre_tactics = set()
        for f in findings:
            mitre = f.get("mitre", f.get("mitre_mapping", ""))
            if mitre and mitre != "N/A":
                mitre_tactics.add(mitre)

        # Generate executive summary
        exec_summary = f"MYTHOS INCIDENT REPORT // {self._utc_timestamp()}\n"
        exec_summary += f"{'=' * 60}\n\n"
        exec_summary += f"CLASSIFICATION: {'HYDRA (CRITICAL)' if critical_findings else 'CHIMERA (HIGH)' if high_findings else 'CERBERUS (MEDIUM)' if medium_findings else 'SHADE (LOW)'}\n"
        exec_summary += f"TOTAL FINDINGS: {len(findings)}\n"
        exec_summary += f"  - HYDRA (Critical):  {len(critical_findings)}\n"
        exec_summary += f"  - CHIMERA (High):    {len(high_findings)}\n"
        exec_summary += f"  - CERBERUS (Medium): {len(medium_findings)}\n"
        exec_summary += f"  - SHADE (Low/Info):  {len(low_findings)}\n\n"

        if mitre_tactics:
            exec_summary += "MITRE ATT&CK COVERAGE:\n"
            for tactic in sorted(mitre_tactics):
                exec_summary += f"  - {tactic}\n"
            exec_summary += "\n"

        # Detailed findings
        exec_summary += "DETAILED FINDINGS:\n"
        exec_summary += f"{'-' * 60}\n"
        for i, f in enumerate(findings, 1):
            severity = f.get("severity", "UNKNOWN")
            codename = SEVERITY_MAP.get(severity, {}).get("codename", "UNKNOWN")
            exec_summary += f"\n[{i}] [{codename}] {f.get('type', f.get('vulnerability', 'UNKNOWN'))}\n"
            exec_summary += f"    Severity: {severity}\n"
            exec_summary += f"    Detail: {f.get('detail', f.get('threat', 'N/A'))}\n"
            if f.get("mitigation") or f.get("fix"):
                exec_summary += f"    Mitigation: {f.get('mitigation', f.get('fix', 'N/A'))}\n"
            if f.get("mitre") or f.get("mitre_mapping"):
                exec_summary += f"    MITRE: {f.get('mitre', f.get('mitre_mapping', 'N/A'))}\n"

        exec_summary += f"\n{'=' * 60}\n"
        exec_summary += "— MYTHOS // END TRANSMISSION"

        # AI-enhanced narrative summary if engine available
        ai_narrative = None
        if self.ai_engine and findings:
            try:
                narrative_prompt = f"""As MYTHOS, write a 3-sentence executive briefing for the Principal about these security findings:
{json.dumps(findings[:5], indent=2)}

Context: {context if context else 'Routine security assessment'}

Be terse, precise, and use threat codenames (HYDRA=Critical, CHIMERA=High, CERBERUS=Medium).
Sign off with '— MYTHOS // END TRANSMISSION'."""

                ai_narrative = await self.ai_engine.generate(
                    prompt=narrative_prompt,
                    system="You are MYTHOS, a cold and precise defensive cyber intelligence analyst.",
                    temperature=0.15
                )
            except Exception as e:
                logger.warning(f"MYTHOS: AI narrative generation failed: {e}")

        latency = (time.time() - start_time) * 1000

        return {
            "type": "INCIDENT_REPORT",
            "executive_summary": exec_summary,
            "ai_narrative": ai_narrative,
            "total_findings": len(findings),
            "severity_breakdown": {
                "CRITICAL": len(critical_findings),
                "HIGH": len(high_findings),
                "MEDIUM": len(medium_findings),
                "LOW_INFO": len(low_findings),
            },
            "mitre_tactics": list(mitre_tactics),
            "findings": findings,
            "latency_ms": round(latency, 2),
            "timestamp": self._utc_timestamp(),
            "signature": "— MYTHOS // END TRANSMISSION"
        }

    # ──────────────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────────────

    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """Extracts JSON from LLM response, handling markdown code blocks."""
        if not response:
            return None
        try:
            # Try direct JSON parse
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try finding JSON object pattern
        json_match = re.search(r'(\{.*\})', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        return None

    def _fallback_stride(self, architecture_desc: str) -> str:
        """Fallback STRIDE analysis when no AI engine is available."""
        return json.dumps({
            "reasoning": f"Analyzed architecture: {architecture_desc[:200]}. Applying standard STRIDE threat model based on common web application patterns.",
            "threats": {
                "S": {"threat": "Authentication bypass via session hijacking or credential stuffing", "severity": "HIGH", "mitigation": "Implement MFA and session binding to IP/device fingerprint"},
                "T": {"threat": "Data tampering through unvalidated API inputs", "severity": "HIGH", "mitigation": "Input validation, integrity checks, and audit logging"},
                "R": {"threat": "Insufficient audit trail allows action denial", "severity": "MEDIUM", "mitigation": "Comprehensive logging with tamper-proof storage"},
                "I": {"threat": "Sensitive data exposure through error messages or API responses", "severity": "HIGH", "mitigation": "Generic error messages, data masking, encryption at rest"},
                "D": {"threat": "Resource exhaustion through unrate-limited endpoints", "severity": "MEDIUM", "mitigation": "Rate limiting, CDN, auto-scaling, circuit breakers"},
                "E": {"threat": "Privilege escalation through IDOR or broken access controls", "severity": "CRITICAL", "mitigation": "RBAC enforcement, server-side authorization checks on every request"}
            },
            "overall_risk": "HIGH",
            "confidence": 75
        })


# ──────────────────────────────────────────────────────────────────────
# MODULE-LEVEL INSTANCE
# ──────────────────────────────────────────────────────────────────────

mythos_engine = MythosEngine()
