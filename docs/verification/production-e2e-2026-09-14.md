# Production E2E Acceptance — 2026-09-14

Release scope: macOS, Blender 5.2.1 LTS, Dreamina Design MCP 0.3.0.

## State evidence

| Gate | Result | Evidence |
|---|---|---|
| `PreviewValidated` | `PASS` | Installed implementation produced a 48-frame H.264 MP4; receipt and independent re-hash matched. |
| Blender public adapter entry | `FAIL` | `bin/blender_adapter` imports missing module `blender_adapter`; direct installed `scripts/dreamina_adapter.py` was required. |
| Dreamina MCP initialize | `PASS` | Server reported protocol `2025-06-18`, name `dreamina-design`, version `0.3.0`. |
| Dreamina MCP CLI readiness | `PASS` | `installed=true`, `trusted=true`, all eight advertised generation modes present. |
| Dreamina MCP account readiness | `PASS` | `dreamina_account` returned a redacted usable credit result; identity fields are intentionally omitted here. |
| Dreamina native denial | `PASS` | Native dialog Cancel returned `ApprovalDeniedError`; no operation-ledger file or submit ID was created. |
| `JimengLinkReady` | `OPTIONAL_UNAVAILABLE` | Blender 5.2.1 factory-startup add-on registry returned no Jimeng/Dreamina/即梦 official add-on. |
| New MCP paid canary | `NOT_RUN` | Requires a separately approved exact paid request after the denial and Blender gates pass. |
| `Completed` | `NOT_RUN` | Cannot be claimed before a validated Blender preview, one stored submit ID, terminal query, verified download, ffprobe, and independent SHA-256. |

## Exact probes

```text
/Applications/Blender.app/Contents/MacOS/Blender --version
Blender 5.2.1 LTS

installed bin/blender_adapter --help
ModuleNotFoundError: No module named 'blender_adapter'

installed implementation through managed Harness
1920x1080, H.264, 24 fps, 2.000 s, 104428 bytes
sha256=b8b5b7607d29b4ac02da83117078b491badd22e0a81e995aa09c0402e18847bb
restoration.status=confirmed
orchestrator_validation_errors=[]

Blender --background --factory-startup official add-on probe
OFFICIAL_ADDON_PROBE=[]
```

The Dreamina MCP read-only calls were made against the public installed cache,
not the source checkout. No credential, account identifier, approval material,
or absolute private cache path is recorded in this evidence.

The denial probe used Seedance 2.5, 480p, 4 seconds, and one locally generated
MP4 reference under an approved temporary root. The server returned
`isError=true`, `requires_user_action=true`, and a non-retryable
`ApprovalDeniedError`. Only an approval-session record changed; the operations
directory had no new file, proving the CLI generation command was not invoked.

## No gate inflation

`PreviewValidated`, `JimengLinkReady`, `Submitted`, `Querying`, and `Completed`
remain separate. CLI readiness and account readiness do not satisfy a paid
submission gate; a native approval dialog does not prove submission; a remote
success state does not prove final artifact acceptance.
