# Day 01 – What Is Automation? + My First Scheduled Script

Part of my **#30DaysOfAutomation** challenge.

## What I learned today

"Automation" is not one thing. There are 3 main types:

| | RPA | Workflow automation | AI agents |
| --- | --- | --- | --- |
| How it works | A software robot clicks and types on the screen like a person | Connects apps through APIs and triggers | An AI model (LLM) reads, reasons and decides the next step |
| Best for | Old systems with no API, stable rule-based tasks | Moving data between modern cloud apps | Messy input: emails, documents, decisions |
| Weakness | Breaks when the screen changes | Can't handle unclear input | Less predictable, needs guardrails |
| Example | Typing invoices into an old ERP system | New lead → Google Sheet → Slack alert | Reading support emails and drafting replies |
| Tools | UiPath, Power Automate, Automation Anywhere | n8n, Make, Zapier | LLM APIs, n8n AI Agent node, UiPath Agentic |

**My takeaway:** RPA automates *actions*, AI agents automate *decisions*. Many companies use both together: AI handles the messy input, and RPA does the repetitive clicking.

## Mini project: my first scheduled script

Every automation has two parts:
- **Trigger**: what starts it (a schedule, a new email, a webhook)
- **Task**: what it does

`hello_automation.py` uses a time schedule as the trigger and writes a log line as the task. No human clicks anything.

### How to run
```bash
# Run once
python3 hello_automation.py

# Run every 10 seconds (press Ctrl + C to stop)
python3 hello_automation.py --every 10
```

Every run is saved to `automation_log.txt`.

### Output
```
2026-11-01 10:00:00  Hello! The bot ran by itself.
2026-11-01 10:00:10  Hello! The bot ran by itself.
2026-11-01 10:00:20  Hello! The bot ran by itself.
```

## Resources I read
- [How to explain RPA in plain English – The Enterprisers Project](https://red.ht/3lwwdzb)
- [What Is RPA? – Built In](https://builtin.com/articles/what-is-rpa)
- [RPA vs. AI Agents – Zencoder](https://zencoder.ai/blog/rpa-vs-ai-agents)
- [RPA vs AI Agents: the real difference – Assistents.ai](https://assistents.ai/blog/rpa-vs-ai-agents-the-real-difference)
- [Building Effective Agents – Anthropic](https://www.anthropic.com/engineering/building-effective-agents)
