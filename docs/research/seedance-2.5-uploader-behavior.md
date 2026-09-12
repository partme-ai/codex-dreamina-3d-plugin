# Seedance 2.5 / Dreamina Uploader — Observed External Behavior

> **Scope.** Behavior study only. No vendor source, UI strings, identifiers,
> local bridge protocol, or bundled ffmpeg is incorporated into the
> implementation. All references to vendor products identify interoperability
> targets and remain the property of their respective owners.

## Observed artefacts

| Artefact                                                    | Hash (SHA-256)                                                     |
|-------------------------------------------------------------|---------------------------------------------------------------------|
| Official Blender 1.0.0 reference package                    | `471b315b8da91023be46496f902f7d64c1b48b91567d10cd442de7dffe0d68ae`  |

The hash is recorded here for traceability of the behaviour study. The
orchestrator never reuses the reference package itself; the public DCC and
Dreamina CLI contracts are the only inputs to the implementation.

## Observed behaviour

- **Camera-render preview mode.** The official uploader emits an MP4 from the
  active camera at the configured resolution and frame range.
- **Local-video preview mode.** When the source is a previously-rendered video
  the uploader passes it through with a temporary-settings restoration step.
- **Temporary-setting restoration.** Camera and output overrides are restored
  after the export regardless of success or failure. The receipt must carry a
  `restoration.status` field.
- **H.264 / MP4 only.** Codec and container are fixed by the protocol; the
  orchestrator rejects any other combination.
- **Protocol-driven limits.** Maximum 60 seconds, dimensions in
  [16, 4096], fps in [1, 120], single explicit camera, single explicit frame
  range.
- **Local web bridge.** The reference package exposes a local-only web bridge
  for browser-based progress inspection. This implementation does NOT replicate
  the bridge; status is conveyed via the public CLI/JSON contract.

## Excluded inputs

The following inputs were intentionally NOT copied into this plugin:

- Vendor Python or JavaScript source files.
- UI strings, screenshots, or iconography tied to the vendor's branding.
- Local bridge protocol details or message shapes.
- Bundled `ffmpeg` or any other media binary.
- Any vendor credentials or sample output media.

## Implications for the orchestrator

- The handoff validator (Task 1) enforces the protocol-driven limits listed
  above as a closed set.
- The companion adapters (Tasks 4 / 5) are invoked only via argv and JSON
  contracts so the orchestrator's behaviour is independent of the vendor's
  internal implementation.
- No part of this plugin opens a local web bridge; status is reported through
  the design plugin's public query endpoint.