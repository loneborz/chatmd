<!-- lwa:meta
{
  "id": "CHAT-D1",
  "kind": "document",
  "title": "Portable Conversation Bundle Contract",
  "authority": "local-native",
  "revision": 2,
  "status": "active",
  "created_at": "2026-09-18T23:51:10Z",
  "updated_at": "2026-09-18T23:54:40Z",
  "owner": {
    "kind": "project",
    "id": "CHAT-P1"
  },
  "relations": []
}
-->
# Portable Conversation Bundle Contract

## Purpose

Define the durable product and interchange contract for ChatMD conversation bundles without prematurely fixing implementation details that belong to later Work.

ChatMD converts a public ChatGPT shared conversation into a portable, deterministic bundle for:

- durable human-readable archival;
- machine-readable ingestion;
- reuse by other systems;
- native use by Context World;
- possible future use through an Obsidian plugin.

## Bundle contract

A bundle has this structure:

```text
conversation/
├── manifest.json
├── conversation.md
└── assets/
```

### `manifest.json`

`manifest.json` is the sole authoritative machine-readable semantic, compatibility, provenance and integrity contract for the bundle.

It contains enough deterministic, portable information for a consumer to interpret the conversation, its ordering, its supported content and the integrity of bundle members without treating `conversation.md` as a semantic source of truth.

### `conversation.md`

`conversation.md` is a deterministic human-readable projection only.

It exists for durable reading and archival. It is not intended for reverse parsing and must not become a separate competing authority.

### `assets/`

`assets/` contains the required visible assets represented by the conversation.

## Source and content identity

### Source identity

`source_identity` identifies the public ChatGPT share publication. It uses a namespaced identity conceptually equivalent to:

```text
chatgpt-share:<share-id>
```

Different public shares remain distinct sources. An underlying ChatGPT conversation identifier, when reliably available, is optional provenance only and does not replace the share publication identity.

### Content identity

`content_identity` identifies one exact canonical visible-content revision. It is an algorithm-qualified SHA-256 identity computed from canonical semantics, not from final bundle serialization.

It changes when canonical visible conversation content or required asset contents change. It does not change because of filenames, paths, Markdown formatting, manifest formatting, ChatMD version, bundle format version, provenance, timestamps or other non-canonical metadata.

One bundle represents one immutable content revision snapshot. ChatMD does not own revision retention, replacement or history policy. Consumers decide whether older revisions are retained, replaced or archived.

## Canonical content

### Text

Canonical text is the decoded source string exactly as obtained from the structured source. ChatMD must not normalize Unicode, line endings, whitespace, blank lines or characters.

Canonical hashing uses deterministic UTF-8 encoding of that exact string.

### Conversation title

The exact reader-visible conversation title is canonical conversation-level content and participates in `content_identity`. A title-only change creates a new content revision.

A legitimately absent title remains absent and must not be synthesized. When present, the exact title is projected as the document title in `conversation.md`.

### Messages and parts

Canonical visible messages and their visible parts preserve source order and boundaries. Ordered messages and parts remain ordered in the identity model. Each canonical value uses an explicit typed object so different semantic kinds cannot collapse into the same identity representation.

## Canonical identity preimage

ChatMD must not hash `manifest.json` bytes.

The `content_identity` preimage is a separate deterministic canonical JSON value containing only identity-bearing semantics. It excludes provenance, filenames, paths, bundle format version, tool version and presentation fields.

The preimage includes the exact canonical conversation title when present, ordered canonical visible messages and parts, canonical citations and the content identity contribution of every required visible asset.

## Assets and supported content

Bundle format v1 supports text and evidence-backed visible image parts only.

Required image assets are stored exactly as downloaded. ChatMD must not resize, re-encode, strip metadata, convert formats or otherwise transform them. SHA-256 is calculated over the exact stored bytes.

Asset paths and filenames do not participate in `content_identity`. They remain deterministic bundle presentation details.

Unknown visible multimodal or attachment types fail visibly rather than being silently omitted.

## Citations

Only active structured references that are reader-visible in the public share interface are canonical citations. Marker-shaped text without an active reader-visible citation remains ordinary exact message text.

A canonical citation contains:

- a valid anchor;
- the exact marker substring;
- the exact destination URL.

When actually exposed by the public interface, canonical citation data may also contain:

- source title;
- attribution or domain;
- supporting snippet.

Absent optional values must not be synthesized.

Citation anchors use zero-based, half-open UTF-8 byte offsets into the exact message text. The marker must exactly match the referenced byte range.

The exact destination URL is preserved without redirect resolution, query cleanup, parameter sorting, fragment removal, percent-encoding normalization or other rewriting.

Invisible search, routing, extraction, diagnostic, indexing, icon and serialization internals are not canonical.

## Bundle completeness

A valid bundle is atomic and complete. Every required visible asset must be locally present and verified.

A missing, malformed, inaccessible or hash-mismatched required asset makes conversion fail. ChatMD must not publish a partial valid-looking bundle.

## Reproducibility

For the same `source_identity`, identical canonical conversation content and identical required asset bytes must produce byte-for-byte identical portable bundle output.

Run-specific timestamps, environment information, transient HTTP metadata and similar operational details remain outside the portable bundle.

## Compatibility

The bundle uses split compatibility rules:

- unknown identity-bearing canonical semantics fail visibly;
- unsupported major bundle format versions are rejected;
- unknown fields inside explicitly non-canonical provenance or extension areas may be ignored or preserved.

Changes to canonical semantics, canonicalization, required identity-bearing fields or identity computation require a new major bundle format version.

## Human-readable projection

`conversation.md` uses deterministic ChatMD-added message role headings and preserves source-authored message text exactly. It preserves message boundaries and projects local assets at their original content position.

For messages containing canonical citations, the source message remains unchanged and a deterministic ChatMD-generated Sources section is appended. Sources are ordered by citation anchor.

The projection is for durable human reading, not reverse parsing, and never becomes a second semantic authority.

## Content preservation invariant

ChatMD must not rewrite source-authored conversation content.

User and assistant content must be preserved as faithfully as the source representation allows. ChatMD may add structural metadata, integrity data and deterministic presentation structure, but must not summarize, paraphrase, clean up or otherwise alter source-authored message content.

## Determinism and portability

Equivalent supported source conversation data must produce equivalent bundle semantics and deterministic human-readable output.

The bundle must be usable without ChatMD, Context World or Obsidian being present. It must not depend on machine-local paths, consumer-specific state or a proprietary consumer database to remain interpretable.

## Ownership and consumers

ChatMD owns this interchange contract.

Context World, a possible future Obsidian plugin and other systems are consumers. They may build native ingestion or presentation around the bundle, but their internal models do not define the ChatMD contract and ChatMD must remain independently usable.

## Boundaries for later Work

The contract is resolved. Later Work still needs to choose implementation details that do not change its semantics, including:

- the exact manifest field layout and deterministic JSON serialization profile;
- the exact textual encoding of namespaced and algorithm-qualified identities;
- deterministic asset naming and directory layout beneath `assets/`;
- the exact deterministic Markdown formatting around the required projection behavior;
- HTTP acquisition, retry and download mechanics;
- packaging, installation or release mechanics;
- Context World or Obsidian integration behavior.

Those implementation choices require separate Work with concrete source and implementation evidence. They must preserve this contract's identity, content, completeness, compatibility, reproducibility, portability and ownership rules.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-D1`
- Kind: `document`
- Status: `active`
- Revision: `2`
- Authority: `local-native`
- Owner: [[Projects/CHAT-P1/CHAT-P1|CHAT-P1]]: chatmd

## Relations

_None._

## Backlinks

- **governed-by** <- [[Projects/CHAT-P1/Work/CHAT-3|CHAT-3]]: Extend canonical conversation model with title and citations
- **governed-by** <- [[Projects/CHAT-P1/Work/CHAT-4|CHAT-4]]: Ship the first complete end-user chatmd workflow
- **governed-by** <- [[Projects/CHAT-P1/Work/CHAT-5|CHAT-5]]: Make local ChatMD capture reliable
<!-- lwa:derived:end -->
