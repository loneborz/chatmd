<!-- lwa:meta
{
  "id": "CHAT-7",
  "kind": "issue",
  "title": "Make post-capture shared-link exposure explicit",
  "authority": "local-native",
  "revision": 1,
  "status": "active",
  "created_at": "2026-09-19T15:45:00Z",
  "updated_at": "2026-09-19T15:45:00Z",
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

- [ ] A successful capture clearly reports `CAPTURE COMPLETE`.
- [ ] A successful capture reports the actual persisted file path.
- [ ] A successful capture reports the public share URL used as its source.
- [ ] A successful capture explicitly states that the shared link still exists.
- [ ] The result tells the user to revoke it through
      `ChatGPT > Settings > Data Controls > Shared Links`.
- [ ] The post-capture security result appears only after successful
      persistence.
- [ ] Validation, fetch, parse, and persistence failures do not emit a
      successful post-capture security result.
- [ ] Collision captures still report the actual newly persisted path.
- [ ] No automatic revocation, undocumented OpenAI API integration,
      browser-cookie handling, browser automation, or bulk deletion is added.
- [ ] Existing tests continue to pass.
- [ ] `python3 -m unittest -v`, `npx --yes pyright`,
      `uvx ruff check .`, and `git diff --check` pass.
- [ ] Local-native render and validate pass.
- [ ] A human accepts the resulting behavior against this Work contract.

## Completion boundary

CHAT-7 is complete when a successful ChatMD capture makes the remaining public
shared-link exposure explicit and difficult to overlook, failure paths do not
misrepresent capture as complete, the required verification passes, and a human
accepts the behavior.

Do not mark this Work done, check human-accepted criteria, reconcile authority,
commit, or push unless a later human decision explicitly authorizes that action.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-7`
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
