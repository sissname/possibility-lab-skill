# Idea Registry Schema

Default field locale: `zh`.

## Chinese Fields

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
- `价值类型`
- `标签`

## English Field Compatibility

The writer maps these English keys to Chinese fields when `field_locale=zh`:

| English key | Chinese field |
|---|---|
| `Title` | `标题` |
| `Raw idea` | `原始想法` |
| `Theme` | `母题` |
| `Recommended form` | `最推荐形态` |
| `Evidence level` | `当前证据等级` |
| `Evidence` | `验证证据` |
| `Smallest validation` | `最小验证` |
| `Success signal` | `成功信号` |
| `Failure signal` | `失败信号` |
| `Upgrade condition` | `升级条件` |
| `Next step` | `下一步` |
| `Status` | `状态` |
| `Value type` | `价值类型` |
| `Tags` | `标签` |

Common lowercase and snake_case aliases are also accepted, such as `title`, `raw_idea`, `evidence_level`, `next_step`, and `value_type`.

## Evidence Levels

- `L0 无证据`
- `L1 个人直觉`
- `L2 具体反馈`
- `L3 小实验信号`
- `L4 强需求信号`
- `L5 可扩展证据`

## Status Options

- `灵感`
- `素材`
- `实验`
- `项目候选`
- `项目`
- `归档`

## Value Type Options

- `文化`
- `教育`
- `内容`
- `工具`
- `商业`
- `社区`
- `系统`
- `作品`
- `研究`

## English Defaults

When `field_locale=en`, the writer maps Chinese keys back to the English field names listed above and uses English defaults such as `material`, `experiment`, and `project candidate`.
