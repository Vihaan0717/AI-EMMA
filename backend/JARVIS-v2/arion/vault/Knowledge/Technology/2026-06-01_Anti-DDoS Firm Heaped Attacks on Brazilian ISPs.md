---
title: "Anti-DDoS Firm Heaped Attacks on Brazilian ISPs"
source: https://krebsonsecurity.com/2026/04/anti-ddos-firm-heaped-attacks-on-brazilian-isps/
date: 2026-06-01
tags:
  - news
  - auto-learning
  - auto-injected
---

# Anti-DDoS Firm Heaped Attacks on Brazilian ISPs

A Brazilian tech firm that specializes in protecting networks from distributed denial-of-service (DDoS) attacks has been enabling a botnet responsible for an extended campaign of massive DDoS attacks against other network operators in Brazil, KrebsOnSecurity has learned. The firm’s chief executive says the malicious activity resulted from a security breach and was likely the work of a competitor trying to tarnish his company’s public image.
For the past several years, security experts have tracked a series of massive DDoS attacks originating from Brazil and solely targeting Brazilian ISPs. Until recently, it was less than clear who or what was behind these digital sieges. That changed earlier this month when a trusted source who asked to remain anonymous shared a curious file archive that was exposed in an open directory online.
The exposed archive contained several Portuguese-language malicious programs written in Python. It also included the private SSH authentication keys belonging to the CEO of Huge Networks, a Brazilian ISP that primarily offers DDoS protection to other Brazilian network operators.
Founded in Miami, Fla. in 2014, Huge Networks’s operations are centered in Brazil. The company originated from protecting game servers against DDoS attacks and evolved into an ISP-focused DDoS mitigation provider. It does not appear in any public abuse complaints and is not associated with any known DDoS-for-hire services.
Nevertheless, the exposed archive shows that a Brazil-based threat actor maintained root access to Huge Networks infrastructure and built a powerful DDoS botnet by routinely mass-scanning the Internet for insecure Internet routers and unmanaged domain name system (DNS) servers on the Web that could be enlisted in attacks.
DNS is what allows Internet users to reach websites by typing familiar domain names instead of the associated IP addresses. Ideally, DNS servers only provide answers to machines within a trusted domain. But so-called “DNS reflection” attacks rely on DNS servers that are (mis)configured to accept queries from anywhere on the Web. Attackers can send spoofed DNS queries to these servers so that the request appears to come from the target’s network. That way, when the DNS servers respond, they reply to the spoofed (targeted) address.
By taking advantage of an extension to the DNS protocol that enables large DNS messages, botmasters can dramatically boost the size and impact of a reflection attack — crafting DNS queries so that the responses are much bigger than the requests. For example, an attacker could compose a DNS request of less than 100 bytes, prompting a response that is 60-70 times as large. This amplification effect is especially pronounced when the perpetrators can query many DNS servers with these spoofed requests from tens of thousands of compromised devices simultaneously.
The exposed file archive includes a command-line history showing exactly how this attacker built and maintained a powerful botnet by scouring the Internet for TP-Link Archer AX21 routers. Specifically, the botnet seeks out TP-Link devices that remain vulnerable to CVE-2023-1389, an unauthenticated command injection vulnerability that was patched back in April 2023.
Malicious domains in the exposed Python attack scripts included DNS lookups for hikylover[.]st, and c.loyaltyservices[.]lol, both domains that have been flagged in the past year as control servers for an Internet of Things (IoT) botnet powered by a Mirai malware variant.
The leaked archive shows the botmaster coordinated their scanning from a Digital Ocean server that has been flagged for abusive activity hundreds of times in the past year. The Python scripts invoke multiple Internet addresses assigned to Huge Networks that were used to identify targets and execute DDoS campaigns. The attacks were strictly limited to Brazilian IP address ranges, and the scripts show that each selected IP address prefix was attacked for 10-60 seconds with four parallel processes per host before the botnet moved on to the next target.
The archive also shows these malicious Python scripts relied on private SSH keys belonging to Huge Networks’s CEO, Erick Nascimento. Reached for comment about the files, Mr. Nascimento said he did not write the attack programs and that he didn’t realize the extent of the DDoS campaigns until contacted by KrebsOnSecurity.
“We received and notified many Tier 1 upstreams regarding very very large DDoS attacks against small ISPs,” Nascimento said. “We didn’t dig deep enough at the time, and what you sent makes that clear.”
Nascimento said the unauthorized activity is likely related to a digital intrusion first detected in January 2026 that compromised two of the company’s development servers, as well as his personal SSH keys. But he said there’s no evidence those keys were used after January.
“We notified the team in writing the same day, wiped the boxes, and rotated keys,” Nascimento said, sharing a screenshot of a January 

---
*Synthesized by AutonomousLearner*
