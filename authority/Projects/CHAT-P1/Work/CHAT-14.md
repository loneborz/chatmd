<!-- lwa:meta
{
  "id": "CHAT-14",
  "kind": "issue",
  "title": "Synchronize the ChatMD onepager with runtime capture-root behavior",
  "authority": "local-native",
  "revision": 4,
  "status": "done",
  "created_at": "2026-09-20T13:10:05Z",
  "updated_at": "2026-09-20T13:46:40Z",
  "owner": {
    "kind": "project",
    "id": "CHAT-P1"
  },
  "relations": []
}
-->
# Synchronize the ChatMD onepager with runtime capture-root behavior

## Outcome

Synchronize the public ChatMD onepager with the accepted CHAT-13 runtime
capture-root behavior.

The onepager must no longer describe the capture destination as a
machine-specific path compiled into `chatmd.py`, must no longer tell
another machine to edit product source and reinstall, and must no longer
present `~/My vault/Sources/ChatMD/...` as the product destination.

This Work does not change product behavior. It changes only the public
onepager copy so it matches the already accepted destination contract:
`CHATMD_CAPTURE_ROOT` is required machine-local runtime input.

Revision 2 is a human owner copy-contract correction. Revision 1 froze
exact Config and install-aside prose before visual implementation. That
revision keeps the same three website surfaces and required destination
facts, but defines required meaning for Config and install-aside copy
rather than locking final sentences in advance. The hero Saved-path
replacement remains exact. Final wording must be reviewed in the
rendered page during human acceptance before this Work can be completed.

Revision 3 is a human owner install-aside correction. It keeps the
revision 2 meaning contract and all existing non-goals. Inside the
existing install aside only, it now requires a compact command/example
line for:

```sh
export CHATMD_CAPTURE_ROOT="/path/to/captures"
```

Minimal markup changes inside that existing aside are allowed only if
needed to present that command clearly. CSS, broader layout, a fourth
install step, and the GitHub CTA remain unchanged. The card must stay
compact and visually balanced with the install column.

Revision 4 is a human owner final-acceptance correction. It keeps the
revision 3 meaning, export-command, hero-path, and CTA-byte contracts.
Immediately before the existing GitHub CTA, the install aside must show
a small `MORE ON GITHUB` label using the existing `.mono-label`
treatment already used in that card. The GitHub CTA itself remains
byte-for-byte unchanged. No other visual or copy change is authorized.

## Governing authority / source of truth

CHAT-P1 defines the product purpose, local-first boundary, no-rewrite
invariant, and the one-URL public-share interface. This Work does not
change that Project contract.

Accepted CHAT-13 defines the current destination behavior. The installed
`chatmd` command resolves an absolute capture root from the process
environment variable `CHATMD_CAPTURE_ROOT`. Product source does not
encode a machine-specific or vault-specific destination. A missing,
empty, or non-absolute value fails before fetch or write. Changing the
capture directory later does not require editing product source or
reinstalling. CHAT-13 explicitly excluded website updates and is closed.
This Work does not reopen CHAT-13.

Accepted CHAT-11 established the public onepager framing and remains
closed. This Work preserves that framing, including the required public
share path, revocation as post-capture security hygiene, and the CHAT-11
forbidden claims. It does not reopen CHAT-11. CHAT-11 froze the hero
terminal demo, including the saved-path example. This later Work
authorizes one bounded exception: the hero Saved-path text only.

Accepted CHAT-6 and CHAT-12 own the public GitHub README as a separate
landing page and remain closed. CHAT-13 already updated `README.md` to
the runtime capture-root contract. This Work does not change `README.md`
and does not reopen CHAT-6 or CHAT-12.

Accepted CHAT-5 defines reliable local capture and recorded this
operator's then-current vault path as that Work's local destination. This
Work does not reopen CHAT-5. That vault path is not a public product
default.

The current `chatmd.py` and `test_chatmd.py` implementation, together
with accepted CHAT-13, are the technical source of truth for destination
behavior. Current README copy is already aligned and is reference only.

The implemented onepager surface is `website/index.html`. There is no
template. `website/styles.css` and the surrounding `website/` assets
remain the visual source of truth. This Work may change textual content
inside `website/index.html`, plus the one install-aside markup exception
defined in Scope. It does not authorize CSS or other files.

Repository inspection after CHAT-13 found these stale onepager claims:

- Section 05 Config row still says the capture root is machine-specific
  and set in `chatmd.py`;
- the install aside still says the capture root is a machine-specific
  path inside `chatmd.py`, that another machine must change it and
  reinstall, and that portable capture-root configuration does not exist
  yet;
- the hero terminal Saved path still shows
  `~/My vault/Sources/ChatMD/2026/09/<conversation>.md`;
- the install numbered steps, GitHub CTA, hero command, copy-button
  payload, and remaining terminal result are otherwise current.

CHAT-D1 remains the active portable bundle contract. The current output
does not implement it. CHAT-D1 does not govern this Work. The onepager
must continue to describe that bundle as specified, not implemented.

After implementation, `website/index.html` is the source of truth for the
onepager copy authorized by this Work. The repository implementation and
accepted Work remain the source of truth for product behavior. Human
acceptance remains a separate authority decision and includes review of
the final Config and install-aside wording on the rendered page.

## Authorized implementation surface

This authorization lives in
`authority/Projects/CHAT-P1/Work/CHAT-14.md`.

Later implementation may change `website/index.html` only: the three
authorized copy surfaces, plus the install-aside markup exception in
Scope.

No other file is authorized.

## Scope

This Work is strictly textual content only, except for the install-aside
markup exception below.

In `website/index.html`, change exactly three surfaces:

- the Section 05 Config row;
- the existing install aside, including the authorized command line;
- the hero Saved-path text.

Do not change class names, attributes, copy-button payloads, or the
GitHub CTA except as required by the install-aside exception. Do not
change the install numbered steps or any element outside those three
surfaces.

Config and install-aside copy are bound by required meaning, not by
frozen sentences, except for the exact export command below. Choose
compact wording that fits the existing layout and visual balance. The
hero Saved-path replacement is exact.

### 1. Section 05 Config row

Current visible text:

```text
The capture root is machine-specific and set in chatmd.py
```

Replace only the Config value span. Required meaning: `CHATMD_CAPTURE_ROOT`
controls the capture destination at runtime, outside product source.

That row must not say the capture root is machine-specific, compiled into
`chatmd.py`, or otherwise set in product source.

Keep `CHATMD_CAPTURE_ROOT` wrapped in the existing inline `code` pattern
used by nearby boundary rows if the env var is named. Do not add, remove,
or reorder the Config list item. Do not freeze a specific sentence before
the rendered page is reviewed.

### 2. Install aside

Current aside heading and body:

```text
Before you run it elsewhere

The capture root is currently a machine-specific path inside
chatmd.py. On another machine, change it and reinstall.
Portable capture-root configuration does not exist yet.
```

Change only the existing install aside. Keep the GitHub CTA byte-for-byte,
including href `https://github.com/loneborz/chatmd`, classes
`btn btn-primary full`, visible label `loneborz/chatmd`, and the existing
arrow span.

Required content flow, in this order:

1. Explain that `CHATMD_CAPTURE_ROOT` tells ChatMD where to save captures
   on this machine.
2. Show this exact command/example line:

```sh
export CHATMD_CAPTURE_ROOT="/path/to/captures"
```

3. Optionally add a short closing line such as `Configure it once, then
   run chatmd from anywhere.` if it improves clarity without crowding
   the card.
4. Immediately before the existing GitHub CTA, add a small
   `MORE ON GITHUB` label. Reuse the existing `.mono-label` treatment
   already used in this card. Do not change CSS.

The aside must not tell another machine to edit `chatmd.py` and
reinstall, and must not say that portable capture-root configuration
does not exist yet.

Fail-before-write behavior and no-reinstall behavior are accurate
CHAT-13 facts. They are optional website copy. Include them only if they
keep the aside clear and visually balanced. Do not add them if they
crowd the existing aside.

Keep `CHATMD_CAPTURE_ROOT` wrapped in inline `code` where it appears in
prose. Keep the card compact and visually balanced with the install
column.

Narrow markup exception, install aside only: minimal markup changes
inside the existing `<aside class="install-note">` are allowed only if
needed to present the export command clearly, or to add the authorized
`MORE ON GITHUB` label immediately before the GitHub CTA. Reuse existing
classes already in `website/index.html` if a command-shaped element or
the label is needed. Do not add a fourth install step, a second card, a
copy button, or any element outside that aside. Do not change CSS. Do
not make broader layout changes. Do not alter the GitHub CTA markup.

Do not freeze the heading, explanation, or optional closing line before
the rendered page is reviewed. The export command itself is exact.

### 3. Hero Saved-path text

Current hero Saved path:

```text
~/My vault/Sources/ChatMD/2026/09/<conversation>.md
```

Replace only the existing `.t-path` text with exactly:

```text
/path/to/captures/2026/09/<conversation>.md
```

Keep the existing HTML entity encoding for `<conversation>`. Do not
change the capture command, copy-button payload, `CAPTURE COMPLETE`
result, `Saved:` label, shared-source line, or security warning.

Leave every other onepager string unchanged, including CHAT-11 hero
headline and lead, Section 01, T0-T3, navigation, footer, metadata, and
the install heading and numbered steps.

Do not restructure markup except for the install-aside exception above.
Preserve the existing visual, accessibility, interaction, typography,
responsive, and security-warning constraints already encoded in
`website/index.html` and `website/styles.css`.

`website/og.png` remains the accepted CHAT-11 leftover and is not in
scope.

## Non-goals

Do not:

- modify `chatmd.py`;
- modify tests;
- modify `README.md`;
- change `website/styles.css` or any visual treatment;
- regenerate or modify `website/og.png`;
- change any image, font, favicon, or other asset;
- restructure markup;
- redesign the page;
- change hero behavior beyond the Saved-path text authorized above;
- add packaging, Homebrew, public package publishing, or release
  automation;
- deploy or publish `chatmd.wavesweb.nl`;
- introduce configuration files, settings UI, CLI destination flags,
  or other new configuration capabilities;
- discover, infer, or hardcode an Obsidian vault or other consumer
  layout;
- implement CHAT-D1;
- reopen CHAT-13 or any prior CHAT Work;
- change Project, Document, or prior Work contracts beyond the
  navigation generated by render;
- invent capabilities, install commands, or distribution status;
- add private-history, authentication, lossless, immutable, or
  permanent storage claims.

The install-aside markup exception in Scope is the only authorized
departure from the markup non-goal. It does not authorize CSS, a page
redesign, or markup changes outside that aside.

## Evidence requirements

- Every changed public claim is checked against current `chatmd.py`,
  `test_chatmd.py`, accepted CHAT-13, and current README destination
  copy.
- The Config row communicates the required meaning defined in Scope.
- The install aside communicates the required first-time setup meaning
  defined in Scope, in the authorized order.
- The install aside includes the exact export command from Scope.
- The hero Saved-path text matches the exact replacement in Scope.
- The onepager no longer says the capture root is set in `chatmd.py`, no
  longer says another machine must edit source and reinstall, and no
  longer says portable capture-root configuration does not exist yet.
- The onepager no longer presents `~/My vault/Sources/ChatMD/...` as the
  product destination.
- The GitHub CTA remains unchanged.
- The install aside includes a small `MORE ON GITHUB` label immediately
  before that CTA, using the existing `.mono-label` treatment.
- The hero terminal demo is otherwise unchanged, including the
  copy-button payload.
- CHAT-11 framing, forbidden claims, share-required input, and
  post-capture revocation hygiene remain intact.
- The intended later implementation diff is `website/index.html` only.
- `website/og.png`, `website/styles.css`, other `website/` assets,
  `README.md`, `chatmd.py`, and tests remain unchanged.
- Markup structure is unchanged outside the install-aside exception:
  no added, removed, or reordered elements elsewhere, and no CSS
  changes.
- The install aside remains compact and visually balanced with the
  install column.
- `git diff --check` passes for the intended copy diff.
- Desktop, tablet, and mobile wrapping of the changed copy is visually
  verified in the browser after implementation.
- Existing accessibility, reduced-motion, copy-button, and no-JS
  behavior remain intact.
- Unittest, pyright, and ruff are not required unless product files
  change, which would place the diff outside this Work.
- Local-native render and validate succeed after this Work is added.
- Final Config and install-aside wording are reviewed in the rendered
  page during human acceptance.

Do not retain public conversation bodies, share identifiers,
credentials, cookies, or signed URLs in tracked evidence.

## Acceptance criteria

- [x] The Config row communicates that `CHATMD_CAPTURE_ROOT` controls
      the capture destination at runtime, outside product source.
- [x] The Config row no longer describes a compiled `chatmd.py`
      capture root.
- [x] The install aside first explains that `CHATMD_CAPTURE_ROOT` tells
      ChatMD where to save captures on this machine.
- [x] The install aside then shows exactly
      `export CHATMD_CAPTURE_ROOT="/path/to/captures"`.
- [x] Any closing line, including `Configure it once, then run chatmd
      from anywhere.`, is optional and does not crowd the card.
- [x] The install aside no longer says to edit `chatmd.py`, reinstall,
      or that portable capture-root configuration does not exist yet.
- [x] Fail-before-write and no-reinstall facts, if present, do not
      reduce clarity or visual balance. Their absence is acceptable.
- [x] A small `MORE ON GITHUB` label sits immediately before the
      GitHub CTA and uses the existing `.mono-label` treatment.
- [x] The existing GitHub CTA is unchanged.
- [x] The install aside stays compact and visually balanced with the
      install column. Any markup added for the command or the
      `MORE ON GITHUB` label is confined to that aside and does not
      change CSS.
- [x] The hero Saved-path text is
      `/path/to/captures/2026/09/<conversation>.md` and no longer uses
      `~/My vault/Sources/ChatMD/...`.
- [x] The rest of the hero terminal demo, including the copy-button
      payload, is unchanged.
- [x] CHAT-11 framing is unchanged: share URL remains required input,
      revocation remains post-capture security hygiene, and no
      forbidden claims are introduced.
- [x] Existing visual system, CSS, and assets are unchanged.
- [x] The implementation diff is `website/index.html` only.
- [x] `README.md`, `chatmd.py`, tests, `website/styles.css`, and
      `website/og.png` are unchanged.
- [x] Mobile, tablet, and desktop copy wrapping is visually verified
      after implementation.
- [x] `git diff --check` and local-native render/validate pass.
- [x] CHAT-13 and all prior CHAT Work remain closed.
- [x] A human reviews the final wording in the rendered page and
      accepts the resulting onepager copy against this Work contract.

## Completion boundary

CHAT-14 is complete when the public onepager describes the accepted
CHAT-13 runtime capture-root behavior, the three authorized copy
surfaces satisfy this revision's meaning, export-command, exact-path,
and `MORE ON GITHUB` label contracts, the GitHub CTA remains
byte-for-byte unchanged, layout, styling, hero behavior, and CHAT-11
framing are otherwise unchanged, the required verification passes, and
a human accepts the copy after reviewing the final wording in the
rendered page.

Do not mark this Work done, check human-accepted criteria, reconcile
authority, commit the implementation, or push unless a later human
decision explicitly authorizes that action.

## Implementation evidence

The accepted product implementation is the local working-tree diff
against HEAD `d04bff25ffae7f1e029d8d1a6df9c1a7804405b5`. The
implementation change is exactly `website/index.html`.

Authority closeout also changes:

- `authority/Projects/CHAT-P1/Work/CHAT-14.md`;
- render-owned navigation on `authority/Projects/CHAT-P1/CHAT-P1.md`.

The three authorized onepager surfaces now read:

- Config: `Capture destination is set by CHATMD_CAPTURE_ROOT at runtime`;
- install aside: heading `Set the capture directory`, explanation that
  `CHATMD_CAPTURE_ROOT` tells ChatMD where captures are saved on this
  machine, exact command
  `export CHATMD_CAPTURE_ROOT="/path/to/captures"`, optional closer
  `Configure it once, then run chatmd from anywhere.`, then a
  `.mono-label` `More on GitHub` immediately before the unchanged
  GitHub CTA;
- hero Saved path:
  `/path/to/captures/2026/09/<conversation>.md`.

The GitHub CTA remains byte-for-byte identical to HEAD, including href
`https://github.com/loneborz/chatmd`, classes `btn btn-primary full`,
visible label `loneborz/chatmd`, and the existing arrow span. A
`<wbr>` after `=` in the export command is markup-only wrap inside the
authorized aside. `website/styles.css`, `website/og.png`, other
`website/` assets, `README.md`, `chatmd.py`, and tests are unchanged.
CHAT-13 and prior CHAT Work were not reopened.

## Verification

No prepared LWA GO run exists for CHAT-14. Closeout uses the copy
contract, `git diff --check`, authority render/validate, and live
onepager wrap inspection. Absence of a GO bundle does not decide
acceptance. Unittest, pyright, and ruff are not required because no
product files changed.

Recorded local verification:

- `git diff -- website/index.html` - Config row, install aside, and
  hero Saved-path text only;
- GitHub CTA markup - byte-identical to HEAD;
- `website/styles.css` - unchanged;
- live wrap at 375px, 768px, and 1280px with no horizontal overflow
  in the install aside command box;
- `MORE ON GITHUB` rendered with the same 10.5px uppercase
  `.mono-label` treatment as `SET THE CAPTURE DIRECTORY`, immediately
  before the GitHub CTA;
- hero copy-button payload unchanged:
  `chatmd https://chatgpt.com/share/<public-share-id>`;
- `git diff --check` - passed, exit 0;
- `lwa render` / `lwa validate` - ChatMD authority root valid.

No public conversation body, share identifier, credential, cookie, or
signed URL is retained in tracked evidence.

## Human acceptance

Accepted at `2026-09-20T13:46:40Z` as complete for the CHAT-14
revision 4 boundary.

The human operator reviewed the rendered onepager copy, authorized the
final `MORE ON GITHUB` label immediately before the existing GitHub
CTA, and explicitly granted acceptance of CHAT-14 together with
authority reconciliation, commit of the CHAT-14 change set, and push
to `origin/main`.

## Disposition

`CHAT-14` is completed.

The public onepager now describes accepted CHAT-13 runtime capture-root
behavior: `CHATMD_CAPTURE_ROOT` is required machine-local runtime
input, the install aside shows the exact export command, and the hero
Saved path uses `/path/to/captures/...`. The GitHub CTA is unchanged.
Product behavior, visual system, CSS, and assets are unchanged.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-14`
- Kind: `issue`
- Status: `done`
- Revision: `4`
- Authority: `local-native`
- Owner: [[Projects/CHAT-P1/CHAT-P1|CHAT-P1]]: chatmd

## Owned Documents

_None._

## Relations

_None._

## Backlinks

_None._
<!-- lwa:derived:end -->
