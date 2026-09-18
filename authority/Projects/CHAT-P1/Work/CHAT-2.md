<!-- lwa:meta
{
  "id": "CHAT-2",
  "kind": "issue",
  "title": "Implement deterministic ChatGPT share parsing core",
  "authority": "local-native",
  "revision": 2,
  "status": "done",
  "created_at": "2026-09-18T20:56:48Z",
  "updated_at": "2026-09-18T21:58:04Z",
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

- [x] A production parser implementation exists outside `tools/probe_share.py`.
- [x] Public-share HTTP fetching is isolated behind a clear boundary.
- [x] React Router hydration data can be decoded into the structured share payload.
- [x] `serverResponse.data` is located without rendered DOM scraping.
- [x] The active branch is reconstructed from `mapping` plus `current_node`.
- [x] Visible user and assistant ordering is deterministic.
- [x] Ordinary source text is preserved without rewriting.
- [x] Known visible `image_asset_pointer` parts are represented explicitly in the normalized model.
- [x] Observed internal and hidden content is excluded according to the CHAT-1 visibility evidence.
- [x] Unknown visible content fails clearly instead of being silently discarded.
- [x] Fetching, decoding, reconstruction, visibility projection, and normalization are independently testable.
- [x] Representative automated tests pass.
- [x] Tests and fixtures do not introduce unnecessary sensitive or conversation-specific data.
- [x] Markdown serialization, final CLI UX, asset downloading, and packaging remain outside this Work.
- [x] The intended implementation diff is reviewed.

## Implementation evidence

Accepted implementation consists of:

- `chatmd.py`, containing the production parsing core with isolated fetch, hydration decoding, structured share-data lookup, active-branch reconstruction, visibility projection, and deterministic normalization.
- `test_chatmd.py`, containing privacy-safe synthetic coverage for supported content, visibility exclusions, graph invariants, malformed-source handling, and fail-visible unsupported content.
- LWA execution run `go-20260918T210011.129471000Z-02ff1daf34cfb853` was finalized with disposition `completed` and retained locally.

The implementation remained within CHAT-2 scope. Markdown serialization, final CLI UX, asset downloading, packaging, installation, and release work were not added.

## Verification and acceptance

Human review accepts the CHAT-2 result with execution disposition `completed`.

Verification evidence:

- The final repository test suite contains 14 tests and passed through the LWA verification recorder.
- The final parser was reviewed after the root-format correction.
- All three representative CHAT-1 public shares parsed successfully through the production `chatmd.parse_share()` boundary.
- The plain representative produced 88 visible messages.
- The Markdown representative produced 80 visible messages.
- The rich representative produced 115 visible messages and preserved visible image parts structurally.
- The intended implementation diff was reviewed and remained limited to the parser core, tests, and retained execution evidence.
- No dependency, serializer, CLI, asset-download, packaging, installation, or release scope was introduced.
- LWA execution evidence records frozen Work revision 1, finalized execution disposition `completed`, successful verification attempts, and `chatmd.py` plus `test_chatmd.py` as the product changed files. The retained bundle is intentionally excluded from public Git because it contains machine-local absolute paths.

## Completion boundary

CHAT-2 is complete when a tested production parsing core can turn the current public ChatGPT share representation into a deterministic normalized visible conversation model using the semantics proven by CHAT-1.

Completion does not require Markdown output, the final CLI interface, asset downloading, installation, packaging, or release.

Those remain separate future Work.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-2`
- Kind: `issue`
- Status: `done`
- Revision: `2`
- Authority: `local-native`
- Owner: [[Projects/CHAT-P1/CHAT-P1|CHAT-P1]]: chatmd

## Owned Documents

_None._

## Relations

_None._

## Backlinks

_None._
<!-- lwa:derived:end -->
