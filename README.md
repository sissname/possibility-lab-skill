# Possibility Lab Skill

Possibility Lab is a Codex skill for capturing raw ideas, deduplicating them against an existing Lark/Feishu Base, and turning them into concise, evidence-aware idea registry records.

The default registry language is Chinese (`field_locale=zh`). English payload keys are accepted and mapped to Chinese fields.

## What It Does

- Extracts candidate ideas from a request, conversation, note, or report.
- Maps English or Chinese payload keys into a consistent idea registry schema.
- Checks existing registry rows before creating duplicate titles.
- Runs a dry-run before writing and reports what would be created, skipped, dropped, or blocked.
- Writes records through `lark-cli` when configuration is available.
- Produces a ready-to-import JSON payload when direct writing is not possible.

## Install

Copy the skill folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R possibility-lab ~/.codex/skills/
```

Then invoke it explicitly:

```text
Use $possibility-lab to scan this Chinese conversation, deduplicate ideas, run a dry-run, and prepare rows for my Feishu/Lark Idea Registry.
```

## Configure

Create a local config from the example:

```bash
cp config.example.json config.local.json
```

Edit `config.local.json` with your local values:

```json
{
  "lark_cli_path": "",
  "lark_cli_command": "lark-cli",
  "base_token": "your_base_token",
  "table_id": "your_table_id",
  "identity": "user",
  "field_locale": "zh"
}
```

You can also use environment variables:

```bash
export LARK_CLI_COMMAND="lark-cli"
export LARK_BASE_TOKEN="your_base_token"
export LARK_TABLE_ID="your_table_id"
export LARK_IDENTITY="user"
export LARK_FIELD_LOCALE="zh"
```

CLI resolution order is `LARK_CLI_PATH`, `LARK_CLI_COMMAND`, `config.local.json`, then `lark-cli` on `PATH`.

## Dry-Run

Always dry-run before writing:

```bash
python3 possibility-lab/scripts/write_ideas_to_lark.py examples/idea-payload.zh.json --dry-run --write-report
```

Dry-run validates configuration, resolves the CLI, maps fields, checks duplicate titles when record listing is available, and writes a report under `reports/`.

The report includes:

- `would_create`
- `created`
- `skipped_duplicates`
- `dropped_fields`
- `missing_configuration`
- `batch_payload`

If configuration is missing, dry-run still returns a ready-to-import payload instead of pretending the write succeeded.

## Write

After dry-run succeeds and you are ready to write:

```bash
python3 possibility-lab/scripts/write_ideas_to_lark.py payload.json --write-report
```

The script writes through `lark-cli base +record-batch-create` and does not print token values.

## Initialize A Registry

Prepare a schema plan:

```bash
python3 possibility-lab/scripts/init_lark_registry.py --dry-run --field-locale zh
```

Write a local config file after you have a Base token and table id:

```bash
python3 possibility-lab/scripts/init_lark_registry.py \
  --write-config \
  --base-token "your_base_token" \
  --table-id "your_table_id" \
  --field-locale zh
```

`config.local.json` is ignored by Git.

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

## Validate

```bash
python3 -m py_compile possibility-lab/scripts/*.py
python3 -m unittest discover -s tests
python3 /path/to/quick_validate.py possibility-lab
```

## Privacy

This public package does not include private Base URLs, table ids, exported records, local file paths, or personal workspace data.

Do not commit:

- `config.local.json`
- real tokens or table ids
- exported registry data
- write reports
- batch payloads containing private ideas

## License

MIT
