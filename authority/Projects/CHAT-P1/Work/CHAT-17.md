<!-- lwa:meta
{
  "id": "CHAT-17",
  "kind": "issue",
  "title": "Define a universal ChatMD capture invocation",
  "authority": "local-native",
  "revision": 1,
  "status": "active",
  "created_at": "2026-09-20T21:56:00Z",
  "updated_at": "2026-09-20T21:56:00Z",
  "owner": {
    "kind": "project",
    "id": "CHAT-P1"
  },
  "relations": [
    {
      "type": "related",
      "target": "CHAT-18"
    }
  ]
}
-->
# Define a universal ChatMD capture invocation

## Outcome

ChatMD should be invocable from useful contexts without the user first
asking whether the current entrypoint is supported.

The product direction is a universal capture interface:

```text
chatmd <input>
```

ChatMD classifies that input and routes it through one common ingestion
boundary. Source-specific reconstruction stays in source adapters. The
existing normalized conversation model, Markdown renderer, capture-root
writer, collision behavior, and success or failure reporting remain the
downstream pipeline.

This Work investigates the current invocation surface, defines the smallest
coherent capture-input boundary, and implements only the first-slice input
channels that investigation shows are routing, not new sources.

The user-visible value is that handing ChatMD a useful input becomes one
habit. CLI arguments, files, stdin, clipboard, URLs, and later OS
invocation surfaces should feed the same boundary instead of growing into
unrelated per-app integrations.

## Governing authority / source of truth

CHAT-P1 defines the product purpose, local-first boundary, no-rewrite
invariant, fail-visible behavior, Python-stdlib preference, and the current
primary interface `chatmd <share-url>`.

That Project contract currently bounds ChatMD to public ChatGPT shared
conversations. This Work must not silently rewrite CHAT-P1 into a generic
document-ingest product. If the first-slice invocation boundary requires a
smallest CHAT-P1 wording change so Project and Work stay consistent, that
change is in scope only as a consistency correction. It must preserve the
no-rewrite invariant, local-first boundary, fail-visible behavior, and
ChatGPT public share as the current implemented source.

CHAT-D1 remains the portable bundle contract. This Work does not implement
`manifest.json`, `assets/`, or content identity, and is not governed by
CHAT-D1.

Accepted CHAT-4 established the one-URL CLI and excluded stdin, clipboard,
GUI, and multiple-URL modes from the first workflow. Accepted CHAT-8 made
`chatmd` a normal installed command. Accepted CHAT-9 added zero-argument
macOS clipboard capture for one `https://chatgpt.com/share/...` URL and
kept clipboard resolution at the CLI and input boundary. Accepted CHAT-5,
CHAT-7, CHAT-10, and CHAT-13 own capture reliability, post-capture
security output, image preservation, and portable capture-root behavior.
This Work must reuse those contracts and must not reopen them except where
the new ingestion boundary has to sit in front of them.

The current `chatmd.py` and `test_chatmd.py` implementation are the
technical source of truth for invocation and capture. Repository
inspection before this Work found:

- `main()` accepts one optional positional `url` argument;
- an explicit argument is treated as a generic absolute HTTP(S) URL, then
  passed to ChatGPT share parsing;
- zero-argument `chatmd` reads macOS `pbpaste` and accepts only one
  `https://chatgpt.com/share/...` URL after surrounding whitespace is
  removed;
- there is no stdin path, no local-file path, no selected-text path, and
  no source-adapter layer;
- `parse_share()` and hydration decoding are ChatGPT-share-specific;
- the normalized `Conversation` model, `serialize_conversation()`,
  `write_markdown()`, image acquisition, capture root, and CHAT-7 success
  result are the current downstream pipeline.

CHAT-18 is related Work for a Codex source adapter. It is independently
deliverable. This Work must not implement Codex ingestion.

The repository implementation, tests, documented invocation, and
observable `chatmd` command result are the technical source of truth after
implementation. Human acceptance remains a separate authority decision.

## Affected systems

- `chatmd.py` CLI and input boundary in `main()` and its helpers;
- `test_chatmd.py` invocation, clipboard, and workflow tests;
- installed `chatmd` console-script entrypoint from `pyproject.toml`;
- `README.md` Quick start and invocation documentation;
- `chatmd --help` text;
- existing ChatGPT fetch, parse, normalize, serialize, image, write, and
  CHAT-7 success path, which this Work must reuse rather than duplicate.

`website/` and the public onepager are outside this Work unless a later
human decision authorizes a copy correction after the invocation contract
changes.

## Constraints

- Keep fetching, parsing, normalization, and serialization as separate
  boundaries.
- Prefer one common ingestion boundary over per-app or per-channel capture
  implementations.
- Explicitly separate capture-input channels from source adapters.
- Preserve the existing one-file, Python-stdlib runtime unless
  investigation proves a dependency is required.
- Do not use an LLM in the capture path.
- Do not scrape private or authenticated conversations.
- Do not introduce a watcher, daemon, GUI, menu bar application, Shortcut,
  or macOS Service in this Work.
- Failed classification, fetch, parse, or persistence must not print
  `CAPTURE COMPLETE` or the CHAT-7 shared-link security warning.
- Existing explicit `chatmd <chatgpt-share-url>` behavior remains the
  scriptable path and must not start reading the clipboard.
- Capture-root, collision, image preservation, and CHAT-D1 bundle
  semantics remain unchanged.

## Scope

Investigate the current invocation surface, define the capture-input
versus source-adapter split, and implement the smallest first slice that
makes `chatmd <input>` a real routing interface for currently supported
ChatGPT public shares.

### 1. Classify inputs

Treat these as candidates to classify, not as a list that must all be
implemented now:

- CLI arguments;
- local files;
- stdin;
- clipboard content;
- selected text;
- URLs;
- a future macOS Service, Shortcut, menu-bar action, or other global
  invocation mechanism.

Investigation must distinguish:

- input channels, which are how bytes or a path reach ChatMD;
- source identifiers, which name a capturable conversation source;
- source adapters, which reconstruct a normalized `Conversation`.

Default interpretation, unless investigation produces contrary evidence:

- CLI arguments, local files, stdin, clipboard, selected text, and later
  OS actions are channels or payloads into one boundary;
- a ChatGPT public share URL is a source identifier for the existing
  ChatGPT adapter;
- selected text is a payload that a later Service or Shortcut would feed
  through stdin, clipboard, or the same CLI boundary;
- arbitrary files, HTML dumps, or prose that are not a known source
  identifier are not a new conversation format in this Work.

### 2. Define one ingestion boundary

Define a single capture-input boundary in front of source adapters and the
existing pipeline. Conceptually:

```text
input channel
  -> classified capture input
  -> source adapter
  -> normalized Conversation
  -> existing Markdown rendering and local capture
```

Keep clipboard, file, stdin, and URL handling at that boundary. After a
supported ChatGPT share identifier is resolved, call the same existing
capture path used today. Do not duplicate fetch, parse, serialize, write,
collision, image, or success-output logic.

### 3. First-slice implementation

Implement only the channels that investigation shows can route to the
existing ChatGPT source without adding a new adapter:

- keep explicit CLI invocation working;
- keep or generalize zero-argument clipboard capture so clipboard content
  is classified by the common boundary rather than by a ChatGPT-only
  side path;
- add stdin and local-file routing when those channels can carry a
  supported source identifier without inventing a file-format adapter;
- detect URL-shaped input and route it to the matching source adapter,
  which in this Work remains the existing ChatGPT adapter.

If investigation shows that a candidate channel would require a new
source format rather than routing, classify it, fail clearly when that
input is offered, and leave the adapter to later Work.

### 4. Future invocation contract

Define the contract a later macOS Service, Shortcut, menu-bar action, or
global invocation mechanism would call. Do not implement those surfaces.

### 5. Documentation

Update `chatmd --help` and `README.md` so they describe the accepted
first-slice invocation honestly, including what is still unsupported.

## Non-goals

Do not:

- implement a macOS Service, Shortcut, menu bar, daemon, watcher, or GUI;
- implement a Codex source adapter, which is CHAT-18;
- implement additional source adapters beyond the existing ChatGPT public
  share path;
- turn ChatMD into a generic file, clipboard, or selected-text archiver;
- parse arbitrary documents, PDFs, HTML pages, or Markdown files as if
  they were conversations;
- search arbitrary prose for an embedded URL unless investigation proves
  that is required for a copied share link, which accepted CHAT-9
  rejected;
- add multiple-URL batch capture;
- change ChatGPT share parsing, image acquisition, Markdown serialization,
  capture-root behavior, collision behavior, or CHAT-D1 bundle semantics;
- change the CHAT-7 successful ChatGPT post-capture security result
  except where a non-ChatGPT source is rejected before that result;
- add third-party clipboard, HTTP, or parsing dependencies without
  concrete necessity;
- redesign packaging, installation, or distribution;
- update the public onepager;
- reopen CHAT-4, CHAT-8, or CHAT-9 as completed Work;
- use browser automation or ChatGPT authentication.

## Risks

- CHAT-P1 still describes a ChatGPT-share tool. Over-reading "arbitrary
  useful input" as generic content ingest would expand product scope
  without a Project decision.
- Putting source detection inside every channel would recreate per-app
  integrations under a new name.
- Broadening clipboard or stdin classification could weaken the accepted
  CHAT-9 contract that clipboard text is one URL, not prose to search.
- Local-file routing can confuse a path argument with a URL argument, or
  accidentally treat file bytes as a new source format.
- Stdin versus clipboard precedence can surprise users if both are
  present.
- Implementing OS services now would over-scope this Work and couple
  ChatMD to macOS application packaging it does not have.

## Implementation sequence

1. Inspect `main()`, clipboard helpers, argparse, tests, and README
   against accepted CHAT-8 and CHAT-9.
2. Classify each candidate input as channel, source identifier, source
   adapter, later OS surface, or out of scope.
3. Record the capture-input versus source-adapter split and the first
   slice that preserves the current architecture.
4. If a CHAT-P1 consistency correction is required, keep it to the
   smallest wording that admits `chatmd <input>` without claiming new
   sources.
5. Implement the common ingestion boundary in front of the existing
   ChatGPT capture path.
6. Route first-slice channels through that boundary. Keep explicit URL
   invocation independent of clipboard and stdin.
7. Make unrecognized, empty, ambiguous, or unsupported input fail clearly
   with no fetch, no write, and no successful capture result.
8. Update focused tests, `chatmd --help`, and README.
9. Reinstall or otherwise refresh the installed `chatmd` command before
   entrypoint verification, because CHAT-8 installs a non-editable copy.
10. Stop. Leave Codex ingestion to CHAT-18 and OS surfaces to later Work.

## Evidence requirements

- Investigation evidence states the capture-input versus source-adapter
  split and the first-slice decision for CLI arguments, files, stdin,
  clipboard, selected text, URLs, and future OS invocation.
- Focused tests prove explicit `chatmd <chatgpt-share-url>` still uses
  the existing capture path and does not read clipboard or stdin.
- Focused tests prove first-slice channels that this Work implements are
  classified before the existing ChatGPT pipeline and then share that
  pipeline.
- Tests prove unrecognized, empty, ambiguous, and unsupported input fail
  clearly with non-zero status, create no capture, and do not emit
  `CAPTURE COMPLETE`, `Saved:`, `Shared source:`, or the CHAT-7 security
  result.
- Clipboard tests remain isolated from the operator's live clipboard.
- File and stdin tests use privacy-safe fixtures and do not retain real
  share identifiers or conversation bodies.
- Existing relevant tests continue to pass, with stale missing-input
  assertions updated to the new contract rather than preserved as
  requirements.
- `chatmd --help` and README describe the accepted first slice and do
  not claim unimplemented OS integrations or Codex capture.
- The installed `chatmd` entrypoint is verified, not only direct
  `chatmd.py` execution.
- `python3 -m unittest -v` passes.
- `npx --yes pyright` passes.
- `uvx ruff check .` passes.
- `git diff --check` passes.
- The intended implementation diff contains no unrelated scope.

Do not retain public conversation bodies, share identifiers, credentials,
cookies, or signed URLs in tracked evidence.

## Acceptance criteria

- [ ] Investigation has classified CLI arguments, local files, stdin,
      clipboard, selected text, URLs, and future OS invocation as
      channel, source identifier, later surface, or out of scope.
- [ ] One common capture-input boundary is defined and implemented in
      front of source adapters and the existing ChatGPT capture pipeline.
- [ ] Capture-input channels are separate from source adapters in the
      resulting design and code.
- [ ] `chatmd https://chatgpt.com/share/...` continues to work through
      the existing explicit invocation path.
- [ ] Zero-argument clipboard capture continues to work for a copied
      ChatGPT share URL, or a documented successor through the common
      boundary preserves that daily workflow.
- [ ] First-slice file and stdin routing are implemented where
      investigation shows they carry a supported source identifier, or
      they fail clearly with the classification recorded in this Work.
- [ ] Unrecognized or unsupported input fails clearly, writes no capture,
      and does not emit a successful capture result.
- [ ] A later macOS Service, Shortcut, menu-bar action, or global
      invocation mechanism has a defined call contract and is not
      implemented.
- [ ] Codex ingestion is not implemented.
- [ ] ChatGPT parsing, image acquisition, Markdown serialization,
      capture-root, collision, and CHAT-D1 bundle semantics are
      unchanged.
- [ ] CHAT-7 successful ChatGPT post-capture security output remains
      unchanged for successful ChatGPT captures.
- [ ] `chatmd --help` and README match the accepted first-slice
      invocation.
- [ ] Existing relevant tests continue to pass, with focused tests added
      for the new boundary.
- [ ] The installed `chatmd` entrypoint is verified.
- [ ] `python3 -m unittest -v`, `npx --yes pyright`, `uvx ruff check .`,
      and `git diff --check` pass, with failures and limitations reported
      honestly.
- [ ] The intended implementation diff contains no unrelated scope.
- [ ] A human accepts the resulting invocation boundary against this
      Work contract.

## Completion boundary

CHAT-17 is complete when the capture-input versus source-adapter split is
recorded, one common ingestion boundary exists, the first-slice channels
that can route to the existing ChatGPT source do so through that
boundary, unsupported input fails clearly, future OS invocation is
defined but not built, Codex ingestion remains outside this Work, the
required verification passes, and a human accepts the result.

Do not mark this Work done, check human-accepted criteria, reconcile
authority, commit, or push unless a later human decision explicitly
authorizes that action.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-17`
- Kind: `issue`
- Status: `active`
- Revision: `1`
- Authority: `local-native`
- Owner: [[Projects/CHAT-P1/CHAT-P1|CHAT-P1]]: chatmd

## Owned Documents

_None._

## Relations

- **related** -> [[Projects/CHAT-P1/Work/CHAT-18|CHAT-18]]: Import Codex shared conversations

## Backlinks

- **related** <- [[Projects/CHAT-P1/Work/CHAT-18|CHAT-18]]: Import Codex shared conversations
<!-- lwa:derived:end -->
