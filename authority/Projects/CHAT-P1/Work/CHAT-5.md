<!-- lwa:meta
{
  "id": "CHAT-5",
  "kind": "issue",
  "title": "Make local ChatMD capture reliable",
  "authority": "local-native",
  "revision": 2,
  "status": "done",
  "created_at": "2026-09-19T14:17:46Z",
  "updated_at": "2026-09-19T15:19:54Z",
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
# Make local ChatMD capture reliable

## Outcome

ChatMD reliably captures one public shared ChatGPT conversation as one durable
local Markdown source file owned by the user.

ChatMD acts only as the boundary between a transient ChatGPT shared
conversation and a durable local source. It must not interpret or transform
the conversation into knowledge.

## Governing authority / source of truth

CHAT-P1 defines the product purpose, local-first boundary and no-rewrite
invariant. CHAT-D1 governs source-faithful canonical conversation semantics.
CHAT-1 through CHAT-4 provide the accepted parser, normalized model,
serializer, CLI and test architecture that this Work must reuse where
adequate.

The actual local Obsidian vault destination is:

`/Users/marwan/My vault/Sources/ChatMD`

The repository implementation, tests and observable command result are the
technical source of truth after implementation. Human acceptance remains a
separate authority decision.

## Scope

- Store successful captures under
  `/Users/marwan/My vault/Sources/ChatMD/YYYY/MM/`, using the local capture
  date for `YYYY` and `MM`.
- Create missing year and month directories when needed.
- Preserve the existing source-faithful Markdown representation, title
  behavior and filesystem-safe filename behavior where they are sound.
- Make a capture successful only after a complete, valid, non-empty Markdown
  export has been safely persisted at its final path.
- Never silently truncate, replace or overwrite an existing capture. On a
  filename collision, preserve the existing file, create a deterministic
  collision-safe filename such as `conversation-2.md`, and report the actual
  resulting path.
- Ensure failed fetch, parse, conversion, validation or filesystem operations
  do not publish a successful-looking final Markdown file and return a
  non-zero CLI result with an actionable error.
- Reject whitespace-only, empty-shell or otherwise contentless conversation
  exports while preserving legitimate existing non-empty exports.
- Report the exact absolute final path after persistence with the form
  `Saved: <absolute-path>`.
- Keep the existing one-public-URL CLI invocation model and do not make shell
  quoting part of ChatMD syntax.
- Use the existing parser, normalized model, serializer and test architecture
  without introducing a generalized storage configuration system.

## Non-goals

Do not implement or introduce:

- conversation interpretation, summarization, rewriting, conclusions or
  knowledge extraction;
- generated tags, classification, embeddings, RAG, LLM processing or automatic
  promotion into Knowledge;
- Context World indexing, search, cross-linking or Obsidian plugin integration;
- generalized storage configuration, cloud synchronization or a major CLI
  redesign;
- a new parser, normalized conversation model, Markdown representation or
  unrelated refactoring;
- packaging, installation, distribution, release automation or deployment.

## Evidence requirements

Automated tests must use temporary or isolated directories and establish:

- the successful default destination contract and `YYYY/MM` routing;
- creation of missing destination directories;
- expected safe filename behavior;
- deterministic collision handling and preservation of the existing file;
- rejection of empty or contentless exports;
- visible fetch, parse or conversion failure behavior;
- no successful-looking final file after any failed export or persistence
  operation;
- exact absolute path reporting on success, including after a collision;
- preservation of the existing source-faithful Markdown output and regression
  of existing ChatMD behavior.

Run the repository quality gate:

- `python3 -m unittest -v`;
- `pyright` or the repository's established equivalent;
- `ruff check .` or the repository's established equivalent;
- `git diff --check`;
- local-native authority validation and any applicable LWA execution evidence.

If the environment safely permits it, perform one end-to-end capture from a
representative public shared ChatGPT URL and retain only the evidence needed
to inspect the resulting local file. Do not retain the public conversation
body, share identifier, credential, cookie or signed URL in tracked evidence.

## Acceptance criteria

- [x] One public shared ChatGPT URL creates one durable Markdown source file
      under `/Users/marwan/My vault/Sources/ChatMD/YYYY/MM/`.
- [x] The year and month directories are derived from the local capture date
      and are created when missing.
- [x] The final filename remains filesystem-safe and preserves the established
      title and slug behavior where sound.
- [x] A collision never overwrites the existing file and produces a
      deterministic new filename while reporting the actual path.
- [x] Empty, whitespace-only, shell-only and other contentless exports are
      rejected without a successful-looking final file.
- [x] Fetch, parse, conversion, validation and filesystem failures return a
      non-zero result, emit an actionable error and do not publish a partial
      final capture.
- [x] The success message is emitted only after persistence and contains the
      exact absolute final path.
- [x] The exported Markdown remains source-faithful and does not add
      interpretation, rewriting, knowledge promotion or consumer integration.
- [x] The existing one-URL CLI model and current ChatMD behavior remain
      working.
- [x] The focused tests, complete test suite, applicable lint/type checks and
      `git diff --check` pass, with failures and limitations reported honestly.
- [x] One real end-to-end capture is performed when safely possible; the
      resulting file is inspected for non-empty valid Markdown and expected
      conversation content without treating file existence as proof of
      completeness.

## Completion boundary

CHAT-5 is complete only after the implementation evidence and verification
show that one real public shared ChatGPT URL can produce one complete,
source-faithful Markdown capture at the exact local vault destination without
overwriting an existing capture or publishing a failed export.

Human acceptance is required at this boundary: the human operator must open
the exact resulting file and confirm that the captured conversation is
complete and acceptable. Execution finalization, evidence retention, code
existence, test success and Git state do not substitute for that decision.

Do not mark this Work done, check acceptance criteria as human-accepted,
reconcile authority, commit, push, merge or deploy as part of this Work unless
the required later human decision explicitly authorizes that action.

## Implementation evidence

The accepted product implementation is committed as:

`fb4cf19150140ac445dcb634bc071b7003557aa0`

It changes exactly:

- `chatmd.py`;
- `test_chatmd.py`.

The implementation reuses the existing parser, normalized conversation model,
serializer, CLI, and atomic temp-file plus `os.link` publication. Successful
captures are stored under `/Users/marwan/My vault/Sources/ChatMD/YYYY/MM/`
using the local capture date, create missing year and month directories,
reject contentless exports, preserve existing files on collision with a
deterministic `name-2.md` suffix, and print `Saved: <absolute-path>` only
after persistence. No generalized storage configuration, knowledge
processing, or Markdown redesign was added.

## Verification

Recorded LWA execution for run
`go-20260919T144213.524970000Z-924eae123c72fbb8` finalized with disposition
`completed`. The quality gate results were:

- `python3 -m unittest -v test_chatmd.WorkflowTests` - passed;
- `python3 -m unittest -v` - 41 tests passed;
- `npx --yes pyright` - passed;
- `uvx ruff check .` - first attempt failed with `DTZ011` on naive
  `date.today()`; after switching the capture date to a timezone-aware local
  date, the same command passed;
- `python3 -m unittest -v` and `npx --yes pyright` were recorded again after
  that fix and passed;
- `git diff --check` - passed;
- `local-native validate` of the ChatMD authority root - passed.

Automated filesystem tests used temporary capture roots and did not write
fixtures into `/Users/marwan/My vault/Sources/ChatMD`.

The accepted live capture created:

`/Users/marwan/My vault/Sources/ChatMD/2026/09/Betrouwbare lokale capture-tool.md`

The human opened that file and confirmed a complete, source-faithful capture
for the current exporter contract. No public share URL or conversation body
is retained in tracked authority, tests, or execution evidence.

## Human acceptance

Accepted at `2026-09-19T15:19:54Z` as complete for the CHAT-5 boundary.

The implementation, recorded quality gate, and live vault capture are
accepted. Existing unresolved-image placeholder behavior
`[Image in original conversation]` is accepted for this Work and remains
outside CHAT-5 scope.

## Disposition

`CHAT-5` is completed.

Reliable local capture to the authorized vault `YYYY/MM` destination, collision
preservation, contentless-export rejection, exact `Saved:` path reporting, and
source-faithful one-URL CLI behavior satisfy the completion boundary.
Deployment, packaging, distribution, release automation, image downloading,
and the CHAT-D1 portable bundle contract remain outside this Work.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-5`
- Kind: `issue`
- Status: `done`
- Revision: `2`
- Authority: `local-native`
- Owner: [[Projects/CHAT-P1/CHAT-P1|CHAT-P1]]: chatmd

## Owned Documents

_None._

## Relations

- **governed-by** -> [[Projects/CHAT-P1/Documents/CHAT-D1|CHAT-D1]]: Portable Conversation Bundle Contract

## Backlinks

_None._
<!-- lwa:derived:end -->
