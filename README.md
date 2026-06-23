# Possibility Lab Skill

Possibility Lab is a Codex skill for capturing raw ideas, deduplicating them against an existing Lark/Feishu Base, and turning them into concise, evidence-aware idea registry records.

It is designed for idea inboxes, creative backlogs, product opportunity logs, research queues, and personal or team "idea registry" workflows.

## What It Does

- Extracts candidate ideas from a request, conversation, note, or report.
- Checks existing registry rows before creating duplicates.
- Structures each idea with evidence level, smallest validation, success and failure signals, upgrade condition, and next step.
- Writes records through `lark-cli` when registry configuration is available.
- Produces a ready-to-import JSON payload when direct writing is not possible.

## Install

Copy the skill folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R possibility-lab ~/.codex/skills/
```

Then invoke it explicitly, for example:

```text
Use $possibility-lab to record the useful ideas from this conversation into my Idea Registry.
```

## Configure Lark/Feishu

Set these environment variables before asking the skill to read or write records:

```bash
export LARK_BASE_TOKEN="your_base_token"
export LARK_TABLE_ID="your_table_id"
export LARK_IDENTITY="user"
```

`LARK_IDENTITY` defaults to `user` when omitted. The skill will ask for the Base token and table id if they are missing.

The skill expects `lark-cli` to be installed and authenticated when writing directly to Lark/Feishu. If it is unavailable, the skill should return a JSON payload you can import or run later.

## Example Requests

```text
Use $possibility-lab to scan this conversation and save any project-worthy ideas.
```

```text
Use $possibility-lab to deduplicate these raw ideas against my registry and prepare Feishu rows.
```

```text
Use $possibility-lab to turn this rough idea into an evidence-aware registry card.
```

## Privacy

This public package does not include private Base URLs, table ids, exported records, local file paths, or personal workspace data. Keep your registry credentials in environment variables or your local shell profile, not inside the skill.

## License

MIT
