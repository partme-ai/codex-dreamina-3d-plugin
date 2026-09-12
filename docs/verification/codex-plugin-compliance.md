# Codex Plugin Contract Compliance

Audit of `codex-dreamina-3d` against the official Codex plugin building
contract, performed 2026-09-12.

## Sources

- <https://developers.openai.com/plugins/build/plugins> — official builder docs
- <https://learn.chatgpt.com/docs/build-plugins> — plugin structure overview
- `plugin-creator/references/plugin-json-spec.md` — shipped with the local
  Codex install, the canonical manifest and marketplace sample spec
- `plugin-creator/references/installing-and-updating.md` — install and local
  iteration loop
- `plugin-creator/scripts/validate_plugin.py` — OpenAI's own validator

## Verdict

**`validate_plugin.py` passes against this plugin.**

```text
$ python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
Plugin validation passed: /Users/wandl/workspaces/workspace-partme-ai/codex-dreamina-3d-plugin
```

## Manifest (`.codex-plugin/plugin.json`)

| Rule | Status | Evidence |
|---|---|---|
| Manifest lives at `.codex-plugin/plugin.json` | PASS | present |
| `.codex-plugin/` contains *only* `plugin.json` | PASS | directory holds one file |
| `name` kebab-case, matches plugin identity | PASS | `codex-dreamina-3d` |
| `version` strict semver | PASS | `0.1.0` |
| `description` non-empty | PASS | present |
| `author.name` non-empty | PASS | `Full Stack Skills / PartMe.AI` |
| `author` has no unknown keys | PASS | only `name`, `url` |
| No unaccepted top-level fields | PASS | `validate_plugin.py` rejects extras such as `hooks`; we declare none |
| `interface.{displayName,shortDescription,longDescription,developerName,category}` non-empty | PASS | all present |
| `interface.defaultPrompt` present | PASS | 3 entries, all ≤128 chars |
| `interface.capabilities` is a non-empty-string array | PASS | `["Interactive","Read","Write"]` |
| `websiteURL`/`privacyPolicyURL`/`termsOfServiceURL` absolute `https://` | PASS | all three GitHub URLs |
| `brandColor` matches `#RRGGBB` | PASS | `#7C3AED` |
| `composerIcon`/`logo`/`logoDark` point to real files in the archive | PASS | `assets/*.png` verified on disk |
| `interface.screenshots` is an array of real PNGs | PASS | empty array |
| `skills` resolves to `skills` | PASS | `./skills/` |
| No `[TODO: ...]` placeholders | PASS | none |
| Optional capabilities absent when unused | PASS | no `hooks`, no `.mcp.json`, no `.app.json` |

## Skills

| Rule | Status | Evidence |
|---|---|---|
| `skills/` at plugin root | PASS | present |
| Each skill dir has `SKILL.md` | PASS | 4/4 |
| `SKILL.md` starts with `---\n` and closes frontmatter | PASS | 4/4 |
| Frontmatter is valid YAML object | PASS | 4/4 |
| Frontmatter `name` non-empty and matches directory | PASS | verified per skill |
| Frontmatter `description` non-empty | PASS | 4/4 |
| `disable-model-invocation` absent or false | PASS | absent |

## Marketplace (`.agents/plugins/marketplace.json`)

| Rule | Status | Evidence |
|---|---|---|
| Top-level `name` identifies the marketplace | PASS | `partme-ai-dreamina-3d` |
| `interface.displayName` at top level, not per entry | PASS | `PartMe.AI Dreamina 3D` |
| Entry `name` matches plugin dir and manifest | PASS | `codex-dreamina-3d` |
| Entry has `source` | PASS | `{"source":"url","url":"...","ref":"main"}` (git-backed source is documented) |
| Entry has `policy.installation` | PASS | `AVAILABLE` (allowed value) |
| Entry has `policy.authentication` | PASS | `ON_USE` (allowed value) |
| Entry has `category` | PASS | `Creativity` |
| `policy.products` omitted (override only) | PASS | omitted |

## Install path (personal marketplace)

Codex resolves `source.path` relative to the marketplace root. For
`~/.agents/plugins/marketplace.json` the root is the home directory, so this
entry resolves correctly:

```json
{ "name": "codex-dreamina-3d",
  "source": { "source": "local",
              "path": "./workspaces/workspace-partme-ai/codex-dreamina-3d-plugin" } }
```

Verified end to end:

```text
$ codex plugin add codex-dreamina-3d@personal
Added plugin `codex-dreamina-3d` from marketplace `personal`.
Installed plugin root: ~/.codex/plugins/cache/personal/codex-dreamina-3d/0.1.0

$ codex plugin list
codex-dreamina-3d@personal  installed, enabled  0.1.0
```

> The documented example layout places plugins under `./plugins/<name>`
> (`~/plugins/<name>`). This repository keeps its source in
> `~/workspaces/...`, matching the existing `stitch-design` entry, which
> resolves the same way.

## Cachebuster / local iteration loop

The documented update loop requires bumping the manifest version to
`<base-version>+codex.<cachebuster>` before reinstalling, so Codex does not
serve a cached copy.

This was a **real conflict** found during the audit: our own
`scripts/validate_distribution.py` hard-pinned `version == "0.1.0"` and
rejected the cachebuster form that the documented loop mandates. Fixed in
`65a1711`'s successor — the validator now accepts strict semver whose base is
`0.1.0`, with or without a build-metadata suffix:

| Version | Before fix | After fix |
|---|---|---|
| `0.1.0` | accept | accept |
| `0.1.0+codex.20260912062630` | **reject** | accept |
| `0.2.0` | reject | reject |
| `v1` | reject | reject |

`scripts/local_install.py --cachebuster` now applies the documented policy
(preserve the base, replace any existing token) and OpenAI's own
`update_plugin_cachebuster.py` was verified to leave the manifest still valid:

```text
$ python3 update_plugin_cachebuster.py <plugin>
Updated plugin version: 0.1.0 -> 0.1.0+codex.20260912062630
$ python3 validate_plugin.py <plugin>
Plugin validation passed
```

## Deliberate stricter-than-required choices

These are our own constraints, not contract violations:

- `validate_distribution.py` rejects `mcpServers`/`.mcp.json` until an MCP
  server actually exists. The contract permits them; we forbid them while
  unused so the manifest cannot advertise a transport we do not ship.
- The portable root `plugin.json` / `mcp.json` stay inactive, as recorded in
  [portable-migration.md](../portable-migration.md).

## Residual note

`interface.capabilities` values are not enumerated by the contract validator;
it requires only an array of non-empty strings. We use the same
`["Interactive","Read","Write"]` set as the working `stitch-design` reference.
