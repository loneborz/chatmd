<!-- lwa:meta
{
  "id": "CHAT-11",
  "kind": "issue",
  "title": "Reframe the ChatMD onepager around local conversation capture",
  "authority": "local-native",
  "revision": 2,
  "status": "done",
  "created_at": "2026-09-20T10:39:03Z",
  "updated_at": "2026-09-20T11:28:23Z",
  "owner": {
    "kind": "project",
    "id": "CHAT-P1"
  },
  "relations": []
}
-->
# Reframe the ChatMD onepager around local conversation capture

## Outcome

Authorize a strictly textual positioning refinement of the implemented
ChatMD onepager so it leads with the value of turning a user's valuable
ChatGPT conversation into a deterministic local Markdown file that they
control.

ChatMD remains technically a public ChatGPT share capture tool. This Work
does not change product behavior. It changes what the public onepager
presents as the primary user problem.

The onepager must no longer present preservation of a disappearing public
webpage as the primary user problem. The required capture path remains:

```text
ChatGPT conversation
  -> create public share
  -> copy share URL
  -> ChatMD captures the visible shared conversation
  -> local Markdown
  -> optionally revoke the public share
```

The public share is required by the current implementation. It is the
capture boundary and transport mechanism. It is not the primary product
value.

Revision 2 is a human owner scope correction. This Work is strictly
textual content only. It does not authorize image regeneration, asset
changes, CSS changes, visual modifications, or markup restructuring.

## Governing authority / source of truth

CHAT-P1 defines the product purpose, local-first boundary, no-rewrite
invariant, and the one-URL public-share interface. This Work does not
change that Project contract. ChatMD still converts a public ChatGPT
shared conversation into local Markdown.

The current `chatmd.py` and `test_chatmd.py` implementation are the
technical source of truth for what ChatMD actually does. Accepted CHAT-1
through CHAT-10 remain the accepted capture, CLI, clipboard, image, and
security contracts. This Work does not reopen them.

The implemented onepager surface is `website/index.html`. There is no
template. `website/styles.css` and the surrounding `website/` assets
remain the visual source of truth established by the human-approved
prototype and later production hardening. This Work may change textual
content inside `website/index.html` only. It does not authorize changes
to that visual system.

This is the first CHAT-P1 Work that authorizes onepager copy. It does not
authorize onepager assets.

Accepted CHAT-6 owns the public GitHub README as a separate landing page.
This Work does not change `README.md`.

Accepted CHAT-5 defines reliable local capture and still describes ChatMD
as the boundary between a transient ChatGPT shared conversation and a
durable local source. This Work does not reopen that capture contract. It
authorizes the onepager to stop using webpage transience as the primary
user problem, while remaining honest that a public share URL is required.

Accepted CHAT-7 defines the post-capture shared-link security result. The
onepager terminal demo already shows that result. This Work preserves that
demo unchanged. Revocation remains an important post-capture security
step and is not the product's primary reason for existing.

Accepted CHAT-9 already documents the daily workflow as Share, copy link,
then `chatmd`. This Work uses that same required path.

CHAT-D1 remains the unresolved portable bundle contract. It must not be
described as implemented. CHAT-D1 `source_identity` identifies the public
share publication, not an independent ChatGPT conversation. This Work
does not implement CHAT-D1 and must not claim that ChatMD captures a
conversation independently of its share publication.

CHAT-1 investigated whether current public shares can be reconstructed
from structured share data. Its title uses "lossless" as an investigation
label. It is not a public product guarantee. Do not import that word into
onepager copy.

After implementation, `website/index.html` is the source of truth for the
onepager copy authorized by this Work. `website/og.png` is not in scope
and may continue to show the previous positioning. The repository
implementation and accepted Work remain the source of truth for product
behavior. Human acceptance remains a separate authority decision.

## Product decision

Keep these facts separate:

- Technical product: ChatMD fetches one public ChatGPT share and writes
  deterministic local Markdown of the visible shared conversation.
- Primary onepager value: the user gets a local Markdown file of a
  conversation they care about, under their control.
- Share role: required escape path from the ChatGPT interface, not the
  object the user is trying to own.
- Revocation role: important security hygiene after capture, not the
  origin story of the product.

Safe semantic framing for onepager copy:

- the user has a valuable conversation;
- Share provides the current escape path from the ChatGPT interface;
- ChatMD captures the conversation as exposed by that share;
- the resulting artifact is deterministic local Markdown under the user's
  control;
- revocation remains an important post-capture security step, but is not
  the product's primary reason for existing.

## Forbidden claims

The onepager must not claim or imply that:

- ChatMD reads or exports ChatGPT history;
- ChatMD captures private conversations directly;
- creating a share is optional;
- old conversations cease to exist when they leave recent history;
- capture is lossless or "zero loss";
- the resulting file is immutable;
- the resulting file is literally permanent;
- ChatMD captures a conversation independently of its share publication;
- ChatMD authenticates into ChatGPT;
- ChatMD preserves original uploaded image bytes;
- ChatMD downloads file attachments;
- ChatMD automatically revokes public shares;
- ChatMD summarizes conversations or creates knowledge;
- CHAT-D1 is implemented.

Do not replace share-takedown language with a claim that ChatGPT
conversations disappear merely because they leave recent history. If
takedown, expiry, or revocation is mentioned, it must refer to the public
share URL, not to the user's private ChatGPT thread.

Deterministic capture means the same supported share data produces the
same Markdown. It does not mean zero loss, immutability, or permanence.
Existing files are never silently overwritten. That is not a claim that
the file cannot later be edited or deleted.

## Authorized implementation surface

This authorization refinement lives in
`authority/Projects/CHAT-P1/Work/CHAT-11.md`.

Later implementation may change textual content in `website/index.html`
only.

No other file is authorized.

## Scope

This Work is strictly textual content only.

Change text inside the implemented onepager so metadata, hero, Section
01, the T0-T3 progression, navigation terminology, and footer framing
tell one story.

In `website/index.html`, this Work may change only textual content and
textual metadata values:

- document title and description;
- Open Graph and Twitter title, description, and image alt text inside
  `<head>`;
- hero headline and lead;
- Section 01 index label, heading, and lead;
- T0-T3 titles and body copy;
- the nav label currently named `Transience`, if it would otherwise
  contradict Section 01;
- footer framing, if it would otherwise contradict the new lead.

Do not restructure markup. Replace text inside existing elements and
textual attribute values. Do not add, remove, or reorder sections,
wrappers, class names, or interactive elements.

The hero terminal demo must remain unchanged, including the capture
command, `CAPTURE COMPLETE` result, saved-path example, shared-source
line, security warning, and copy-button payload.

Hero facts that already state the input is one public share URL should
remain, or be kept equally unambiguous, so the required share path cannot
become implicit.

`website/og.png` is out of scope. Do not regenerate it. Do not change any
image, font, favicon, or other `website/` asset. If `website/og.png`
still visually contains the previous positioning after this Work, that
is a known follow-up inconsistency and not a defect this Work may fix.

Preserve the existing visual, accessibility, interaction, typography,
responsive, and security-warning constraints already encoded in
`website/index.html` and `website/styles.css`, including:

- near-black document surfaces, hairline structure, and self-hosted Inter
  and IBM Plex Mono;
- amber reserved for the live-share warning;
- skip link, `:focus-visible` treatment, and copy-button status text;
- no-JS readable content and `prefers-reduced-motion` behavior;
- current desktop, tablet, and mobile layout breakpoints;
- no framework, analytics, tracking, or build step.

## Non-goals

Do not:

- regenerate or modify `website/og.png`;
- change any image, font, favicon, or other asset;
- change `website/styles.css` or any visual treatment;
- restructure markup;
- redesign the page;
- change the terminal demo;
- change ChatMD product behavior;
- modify `chatmd.py`;
- modify tests;
- implement CHAT-D1;
- modify `README.md`;
- reopen CHAT-5, CHAT-6, CHAT-7, or CHAT-9;
- change Project, Document, or prior Work contracts beyond the
  navigation generated by render;
- invent capabilities, install commands, or distribution status;
- add private-history, authentication, lossless, immutable, or permanent
  storage claims.

## Known follow-up inconsistency

`website/og.png` currently rasterizes the previous hero headline, lead,
and `Transience` nav label. After CHAT-11, Open Graph and Twitter textual
metadata in `website/index.html` may describe the new positioning while
`website/og.png` still shows the old first-viewport copy.

That mismatch is accepted and out of scope. It is not a CHAT-11
completion blocker, defect, or required follow-up. Human acceptance of
this Work directed that no collateral Work be created for it.

## Evidence requirements

- Every new or changed public claim is checked against current
  `chatmd.py`, `test_chatmd.py`, and accepted CHAT-1 through CHAT-10.
- The onepager still makes a public ChatGPT share URL unambiguously
  required.
- None of the forbidden claims appear in title, metadata, hero, Section
  01, T0-T3, nav, footer, or image alt text.
- The hero terminal demo remains unchanged.
- The intended later implementation diff is `website/index.html` only.
- `website/og.png`, `website/styles.css`, other `website/` assets,
  `README.md`, `chatmd.py`, and tests remain unchanged.
- `git diff --check` passes for the intended copy diff.
- Desktop, tablet, and mobile wrapping of the changed copy is visually
  verified in the browser after implementation.
- Existing accessibility, reduced-motion, copy-button, and no-JS behavior
  remain intact.
- Unittest, pyright, and ruff are not required unless product files
  change, which would place the diff outside this Work.
- Local-native render and validate succeed after this Work is added.

Do not retain public conversation bodies, share identifiers, credentials,
cookies, or signed URLs in tracked evidence.

## Acceptance criteria

- [x] The onepager leads with conversation ownership and local capture
      rather than defensive webpage archival.
- [x] It remains unambiguous that a public ChatGPT share URL is required.
- [x] No unsupported lossless, immutable, permanent, history-access, or
      private-capture claims are introduced.
- [x] Creating a share is not described as optional, and ChatMD is not
      described as capturing a conversation independently of its share
      publication.
- [x] Revocation remains visible as post-capture security hygiene and is
      not the primary reason the product exists.
- [x] The terminal demo remains unchanged.
- [x] Existing markup structure and visual system remain unchanged.
- [x] Metadata, hero, Section 01, navigation terminology, and footer do
      not contradict one another.
- [x] Mobile, tablet, and desktop copy wrapping is visually verified after
      implementation.
- [x] The implementation diff is `website/index.html` only.
- [x] `website/og.png` is unchanged. Any remaining visual mismatch with
      the new copy is recorded as the known follow-up inconsistency
      defined by this Work, not fixed here.
- [x] `README.md`, `chatmd.py`, tests, and `website/styles.css` are
      unchanged.
- [x] `git diff --check` and local-native render/validate pass.
- [x] A human accepts the resulting onepager copy against this Work
      contract.

## Completion boundary

CHAT-11 is complete when the implemented onepager leads with owned local
capture of a valuable conversation, still requires a public ChatGPT share
as the capture path, introduces none of the forbidden claims, changes
only textual content in `website/index.html`, preserves the existing
visual system, assets, markup structure, and terminal demo, passes the
required verification, and a human accepts the copy.

A leftover `website/og.png` that still shows the previous positioning
does not block completion.

Do not mark this Work done, check human-accepted criteria, reconcile
authority, commit the implementation, or push unless a later human
decision explicitly authorizes that action.

## Implementation evidence

The accepted product implementation is the local working-tree diff against
HEAD `bbd949a76dcf88e7746a2b4c6f927a64848c2db3`. It is not yet committed.
The implementation change is exactly `website/index.html`.

Authority closeout also changes:

- `authority/Projects/CHAT-P1/Work/CHAT-11.md`;
- render-owned navigation on `authority/Projects/CHAT-P1/CHAT-P1.md`.

The onepager now leads with owned local capture:

```text
Turn a ChatGPT chat
into local Markdown.
You control the file.
```

Section 01 leads with the product job:

```text
Capture the conversation.
Keep the file.
```

The hero lead, hero facts, T0-T3 workflow, nav label `Path`, footer, and
textual metadata remain the accepted CHAT-11 copy. A public ChatGPT share
URL is still required input. Capture is of the visible shared
conversation. Deterministic local Markdown is the output. Revocation
remains post-capture security hygiene.

The hero terminal demo is byte-for-byte identical to HEAD. Markup
structure, `website/styles.css`, `website/og.png`, other `website/`
assets, `README.md`, `chatmd.py`, and tests are unchanged.

No private-history, optional-share, lossless, immutable, or permanent
storage claims were introduced. No collateral Work was created for the
unchanged `website/og.png`.

## Verification

No prepared LWA GO run exists for CHAT-11. Closeout uses the copy
contract, `git diff --check`, authority render/validate, and live
onepager wrap inspection. Absence of a GO bundle does not decide
acceptance. Unittest, pyright, and ruff are not required because no
product files changed.

Recorded local verification:

- `git diff --check` - passed, exit 0;
- hero terminal demo - byte-identical to HEAD;
- live wrap at approximately 375px, 768px, and 1280px:
  - hero: `Turn a ChatGPT chat` / `into local Markdown.` /
    `You control the file.`;
  - Section 01 heading: `Capture the conversation.` / `Keep the file.`;
- `lwa render` / `lwa validate` - ChatMD authority root valid
  (1 project, 11 issues, 1 document, 13 objects).

Closeout inspection of `website/index.html` confirmed the accepted hero,
Section 01 heading, share-required lead and workflow, and unchanged
terminal demo remain in the working tree.

No public conversation body, share identifier, credential, cookie, or
signed URL is retained in tracked evidence.

## Human acceptance

Accepted at `2026-09-20T11:27:00Z` as complete for the CHAT-11 revision 2
boundary.

The human operator reviewed the implemented onepager copy, wrap evidence,
and CHAT-11 contract, then explicitly granted acceptance of CHAT-11 and
authorized authority reconciliation without commit or push.

The unchanged `website/og.png` was explicitly accepted as out of scope.
It is not a blocker, defect, or required follow-up. No collateral Work
was created for it.

## Disposition

`CHAT-11` is completed.

The public onepager leads with turning a ChatGPT chat into local Markdown
under the user's control, still requires a public ChatGPT share URL as
the capture path, and does not introduce forbidden claims. Product
behavior, visual system, assets, markup structure, and the terminal demo
are unchanged.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-11`
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
