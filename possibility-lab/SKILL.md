---
name: possibility-lab
description: "Use when the user wants to capture, supplement, audit, deduplicate, or review ideas in a Lark/Feishu Base idea registry. Trigger on requests to record ideas, add ideas to an idea registry, scan a conversation for ideas, enrich rough ideas with evidence, run an idea review, or prepare structured Lark/Feishu Base rows."
---

# Possibility Lab

Use this skill to turn raw ideas into concise, evidence-aware records for a Lark/Feishu Base idea registry.

Default language: match the user's language. If the user writes in Chinese, respond in Chinese.

## Configuration

Before reading or writing Lark/Feishu records, confirm the registry configuration is available.

Prefer these environment variables when present:

```bash
LARK_BASE_TOKEN
LARK_TABLE_ID
LARK_IDENTITY
```

Use `LARK_IDENTITY=user` when it is missing. If `LARK_BASE_TOKEN` or `LARK_TABLE_ID` is missing, ask the user for the target Base token and table id before attempting any read or write command.

Do not hard-code private Base URLs, tokens, table ids, exported records, or local absolute paths into outputs or saved artifacts.

## Core Rules

1. Do not add decorative title prefixes.
   - Good: `Cloud document archive syncer`
   - Bad: `Idea | Cloud document archive syncer`
   - Bad: `Agent Skill Idea | Cloud document archive syncer`
2. Before creating records, read existing records and deduplicate by title and close semantic overlap.
3. Prefer writing to the registry when the user asks to record, supplement, save, or add ideas.
4. Keep each record actionable: include why it matters, smallest validation, success signal, failure signal, upgrade condition, and next step.
5. If the request is ambiguous, infer from the recent conversation before asking.
6. If tool access or registry configuration is missing, produce a ready-to-import JSON payload instead of pretending the write succeeded.

## Lark CLI Commands

When `lark-cli` is available, use these command shapes and substitute configuration from the environment or user-provided values.

List records:

```bash
lark-cli base +record-list --as "${LARK_IDENTITY:-user}" \
  --base-token "$LARK_BASE_TOKEN" \
  --table-id "$LARK_TABLE_ID" \
  --format json --limit 200
```

Create records in batch:

```bash
lark-cli base +record-batch-create --as "${LARK_IDENTITY:-user}" \
  --base-token "$LARK_BASE_TOKEN" \
  --table-id "$LARK_TABLE_ID" \
  --json @/absolute/path/to/payload.json \
  --format json
```

List fields when schema verification is needed:

```bash
lark-cli base +field-list --as "${LARK_IDENTITY:-user}" \
  --base-token "$LARK_BASE_TOKEN" \
  --table-id "$LARK_TABLE_ID" \
  --format json
```

## Suggested Fields

Use these fields when the target registry supports them. If the user's schema differs, map to the closest available fields after listing fields.

- `Title`: natural title, no prefix
- `Raw idea`: concise description of the original idea
- `Theme`: broader motif, strategic bucket, or recurring pattern
- `Recommended form`: likely product, workflow, report, template, service, content format, research artifact, or system
- `Evidence level`: one of `L0 none`, `L1 intuition`, `L2 specific feedback`, `L3 small experiment signal`, `L4 strong demand signal`, `L5 scalable evidence`
- `Evidence`: why this idea is worth recording now
- `Smallest validation`: the cheapest test that can produce evidence
- `Success signal`: what would prove the idea has traction
- `Failure signal`: what would show it is not worth pursuing now
- `Upgrade condition`: what would move it to a stronger status or project
- `Next step`: one concrete next action
- `Status`: usually `material`, `experiment`, or `project candidate`
- `Value type`: choose from culture, education, content, tool, business, community, system, artwork, research
- `Tags`: choose from available options when clearly applicable; omit otherwise

If the registry uses Chinese field names, use:

- `标题`
- `原始想法`
- `母题`
- `最推荐形态`
- `当前证据等级`
- `验证证据`
- `最小验证`
- `成功信号`
- `失败信号`
- `升级条件`
- `下一步`
- `状态`
- `价值形态`
- `标签`

## Evidence Defaults

- Raw conversation ideas: `Status = material`, `Evidence level = L1 intuition`
- Ideas backed by a document, repeated request, or visible workflow pain: `Status = project candidate`, `Evidence level = L2 specific feedback`
- Already tested workflows: `Status = experiment`, `Evidence level = L3 small experiment signal`

Never inflate evidence. If the recommendation is based on taste or intuition, say so.

## Workflow

1. Collect candidate ideas from the current request, recent conversation, local reports, or registry scan evidence.
2. Verify configuration and list existing records.
3. Remove duplicates and near-duplicates.
4. Map fields to the target schema.
5. Build a batch-create JSON payload.
6. Save the payload under the current workspace `reports/` directory when practical.
7. Create records with `lark-cli`, or return the payload if writing is not possible.
8. Report the exact titles created and any candidates skipped as duplicates.

## Quality Bar

Add an idea only when it is more than a phrase. It should have at least one of:

- a real pain point
- a repeated workflow
- a reusable method
- a concrete artifact that could be built
- evidence from documents, files, user feedback, or conversation history
- a clear next validation

Do not create records that are only decorative wording, vague aspirations, or duplicate labels.
