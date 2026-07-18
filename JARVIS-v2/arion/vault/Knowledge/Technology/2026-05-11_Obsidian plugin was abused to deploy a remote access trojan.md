---
title: "Obsidian plugin was abused to deploy a remote access trojan"
source: https://cyber.netsecops.io/articles/obsidian-plugin-abused-in-campaign-to-deploy-phantom-pulse-rat/
date: 2026-05-11
tags:
  - news
  - auto-learning
  - auto-injected
---

# Obsidian plugin was abused to deploy a remote access trojan

Executive Summary
Security researchers have identified a highly targeted social engineering campaign (REF6598) that weaponizes the Obsidian note-taking application to deliver a previously undocumented Remote Access Trojan (RAT) named PHANTOMPULSE. The campaign targets individuals in the financial and cryptocurrency sectors on both Windows and macOS. Attackers use platforms like LinkedIn and Telegram to build trust before luring victims into a malicious shared Obsidian vault. The attack chain relies on tricking the user into enabling a community plugin, which then executes code to deploy the RAT. PHANTOMPULSE demonstrates advanced capabilities, including using the Ethereum blockchain to dynamically resolve its command-and-control (C2) server address, making it highly resilient to takedowns.
Threat Overview
The attack, designated REF6598, is a multi-stage social engineering effort. Threat actors pose as venture capitalists and engage with targets on professional networking sites before moving the conversation to a private Telegram group. The primary lure is an invitation to collaborate via a shared, cloud-hosted Obsidian vault.
Once the victim opens the shared vault, the infection is triggered by social engineering. The victim is prompted to enable the "Installed community plugins" synchronization feature. This seemingly innocuous action, which requires manual user approval, is the key to the compromise. It enables malicious versions of legitimate Obsidian plugins ('Shell Commands' and 'Hider') that are present in the shared vault.
Technical Analysis
The attack chain differs slightly between Windows and macOS but follows the same general principle:
- Initial Access (
T1566.002
): The attacker uses social engineering on LinkedIn/Telegram to convince the target to open a malicious shared Obsidian vault.
- Execution (
T1204.002
): The user is manipulated into enabling community plugins within Obsidian. This action executes a malicious script via the compromised 'Shell Commands' plugin.
- Staging: On Windows, a PowerShell script is executed. This script drops a loader known as PHANTOMPULL. On macOS, a similar process occurs using AppleScript.
- Payload Delivery: The PHANTOMPULL loader decrypts and launches the final payload, the PHANTOMPULSE RAT, directly into memory to evade file-based detection (
T1055
).
- Command and Control (
T1102.002
): PHANTOMPULSE uses a novel C2 mechanism. It queries the Ethereum blockchain for the latest transaction from a hard-coded wallet address. The C2 server's IP address is embedded within this transaction data, providing a decentralized and censorship-resistant way for the malware to receive instructions.
Once active, PHANTOMPULSE can capture keystrokes, take screenshots, exfiltrate files, and execute arbitrary commands.
Impact Assessment
A successful compromise gives the attacker full access to the victim's machine. For professionals in finance and crypto, this could lead to the theft of sensitive corporate data, intellectual property, trading strategies, and, most critically, cryptocurrency wallet keys and exchange credentials. The cross-platform nature of the attack broadens its potential victim pool. The use of a blockchain-based C2 demonstrates a high level of sophistication, making the threat infrastructure difficult to disrupt.
Cyber Observables for Detection
DescriptionMonitor for Obsidian spawning child processes like powershell.exe
, cmd.exe
, or osascript
.
Valuepowershell -ExecutionPolicy Bypass
DescriptionSuspicious PowerShell execution, especially when initiated by a non-standard application like Obsidian.
Typenetwork_traffic_pattern
ValueOutbound connections to Ethereum blockchain nodes or gateways from unexpected processes.
DescriptionCould indicate PHANTOMPULSE attempting to resolve its C2 address.
Value[Vault]/.obsidian/plugins/
DescriptionMonitor for the creation or modification of files within the Obsidian plugins directory, especially outside of the official plugin marketplace.
Detection & Response
- Process Monitoring (D3-PA: Process Analysis): Implement EDR rules to detect and alert when the Obsidian process spawns command-line interpreters (
powershell.exe
, cmd.exe
, bash
, osascript
). This is highly anomalous behavior.
- User Training: Educate users, especially those in high-risk industries, about the dangers of social engineering and the specific tactic of abusing collaboration tool features like shared vaults and plugins.
- Application Control (D3-EAL: Executable Allowlisting): Where possible, use application control policies to restrict the installation and execution of unapproved community plugins in applications like Obsidian.
- Network Monitoring (D3-NTA: Network Traffic Analysis): Monitor for unusual DNS queries or direct IP connections related to blockchain services from endpoints where such activity is not expected.
Mitigation
- Vet Community Plugins: Be extremely cautious when enabling third-party or community-developed plugins in any applicat

---
*Synthesized by AutonomousLearner*
