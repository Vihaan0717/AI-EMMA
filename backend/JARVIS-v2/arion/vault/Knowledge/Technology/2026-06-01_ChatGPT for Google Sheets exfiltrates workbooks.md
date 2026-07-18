---
title: "ChatGPT for Google Sheets exfiltrates workbooks"
source: https://www.promptarmor.com/resources/gpt-for-google-sheets-data-exfiltration
date: 2026-06-01
tags:
  - news
  - auto-learning
  - auto-injected
---

# ChatGPT for Google Sheets exfiltrates workbooks

Threat Intelligence
ChatGPT for Google Sheets Exfiltrates Workbooks
ChatGPT for Google Sheets is vulnerable to data exfiltration and phishing overlay attacks that affect workbooks across the victim’s account after an indirect prompt injection in a single sheet.
This attack does not require human-in-the-loop approvals, even when in settings the user has explicitly required human approval before ChatGPT edits workbooks.
UPDATE from OpenAI:
"We appreciate the security research here, and it’s unfortunate this one slipped through a crack in our disclosure pipeline. As we’re now aware of this report, we’ve taken immediate steps to protect users against potential attacks in this area by removing the model’s ability to generate Apps Script code, which should eliminate the risk to users of ChatGPT for Google Sheets. We’re taking a close look at how this feature interacts with Google Sheets APIs and re-evaluating our sandboxing approach to make sure this product is as resistant as possible against prompt injection attacks. More broadly, we’ll be doing a re-review of similar functionality in other surfaces to make sure that our defenses are consistent and effective across the board."
Recently, OpenAI launched an AI extension for using ChatGPT in Google Sheets, which has accumulated over 185,000 downloads since its launch less than a month ago. This allows users to operate on their spreadsheets by interacting with an AI chatbot that lives in a sidebar, with the added benefit of drawing on data from ChatGPT connectors.
A single indirect prompt injection attack triggered by a single benign user query can trigger all of the following effects at once:
Exfiltration of many workbooks from across the victim’s account
Display of an interactive phishing pop-up
Overwriting the entire GPT sidebar with an attacker-controlled chatbot interface
Attacker-controlled edits to your workbooks
This attack occurs when any untrusted data source (e.g., from an imported sheet or ChatGPT connector) manipulates ChatGPT to run an attacker-controlled external script, which executes leveraging permissions the user has granted to the ChatGPT for Google Sheets extension.
This vulnerability was responsibly disclosed to OpenAI. Despite multiple follow-ups, we received no communication beyond an automated reply to our initial disclosure. OpenAI's documentation fails to describe sensitive capabilities granted to the model (e.g., running privileged scripts) or risks of model manipulation via indirect prompt injection, instead focusing solely on functional limitations and data-handling concerns. As such, we are publishing our findings to enable informed decision-making regarding the risk surface.
Note: ChatGPT for Google Sheets has a setting called ‘Apply edits automatically’ that determines when human approvals are required before an agentic action completes. However, this attack succeeds even when the user has explicitly disabled automatic edits.
Below, the attacker's server logs show the user’s exfiltrated financial model.
Here, the internal financial model sheet included a link to another spreadsheet relevant to budgeting. The malicious script identifies the spreadsheet URL in the stolen data and exfiltrates the newly discovered workbook. It then continues to process the stolen data, identifying and exfiltrating additional workbooks, eventually exfiltrating 12 in total.
Note: Clicking the ‘stop’ button in the ChatGPT sidebar does not stop scripts that have started from finishing execution.
In addition to the data exfiltration described above, the same attacker-controlled scripts enable a malicious actor to target two variants of a phishing overlay attack.
Variant 1: A sidebar is opened that overlays the ChatGPT for Google Sheets extension with an attacker-controlled site, allowing the attacker to impersonate the extension. The malicious sidebar can execute scripts that edit the sheet in the same way ChatGPT can, allowing it to act in most of the ways the extension normally does, while also performing malicious activities such as:
Harvesting all user prompts
Providing the user with a misaligned chatbot to interact with
Convincing the user to ‘reconnect’ connectors to gain access to additional apps
Displaying a phishing UI to steal credentials for OpenAI
Variant 2: A pop-up modal is opened that renders an attacker-controlled website to phish the user for credentials.
Organizations can leverage the following configuration to control access to ChatGPT for Google Sheets:
Workspace settings > Permissions & roles > ChatGPT for Excel and Google Sheets
UPDATE: OpenAI has responded; details are at the top of the article.
This vulnerability was responsibly disclosed to OpenAI. Despite multiple follow-ups, we received no communication beyond an automated reply to our initial disclosure. OpenAI's documentation fails to describe sensitive capabilities granted to the model (e.g., running privileged scripts) or risks of model manipulation via indirect prompt injectio

---
*Synthesized by AutonomousLearner*
