---
title: "Lawmakers Demand Answers as CISA Tries to Contain Data Leak"
source: https://krebsonsecurity.com/2026/05/lawmakers-demand-answers-as-cisa-tries-to-contain-data-leak/
date: 2026-06-01
tags:
  - news
  - auto-learning
  - auto-injected
---

# Lawmakers Demand Answers as CISA Tries to Contain Data Leak

Lawmakers in both houses of Congress are demanding answers from the U.S. Cybersecurity & Infrastructure Security Agency (CISA) after KrebsOnSecurity reported this week that a CISA contractor intentionally published AWS GovCloud keys and a vast trove of other agency secrets on a public GitHub account. The inquiry comes as CISA is still struggling to contain the breach and invalidate the leaked credentials.
On May 18, KrebsOnSecurity reported that a CISA contractor with administrative access to the agency’s code development platform had created a public GitHub profile called “Private-CISA” that included plaintext credentials to dozens of internal CISA systems. Experts who reviewed the exposed secrets said the commit logs for the code repository showed the CISA contractor disabled GitHub’s built-in protection against publishing sensitive credentials in public repos.
CISA acknowledged the leak but has not responded to questions about the duration of the data exposure. However, experts who reviewed the now-defunct Private-CISA archive said it was originally created in November 2025, and that it exhibits a pattern consistent with an individual operator using the repository as a working scratchpad or synchronization mechanism rather than a curated project repository.
In a written statement, CISA said “there is no indication that any sensitive data was compromised as a result of the incident.” But in a May 19 a letter (PDF) to CISA’s Acting Director Nick Andersen, Sen. Maggie Hassan (D-NH) said the credential leak raises serious questions about how such a security lapse could occur at the very agency charged with helping to prevent cyber breaches.
“This reporting raises serious concerns regarding CISA’s internal policies and procedures at a time of significant cybersecurity threats against U.S. critical infrastructure,” Sen. Hassan wrote.
A May 19 letter from Sen. Margaret Hassan (D-NH) to the acting director of CISA demanded answers to a dozen questions about the breach.
Sen. Hassan noted that the incident occurred against the backdrop of major disruptions internally at CISA, which lost more than a third of it workforce and almost all of its senior leaders after the Trump administration forced a series of early retirements, buyouts, and resignations across the agency’s various divisions.
Rep. Bennie Thompson (D-MS), the ranking member on the House Homeland Security Committee, echoed the senator’s concerns.
“We are concerned that this incident reflects a diminished security culture and/or an inability for CISA to adequately manage its contract support,” Thompson wrote in a May 19 letter to the acting CISA chief that was co-signed by Rep. Delia Ramirez (D-Ill), the ranking member of the panel’s Subcommittee on Cybersecurity and Infrastructure Protection. “It’s no secret that our adversaries — like China, Russia, and Iran — seek to gain access to and persistence on federal networks. The files contained in the ‘Private-CISA’ repository provided the information, access, and roadmap to do just that.”
KrebsOnSecurity has learned that more a week after CISA was first notified of the data leak by the security firm GitGuardian, the agency is still working to invalidate and replace many of the exposed keys and secrets.
On May 20, KrebsOnSecurity heard from Dylan Ayrey, the creator of TruffleHog, an open-source tool for discovering private keys and other secrets buried in code hosted at GitHub and other public platforms. Ayrey said CISA still hadn’t invalidated an RSA private key exposed in the Private-CISA repo that granted access to a GitHub app which is owned by the CISA enterprise account and installed on the CISA-IT GitHub organization with full access to all code repositories.
“An attacker with this key can read source code from every repository in the CISA-IT organization, including private repos, register rogue self-hosted runners to hijack CI/CD pipelines and access repository secrets, and modify repository admin settings including branch protection rules, webhooks, and deploy keys,” Ayrey told KrebsOnSecurity. CI/CD stands for Continuous Integration and Continuous Delivery, and it refers to a set of practices used to automate the building, testing and deployment of software.
KrebsOnSecurity notified CISA about Ayrey’s findings on May 20. Ayrey said CISA appears to have invalidated the exposed RSA private key sometime after that notification. But he noted that CISA still hasn’t rotated leaked credentials tied to other critical security technologies that are deployed across the agency’s technology portfolio (KrebsOnSecurity is not naming those technologies publicly for the time being).
CISA responded with a brief written statement in response to questions about Ayrey’s findings, saying “CISA is actively responding and coordinating with the appropriate parties and vendors to ensure any identified leaked credentials are rotated and rendered invalid and will continue to take appropriate steps to protect the security of o

---
*Synthesized by AutonomousLearner*
