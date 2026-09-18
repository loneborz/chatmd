<!-- lwa:meta
{
  "id": "CHAT-2",
  "kind": "issue",
  "title": "Implement deterministic ChatGPT share parsing core",
  "authority": "local-native",
  "revision": 1,
  "status": "active",
  "created_at": "2026-09-18T20:56:48Z",
  "updated_at": "2026-09-18T20:56:48Z",
  "owner": {
    "kind": "project",
    "id": "CHAT-P1"
  },
  "relations": []
}
-->
# Implement deterministic ChatGPT share parsing core

## Outcome

Implement the production parsing core that converts a current public ChatGPT share URL into a deterministic normalized representation of the visible conversation.

The implementation must use the structured share data and parsing semantics established by CHAT-1 rather than rendered DOM extraction.

## Governing authority / source of truth

CHAT-P1 defines the product purpose and invariants.

CHAT-1 provides the investigation evidence for the current public ChatGPT share format, including:

- ordinary HTTP fetching;
- React Router hydration decoding;
- `serverResponse.data`;
- canonical conversation reconstruction from `mapping` plus `current_node`;
- visibility projection for visible user and assistant content;
- ordinary source-text preservation;
- observed `image_asset_pointer` multimodal content;
- fail-visible handling for unsupported visible content.

The current implementation and tests created by this Work become the repository source of truth for the production parsing core once accepted.

## Scope

Implement the smallest production-quality parsing core supported by CHAT-1 evidence.

Use Python and prefer the standard library unless a dependency is justified by concrete implementation requirements.

Keep distinct boundaries for:

- fetching a public share;
- decoding the hydration payload;
- locating structured share data;
- reconstructing the active conversation branch;
- projecting visible conversation content;
- normalizing supported message content into a deterministic internal representation.

Use `tools/probe_share.py` as investigation evidence and implementation reference, not as production code to be renamed wholesale.

The normalized representation must preserve:

- visible user and assistant role ordering;
- ordinary source text without rewriting;
- known visible multimodal image references as structured data;
- enough source type information for later serialization decisions.

## Non-goals

Do not:

- implement Markdown serialization;
- implement the final `chatmd <share-url>` CLI UX;
- download image assets;
- introduce browser automation;
- require ChatGPT authentication;
- support private conversations;
- add LLM transformation;
- attempt compatibility with historical ChatGPT share formats not established by current evidence;
- add packaging, installers, release automation, or distribution workflows;
- silently discard unsupported visible content.

## Evidence requirements

The implementation must be supported by tests that establish:

- current structured share payloads can be decoded through the production parser boundary;
- the active branch is reconstructed from `mapping` and `current_node`;
- ordering is deterministic;
- known internal, system, tool, reasoning, preamble, and explicitly hidden content is excluded according to the CHAT-1 findings;
- ordinary visible text is preserved without rewriting;
- known `image_asset_pointer` content is retained as structured multimodal data;
- unknown visible content or unknown visible multimodal part types fail clearly rather than disappearing;
- fetch, decode, graph reconstruction, visibility projection, and normalized representation remain independently testable;
- committed fixtures and tests do not contain unnecessary public conversation bodies, share IDs, credentials, cookies, signed URLs, or personal data.

Verification must include the repository's relevant automated tests and an intended-diff review.

## Acceptance criteria

- [ ] A production parser implementation exists outside `tools/probe_share.py`.
- [ ] Public-share HTTP fetching is isolated behind a clear boundary.
- [ ] React Router hydration data can be decoded into the structured share payload.
- [ ] `serverResponse.data` is located without rendered DOM scraping.
- [ ] The active branch is reconstructed from `mapping` plus `current_node`.
- [ ] Visible user and assistant ordering is deterministic.
- [ ] Ordinary source text is preserved without rewriting.
- [ ] Known visible `image_asset_pointer` parts are represented explicitly in the normalized model.
- [ ] Observed internal and hidden content is excluded according to the CHAT-1 visibility evidence.
- [ ] Unknown visible content fails clearly instead of being silently discarded.
- [ ] Fetching, decoding, reconstruction, visibility projection, and normalization are independently testable.
- [ ] Representative automated tests pass.
- [ ] Tests and fixtures do not introduce unnecessary sensitive or conversation-specific data.
- [ ] Markdown serialization, final CLI UX, asset downloading, and packaging remain outside this Work.
- [ ] The intended implementation diff is reviewed.

## Completion boundary

CHAT-2 is complete when a tested production parsing core can turn the current public ChatGPT share representation into a deterministic normalized visible conversation model using the semantics proven by CHAT-1.

Completion does not require Markdown output, the final CLI interface, asset downloading, installation, packaging, or release.

Those remain separate future Work.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-2`
- Kind: `issue`
- Status: `active`
- Revision: `1`
- Authority: `local-native`
- Owner: [[Projects/CHAT-P1/CHAT-P1|CHAT-P1]]: chatmd

## Owned Documents

_None._

## Relations

_None._

## Backlinks

_None._
<!-- lwa:derived:end -->
