# Codex Dreamina 3D Plugin Architecture

> Target orchestration architecture, not implemented. Updated 2026-09-11.

## Context

```mermaid
flowchart LR
    User --> Orchestrator[codex-dreamina-3d]
    Orchestrator --> Detect{DCC capability}
    Detect --> Blender[codex-blender]
    Detect --> Maya[codex-maya]
    Blender --> Preview[ArtifactReceipt]
    Maya --> Preview
    Preview --> Handoff[3D Handoff Validator]
    Handoff --> Design[codex-dreamina-design]
    Design --> Seedance[Seedance 2.5]
    Seedance --> Result[Generated ArtifactReceipt]
```

## Ownership

| Plugin | Owns |
|---|---|
| `codex-blender` | Blender scene inspection and preview export |
| `codex-maya` | Maya scene inspection and Playblast export |
| `codex-dreamina-design` | CLI capability, quotation, approval, submission, query, download |
| `codex-dreamina-3d` | capability selection, receipt validation, prompt handoff, end-to-end state |

## Journey

```mermaid
journey
    title 3D preview to Seedance result
    section Prepare
      Inspect scene: 5: User, DCC plugin
      Review preview settings: 5: User, DCC plugin
      Export and validate MP4: 4: DCC plugin
    section Generate
      Discover Seedance capability: 5: Design plugin
      Review quote and approve: 5: User
      Submit once: 4: Design plugin
      Query and download: 4: Design plugin
```

## Handoff contract

The incoming `ArtifactReceipt` must contain schema version, producer plugin/version, path, SHA-256, codec, dimensions, fps, duration, bytes, camera, frame range, preview mode, and restoration evidence. The orchestrator rejects stale files, hash mismatch, unsupported media, or unconfirmed restoration.

## Failure and recovery

Local export failures return to the DCC plugin. Remote unknown state returns to the Design operation ledger. The orchestrator never retries either side blindly and never converts one gate's success into end-to-end completion.

## Dependency model

Codex manifests do not currently provide a dependable hard cross-plugin dependency contract for this design. Runtime detection and clear install guidance are used; missing companions stop before any mutation or paid action.
