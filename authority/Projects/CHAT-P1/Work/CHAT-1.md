<!-- lwa:meta
{
  "id": "CHAT-1",
  "kind": "issue",
  "title": "Prove lossless ChatGPT share parsing",
  "authority": "local-native",
  "revision": 2,
  "status": "done",
  "created_at": "2026-09-18T18:00:25Z",
  "updated_at": "2026-09-18T20:16:35Z",
  "owner": {
    "kind": "project",
    "id": "CHAT-P1"
  },
  "relations": []
}
-->
# Prove lossless ChatGPT share parsing

## Outcome

Determine whether current public ChatGPT share pages can be fetched with an ordinary HTTP request and reconstructed into correctly ordered conversation data without using browser automation or rendered DOM text as the primary source.

Produce enough concrete evidence to decide the smallest robust parser architecture for chatmd.

## Governing authority / source of truth

CHAT-P1 defines the product purpose, core invariant and initial success condition.

For this Work, observed responses from representative public ChatGPT share URLs are the technical source of truth for the current share format.

Existing third-party exporters may be inspected as implementation references, but they do not define chatmd behavior or authority.

## Scope

Use representative public ChatGPT share URLs to:

- fetch the share page using an ordinary HTTP client;
- identify the structured source from which the conversation can be reconstructed;
- determine how conversation ordering is represented;
- extract user and assistant message content;
- determine whether original Markdown, code blocks, links and whitespace can be preserved;
- identify rich or non-text content that cannot be represented losslessly as ordinary Markdown;
- capture representative normalized output or fixtures sufficient to prove the findings;
- document the smallest parser boundary supported by the evidence.

Keep fetching, parsing and representation concerns distinguishable during the investigation.

## Non-goals

Do not:

- build the final CLI;
- choose a programming language before parser requirements justify the choice;
- introduce browser automation;
- require ChatGPT authentication;
- scrape private conversations;
- use an LLM to transform conversation content;
- summarize or rewrite messages;
- design asset downloading;
- build a GUI, web app or macOS application;
- attempt broad compatibility with historical ChatGPT share formats unless current evidence requires it.

## Evidence requirements

The spike must use multiple representative public share conversations, including where available:

- ordinary prose;
- Markdown structure;
- fenced code;
- links or tables;
- rich or non-text ChatGPT content.

Evidence must establish:

- whether one ordinary HTTP request is sufficient;
- where the authoritative conversation data exists in the response;
- how message order and roles are recovered;
- whether message text can be preserved without DOM reconstruction;
- what content types are not losslessly representable;
- what assumptions the parser would depend on;
- how a format change can fail clearly instead of silently producing incomplete output.

Retain only evidence appropriate for the repository. Do not commit sensitive or unnecessarily public conversation content.

## Acceptance criteria

- [x] At least three representative public ChatGPT share URLs have been investigated.
- [x] Public share pages can be fetched without browser automation, or evidence demonstrates why that assumption is false.
- [x] The structured conversation source has been identified and documented.
- [x] User and assistant message ordering can be reconstructed from source data.
- [x] Representative textual content has been compared against the visible shared conversation.
- [x] Markdown and code preservation behavior has been established.
- [x] Rich or non-text content limitations have been identified.
- [x] Unsupported or ambiguous content has a proposed fail-visible behavior rather than silent loss.
- [x] A normalized fixture or equivalent machine-readable proof demonstrates the recovered conversation structure.
- [x] Fetching, parsing and serialization boundaries can be described independently.
- [x] The spike concludes with a recommendation for the smallest viable implementation architecture.
- [x] No final CLI implementation is introduced as part of this Work.
- [x] The intended investigation diff is reviewed.

## Completion boundary

CHAT-1 is complete when current public ChatGPT share behavior has been demonstrated from real source evidence, the feasibility and limits of lossless extraction are known, and there is enough evidence to make the next implementation Work decision without guessing.

Building the production parser, serializer, CLI, packaging, installation workflow and release process remain separate future Work.

## Investigation evidence

Repository evidence:

- `evidence/CHAT-1/findings.md`
- `evidence/CHAT-1/probe-summary.json`
- `tools/probe_share.py`

The investigation used three representative public shares covering ordinary prose, Markdown-rich content, and multimodal image content. Full downloaded HTML and full message bodies were intentionally not committed.

A visible public-share spot check matched the selected structured-source user and assistant pair, including paragraph structure, blockquote rendering, and bold rendering.

The representative multimodal evidence also established that public image assets can be resolved through a fresh anonymous cookie-aware HTTP session without account authentication. Asset downloading remains outside CHAT-1 implementation scope.

## Verification

Verified during CHAT-1:

- ordinary HTTP fetch succeeded for all three representative public shares without browser automation;
- `mapping` plus `current_node` reconstructed the active branch exactly against `linear_conversation` for all three fixtures;
- representative structured source preserved headings, lists, fenced code, tables, links, blockquotes, and blank-line whitespace;
- visibility projection rules excluded observed internal system, tool, reasoning, preamble, and explicitly hidden content;
- unknown visible content and unknown multimodal part types have documented fail-visible behavior;
- the machine-readable structural proof contains all three representative fixtures and no committed message bodies or conversation IDs;
- the intended investigation diff was reviewed and `git diff --check` passed before authority reconciliation.

<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-1`
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
