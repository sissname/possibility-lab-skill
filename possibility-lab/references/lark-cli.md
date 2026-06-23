# Lark CLI Usage

Possibility Lab resolves the Lark CLI deterministically.

Resolution order:

1. `LARK_CLI_PATH`
2. `LARK_CLI_COMMAND`
3. `config.local.json` key `lark_cli_path`
4. `config.local.json` key `lark_cli_command`
5. `lark-cli` from `PATH`

Do not guess other command names.

## Dry-Run

Run dry-run before any write:

```bash
python3 possibility-lab/scripts/write_ideas_to_lark.py examples/idea-payload.zh.json --dry-run --write-report
```

Dry-run validates configuration, resolves the CLI, maps fields, checks title duplicates when records can be listed, identifies dropped fields, and writes a report when requested.

## Write

Only write after dry-run succeeds and the user clearly asks to write:

```bash
python3 possibility-lab/scripts/write_ideas_to_lark.py payload.json --write-report
```

The script creates a batch payload and calls:

```bash
lark-cli base +record-batch-create --as "$identity" --base-token "$base_token" --table-id "$table_id" --json @payload --format json
```

The script must not print token values.

## Failure Behavior

If CLI resolution, configuration, `field-list`, or `record-list` fails:

- Do not claim records were created.
- Return a report with `missing_configuration` or `errors`.
- Preserve a ready-to-import `batch_payload` in the report when possible.
- Keep local paths and secrets out of final user-facing summaries.
