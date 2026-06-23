---
name: possibility-lab
description: "Use when the user wants to capture, supplement, audit, deduplicate, or review ideas in a Lark/Feishu Base idea registry. Trigger on requests to record ideas, add ideas to an idea registry, scan a conversation for ideas, enrich rough ideas with evidence, run an idea review, prepare structured Lark/Feishu Base rows, or initialize a Chinese-first idea registry."
---

# Possibility Lab

Use this skill to turn raw ideas into concise, evidence-aware records for a Lark/Feishu Base idea registry.

Default language: match the user's language. If the user writes in Chinese, respond in Chinese. Default registry field locale: `zh`.

## Configuration

Before reading or writing Lark/Feishu records, confirm registry configuration exists through environment variables or `config.local.json`.

Supported configuration keys:

- `LARK_CLI_PATH`, `LARK_CLI_COMMAND`, or `config.local.json` keys `lark_cli_path` / `lark_cli_command`
- `LARK_BASE_TOKEN` or `config.local.json` key `base_token`
- `LARK_TABLE_ID` or `config.local.json` key `table_id`
- `LARK_IDENTITY` or `config.local.json` key `identity`; default to `user`
- `LARK_FIELD_LOCALE` or `config.local.json` key `field_locale`; default to `zh`

Never hard-code private Base URLs, tokens, table ids, exported records, or local absolute paths into skill files, outputs, reports, or commits.

## Resource Navigation

- Use `scripts/resolve_lark_cli.py` to resolve the exact Lark CLI command. Do not guess alternative command names.
- Use `scripts/write_ideas_to_lark.py` for payload mapping, dry-run validation, duplicate checks, batch payload creation, and writes.
- Use `scripts/init_lark_registry.py` to create a safe registry setup plan and optionally write `config.local.json`.
- Read `references/schema.md` when field names, Chinese/English mappings, or evidence/status options matter.
- Read `references/lark-cli.md` when CLI configuration, dry-run, write, or common failure handling matters.

## Core Rules

1. Do not add decorative title prefixes.
   - Good: `飞书云端到本地归档同步器`
   - Bad: `Idea｜飞书云端到本地归档同步器`
2. Before creating records, deduplicate by title. Treat semantic near-duplicate detection as a human/agent review layer after title checks.
3. Prefer dry-run first:
   - Build or receive an idea payload.
   - Run `write_ideas_to_lark.py <payload> --dry-run --write-report`.
   - Only perform a real write after dry-run succeeds and the user clearly wants to write.
4. Keep each record actionable: include evidence level, why it matters, smallest validation, success signal, failure signal, upgrade condition, and next step.
5. If configuration, CLI access, field-list, or record-list fails, do not claim success. Return a ready-to-import JSON payload and explain what is missing.
6. Final replies must list exact created titles and skipped duplicate titles. Do not expose local absolute paths, Base tokens, or table ids.

## Standard Workflow

1. Extract candidate ideas from the request, conversation, notes, or reports.
2. Keep only ideas with a real pain point, repeated workflow, reusable method, concrete artifact, evidence, or clear validation path.
3. Build a JSON payload using Chinese field names by default. English keys are accepted and mapped by the writer script.
4. Run:

```bash
python3 possibility-lab/scripts/write_ideas_to_lark.py payload.json --dry-run --write-report
```

5. Review `created`, `skipped_duplicates`, `dropped_fields`, and `missing_configuration` in the report.
6. If the user confirms writing and dry-run is clean, run:

```bash
python3 possibility-lab/scripts/write_ideas_to_lark.py payload.json --write-report
```

7. Report the outcome without leaking secrets.

## Evidence Defaults

- Raw conversation ideas: `状态 = 素材`, `当前证据等级 = L1 个人直觉`
- Ideas backed by a document, repeated request, or visible workflow pain: `状态 = 项目候选`, `当前证据等级 = L2 具体反馈`
- Already tested workflows: `状态 = 实验`, `当前证据等级 = L3 小实验信号`

Never inflate evidence. If the recommendation is based on taste or intuition, say so.
