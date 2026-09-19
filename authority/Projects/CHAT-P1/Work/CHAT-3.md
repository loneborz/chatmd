<!-- lwa:meta
{
  "id": "CHAT-3",
  "kind": "issue",
  "title": "Extend canonical conversation model with title and citations",
  "authority": "local-native",
  "revision": 1,
  "status": "active",
  "created_at": "2026-09-19T00:02:32Z",
  "updated_at": "2026-09-19T00:02:32Z",
  "owner": {
    "kind": "project",
    "id": "CHAT-P1"
  },
  "relations": [
    {
      "type": "governed-by",
      "target": "CHAT-D1"
    }
  ]
}
-->
# Extend canonical conversation model with title and citations

## Outcome

Extend the production parser and normalized conversation model so later bundle Work can use all already-resolved canonical conversation semantics from the public share payload: the exact reader-visible conversation title, including legitimate absence, and active reader-visible structured citations associated with their visible messages.

Keep the parser boundary small and preserve current supported text and image behavior.

## Governing authority / source of truth

CHAT-P1 defines the product purpose, content-preservation invariant and product boundary.

CHAT-D1 directly governs this Work and defines the canonical semantics for conversation titles, messages, parts and citations. Its resolved semantic contract is authoritative; implementation details it intentionally leaves open remain outside this Work unless required for this bounded parser and model slice.

CHAT-1 provides the current public-share format evidence. The accepted `chatmd.py` and `test_chatmd.py` implementation from CHAT-2 are the repository source of truth for the current production parser, normalized model and test structure.

Current structured public-share evidence must establish any source-native title and citation fields, visibility signals and offset units used by the implementation. Do not infer payload fields from marker text or invent unsupported source behavior.

## Scope

- Preserve the exact reader-visible conversation title when present.
- Represent legitimate title absence explicitly without synthesizing a title.
- Make the title available at the normalized `Conversation` boundary.
- Represent each active reader-visible structured citation as canonical structured data associated with the relevant visible message.
- Preserve each citation's zero-based, half-open UTF-8 byte anchor offsets, exact marker substring and exact absolute destination URL.
- Preserve an optional source title, attribution or domain, and supporting snippet only when each value is supplied as reader-visible source data.
- Preserve exact source message text unchanged, including inline citation markers.
- Convert source-native citation offsets to canonical UTF-8 byte offsets when necessary and verify the conversion before exposing them.
- Require the exact marker substring to match the anchored byte range in the exact message text.
- Treat marker-shaped strings without an active reader-visible structured reference as ordinary text only.
- Exclude non-canonical ChatGPT citation internals, including search-result indices, cited-message indices, extraction diagnostics, routing information, internal format labels, icons, favicons, serialization metadata and other invisible implementation details.
- Fail visibly when an active reader-visible citation lacks a valid anchor, exact marker substring or exact absolute destination URL, or otherwise cannot be represented by the CHAT-D1 contract.
- Keep current supported text and image behavior intact, including fail-visible handling for unsupported visible content.

## Non-goals

Do not implement:

- `manifest.json` serialization;
- `content_identity` computation;
- canonical JSON hashing;
- Markdown serialization;
- Sources-section rendering;
- image downloading;
- image hashing;
- deterministic asset naming;
- bundle directory creation;
- atomic bundle publication;
- CLI UX;
- packaging or release work;
- Context World integration;
- Obsidian integration;
- generic support for audio, video, documents, attachments or hypothetical future citation formats.

Do not decide the manifest field layout, deterministic JSON serialization profile, identity encoding, bundle format version, Markdown formatting or other later bundle implementation details that CHAT-D1 intentionally leaves open.

## Evidence requirements

Use current public-share source evidence to establish the exact source locations, field meanings, reader-visible activation or visibility signals, and source-native offset units used for titles and citations before encoding them in the production parser. Retain only privacy-safe structural evidence appropriate for the repository.

Automated tests must establish:

- exact title preservation when present;
- explicit absent-title behavior without synthesis;
- active reader-visible citation extraction into the normalized model and association with the relevant visible message;
- exact message text preservation with inline citation markers untouched;
- correct zero-based, half-open UTF-8 byte offsets, including a non-ASCII case where character indexing and UTF-8 byte indexing differ;
- distinct anchors for repeated identical marker text at different locations;
- ordinary text behavior for marker-shaped text without an active structured citation;
- preservation of optional citation fields only when supplied as reader-visible values;
- visible failure when a mandatory active-citation field is absent or malformed;
- visible failure when the marker does not exactly match its anchored byte range;
- preservation of current supported text and image behavior and continued passage of existing parser tests;
- fail-visible behavior for unsupported visible content so no unsupported visible content is silently discarded.

Verification must include the repository's relevant automated tests, `git diff --check`, local-native validation and review of the complete intended implementation and authority diff.

## Acceptance criteria

- [ ] The normalized `Conversation` model exposes the exact reader-visible title or an explicit absent value without synthesis.
- [ ] Active reader-visible citations are represented as structured canonical data on the relevant visible message.
- [ ] Each citation preserves a valid zero-based, half-open UTF-8 byte anchor, exact marker substring and exact absolute destination URL.
- [ ] Reader-visible optional source title, attribution or domain, and supporting snippet are preserved only when supplied.
- [ ] Exact source message text remains unchanged, including inline citation markers.
- [ ] Source-native offsets are converted and verified before canonical UTF-8 byte offsets are exposed.
- [ ] Marker and anchor mismatches fail visibly.
- [ ] Active citations missing mandatory canonical fields fail visibly.
- [ ] Repeated identical markers remain distinguishable by anchor.
- [ ] Marker-shaped text without an active reader-visible structured reference remains ordinary text.
- [ ] Non-canonical citation internals are excluded from the normalized canonical model.
- [ ] Existing supported text and image behavior remains intact.
- [ ] Unsupported visible content is not silently discarded.
- [ ] Representative automated tests, including the existing parser tests, pass.
- [ ] The complete intended implementation and authority diff is reviewed and remains within this Work.
- [ ] Serialization, hashing, asset handling, bundle publication, CLI, packaging, release and consumer-integration scope is not introduced.

## Completion boundary

CHAT-3 is complete when the tested production parser and normalized model expose the exact reader-visible conversation title and all active reader-visible citations that can be represented under CHAT-D1, with validated canonical UTF-8 byte anchors and unchanged source message text, while preserving current supported text and image behavior and failing visibly on malformed or unsupported visible citation content.

Completion does not require serialization, identity computation, hashing, Markdown or Sources-section rendering, asset handling, bundle creation or publication, CLI UX, packaging, release work, Context World or Obsidian integration, or support for additional content and hypothetical citation formats. Those remain separate future Work.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-3`
- Kind: `issue`
- Status: `active`
- Revision: `1`
- Authority: `local-native`
- Owner: [[Projects/CHAT-P1/CHAT-P1|CHAT-P1]]: chatmd

## Owned Documents

_None._

## Relations

- **governed-by** -> [[Projects/CHAT-P1/Documents/CHAT-D1|CHAT-D1]]: Portable Conversation Bundle Contract

## Backlinks

_None._
<!-- lwa:derived:end -->
