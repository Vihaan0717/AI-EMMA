---
title: "Lockdown Mode"
source: https://help.openai.com/en/articles/20001061-lockdown-mode
date: 2026-06-06
tags:
  - news
  - auto-learning
  - auto-injected
---

# Lockdown Mode

Lockdown Mode is rolling out to eligible personal accounts, including Free, Go, Plus, and Pro, and self-serve ChatGPT Business accounts. If you do not see Lockdown Mode in your settings, it may not be available for your account yet.
Overview
Lockdown Mode is an optional advanced security setting that limits many tools and capabilities in OpenAI products that can connect to the web or external services. It is designed to reduce the risk of data exfiltration from prompt injection attacks by limiting outbound network requests, at the expense of disabling or limiting some useful features.
Lockdown Mode is not intended for everyone. It is designed for people and organizations that handle sensitive data and want stricter protection from data exfiltration risks related to prompt injection.
Availability
Lockdown Mode is available for all account types and workspaces. You must be logged in to use it.
How Lockdown Mode helps reduce data exfiltration risk
Prompt injection is a frontier, challenging research problem, and we are continually working to harden our multi-layered security and safety systems to protect users from such attacks.
Lockdown Mode builds on protections across the model, product, and system levels. This includes sandboxing, protections against URL-based data exfiltration, monitoring and enforcement, and enterprise controls like role-based access and audit logs.
Lockdown Mode is designed to help prevent the final stage of data exfiltration from a prompt injection attack by limiting outbound network requests that could transfer sensitive data to an attacker. Lockdown Mode does not prevent prompt injections from appearing in the content ChatGPT processes. For example, a prompt injection could appear in cached web content or in an uploaded file, and could still affect the behavior or accuracy of a response.
Specifically, for those in Lockdown Mode, the following capabilities of OpenAI products are disabled:
Live web browsing: Web browsing is limited to accessing only cached content. Search results may be limited, unavailable, or stale.
Image support: ChatGPT may not display images in regular responses or retrieve images from the web. Users can still upload image files, and image generation remains available where it is otherwise available.
Deep research: Deep research is disabled.
Agent mode: Agent mode is disabled.
Canvas networking: Users cannot approve Canvas-generated code to access the network.
File downloads: ChatGPT cannot download files for data analysis. ChatGPT can still operate on your manually uploaded files.
Lockdown Mode does not change memory, file uploads, the ability to share a conversation, or whether your conversations may be used to improve models. Many of these settings are separately configurable by workspace admins.
Lockdown Mode does not affect network access in Codex.
Apps
How apps and connectors work in Lockdown Mode depends on your account type and workspace settings.
For personal accounts and self-serve ChatGPT Business accounts, Lockdown Mode allows connectors that use synced data but blocks live connector access and connector write actions. Some connected experiences, including Finances in ChatGPT and shopping-agent experiences, are unavailable in Lockdown Mode.
For managed workspaces, apps, MCPs, and connectors are controlled by workspace settings and role-based access controls. Lockdown Mode does not automatically disable every app in these workspaces. Workspace admins should enable only the trusted apps and actions that members using Lockdown Mode need.
For managed workspace troubleshooting, review the member's role and app settings together. A member may be unable to use an app, connector, MCP, or action if:
the member or group is assigned to a Lockdown Mode role that limits the required capability
the app is not assigned to the member, group, or role
the required read or write action is not enabled
the member does not have access to the underlying file, repository, channel, record, or source system
App access in ChatGPT does not override permissions in the connected source system. For more information about assigning roles, see: RBAC.
When configuring apps for members using Lockdown Mode, admins should consider the data exfiltration risk of each app and action.
High risk
These apps and actions are not recommended for users in Lockdown Mode:
Read or write actions for untrusted apps are not recommended. Enable only apps you trust.
Write actions for trusted apps with broad or uncertain visibility are not recommended. Avoid enabling write actions, even for trusted apps, if you cannot confirm that the side effect is hidden from a malicious actor.
Medium risk
Use these with caution for users in Lockdown Mode:
Sync connectors are lower risk as a possible data exfiltration sink because the data being accessed is already synced to OpenAI, so queries do not send live network requests outside OpenAI. They can still act as sources of sensitive data that a malicious actor may try t

---
*Synthesized by AutonomousLearner*
