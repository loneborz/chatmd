<!-- lwa:meta
{
  "id": "CHAT-7",
  "kind": "issue",
  "title": "Make post-capture shared-link exposure explicit",
  "authority": "local-native",
  "revision": 2,
  "status": "done",
  "created_at": "2026-09-19T15:45:00Z",
  "updated_at": "2026-09-19T16:04:59Z",
  "owner": {
    "kind": "project",
    "id": "CHAT-P1"
  },
  "relations": []
}
-->
# Make post-capture shared-link exposure explicit

## Outcome

Make the temporary public-share security boundary impossible to miss after a
successful ChatMD capture.

After ChatMD has successfully persisted the captured conversation, the CLI must
clearly tell the user:

- that capture completed;
- where the conversation was saved;
- which public ChatGPT share URL was used;
- that the shared link still exists;
- where the user can manually revoke shared links in ChatGPT.

The warning must appear only after successful persistence. A failed capture must
not present the security message as if capture completed.

## Governing authority / source of truth

CHAT-P1 defines the ChatMD product purpose, local-first boundary, and simple
one-URL capture interface.

Accepted CHAT-5 defines the reliable local capture workflow. Accepted CHAT-6
documents the currently accepted public product state.

The current `chatmd.py` and `test_chatmd.py` implementation are the technical
source of truth for the existing success and failure boundaries.

In the current implementation, `main()` calls `write_markdown(...)` before
printing the successful saved path. CHAT-7 preserves that ordering and extends
only the post-persistence user-facing result.

CHAT-D1 does not govern this Work because CHAT-7 does not change portable bundle
semantics, content identity, serialization, or the interchange contract.

## Scope

Change the successful CLI result so that, after persistence has completed, the
user sees a clear result conceptually equivalent to:

~~~text
CAPTURE COMPLETE

Saved:
/path/to/captured-conversation.md

Shared source:
https://chatgpt.com/share/...

SECURITY:
This shared link still exists.
Revoke it in ChatGPT > Settings > Data Controls > Shared Links.
~~~

The exact formatting may be adjusted where required for readable deterministic
CLI output, but the information and ordering above are required.

Update focused tests so they prove:

- successful capture emits the saved path and original shared source URL;
- successful capture emits the explicit shared-link security warning;
- the result is emitted only after `write_markdown(...)` succeeds;
- fetch, parse, validation, or persistence failure does not emit
  `CAPTURE COMPLETE`, `Shared source:`, or the post-capture security warning;
- existing collision behavior still reports the actual persisted path.

Update the README only where needed to keep the public description accurate
after this behavior is accepted.

## Non-goals

Do not:

- automatically revoke any ChatGPT shared link;
- discover or call undocumented OpenAI or ChatGPT APIs for link revocation;
- use browser cookies, browser automation, session extraction, or private
  authentication state;
- implement a bulk or `delete all shared links` operation;
- change the current public-share acquisition mechanism;
- eliminate the public-share step in this Work;
- change parsing, canonical conversation content, serialization semantics,
  capture-root behavior, collision behavior, or CHAT-D1 bundle semantics;
- add configuration, packaging, or unrelated usability work.

Reliable revocation of only the share used for one capture may be investigated
later as separate Work. If that requires fragile private API or browser-session
coupling, eliminating the share-link dependency is preferable to hiding that
fragility inside ChatMD.

## Evidence requirements

- Focused tests exercise the successful post-persistence CLI output.
- Focused tests prove failed capture paths do not emit a successful security
  result.
- Existing capture and workflow tests continue to pass.
- No network revocation, browser-session, cookie, or undocumented API behavior
  is introduced.
- The implementation diff remains bounded to the post-capture result,
  corresponding tests, and any minimal README synchronization required by the
  accepted behavior.
- `python3 -m unittest -v` passes.
- `npx --yes pyright` passes.
- `uvx ruff check .` passes.
- `git diff --check` passes.
- Local-native render and validate pass after authority reconciliation.

## Acceptance criteria

- [x] A successful capture clearly reports `CAPTURE COMPLETE`.
- [x] A successful capture reports the actual persisted file path.
- [x] A successful capture reports the public share URL used as its source.
- [x] A successful capture explicitly states that the shared link still exists.
- [x] The result tells the user to revoke it through
      `ChatGPT > Settings > Data Controls > Shared Links`.
- [x] The post-capture security result appears only after successful
      persistence.
- [x] Validation, fetch, parse, and persistence failures do not emit a
      successful post-capture security result.
- [x] Collision captures still report the actual newly persisted path.
- [x] No automatic revocation, undocumented OpenAI API integration,
      browser-cookie handling, browser automation, or bulk deletion is added.
- [x] Existing tests continue to pass.
- [x] `python3 -m unittest -v`, `npx --yes pyright`,
      `uvx ruff check .`, and `git diff --check` pass.
- [x] Local-native render and validate pass.
- [x] A human accepts the resulting behavior against this Work contract.

## Completion boundary

CHAT-7 is complete when a successful ChatMD capture makes the remaining public
shared-link exposure explicit and difficult to overlook, failure paths do not
misrepresent capture as complete, the required verification passes, and a human
accepts the behavior.

Do not mark this Work done, check human-accepted criteria, reconcile authority,
commit, or push unless a later human decision explicitly authorizes that action.

## Implementation evidence

The reviewed CHAT-7 product change is the tracked diff on
`ec0c9796bbee2321fe7751b0a2d220db9e1582fb`. It changes exactly:

- `chatmd.py`;
- `test_chatmd.py`;
- `README.md`.

`main()` still fetches, parses, serializes, and persists before printing.
After `write_markdown(...)` succeeds, the CLI prints `CAPTURE COMPLETE`, the
actual persisted path, the original shared source URL, that the shared link
still exists, and the manual revoke path
`ChatGPT > Settings > Data Controls > Shared Links`.

Validation, fetch, parse, and persistence failures do not emit that successful
post-capture result. Collision captures still preserve the existing file and
report the actual newly persisted path.

`README.md` was synchronized because the previous `Saved: <absolute-path>`
success-output description became stale after this behavior.

No automatic share revocation was implemented. No undocumented OpenAI or
ChatGPT API, browser cookies, browser automation, private session state, or
bulk shared-link deletion was introduced. Parsing, canonical conversation
content, serialization, capture-root behavior, collision behavior, and CHAT-D1
bundle semantics were not changed.

## Verification

Recorded LWA execution for run
`go-20260919T155231.665409000Z-66f91abab38eceac` finalized with disposition
`completed` by executor `cursor-grok-4.6-extra-high`. Starting and resulting
implementation HEAD before final commit remained
`ec0c9796bbee2321fe7751b0a2d220db9e1582fb`.

The recorded quality gate results were:

- `python3 -m unittest -v` - exit 0 at `2026-09-19T16:00:58Z`;
- `npx --yes pyright` - exit 0 at `2026-09-19T16:00:58Z`;
- `uvx ruff check .` - exit 0 at `2026-09-19T16:00:59Z`;
- `git diff --check` - exit 0 at `2026-09-19T16:00:59Z`.

Focused workflow tests prove the successful post-persistence CLI result and
that validation, fetch, parse, and persistence failures do not emit
`CAPTURE COMPLETE`, `Shared source:`, or the post-capture security warning.
Collision captures report the actual newly persisted path. Existing capture and
workflow tests continued to pass (42 tests).

After authority reconciliation:

- `local-native render` wrote the authority tree from current LWA source;
- `local-native validate` reported the ChatMD authority root valid
  (1 project, 7 issues, 1 document, 9 objects).

No retained run bundle was added because CHAT-7 does not require durable
retained evidence.

## Human acceptance

Accepted at `2026-09-19T16:04:59Z` as complete for the CHAT-7 boundary.

The human operator reviewed the implementation diff and the finalized LWA
execution evidence and explicitly authorized CHAT-7 acceptance and end-to-end
finalization.

## Disposition

`CHAT-7` is completed.

A successful ChatMD capture now makes the remaining public shared-link
exposure explicit after persistence. Failure paths do not present capture as
complete. Automatic revocation, undocumented OpenAI or ChatGPT APIs, browser
cookies, browser automation, session extraction, bulk deletion, and CHAT-D1
bundle work remain outside this Work.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-7`
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
