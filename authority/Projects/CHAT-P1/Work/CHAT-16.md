<!-- lwa:meta
{
  "id": "CHAT-16",
  "kind": "issue",
  "title": "Remove specified divider lines from the ChatMD onepager",
  "authority": "local-native",
  "revision": 3,
  "status": "done",
  "created_at": "2026-09-20T17:23:00Z",
  "updated_at": "2026-09-20T17:40:05Z",
  "owner": {
    "kind": "project",
    "id": "CHAT-P1"
  },
  "relations": []
}
-->
# Remove specified divider lines from the ChatMD onepager

## Outcome

Remove the specified divider lines from three existing public onepager
strips. This is a bounded visual cleanup. It does not redesign those
sections, change copy, change typography, change color, or expand
scope.

The three surfaces are the hero facts strip, the Capture path T0-T3
sequence, and the Failure semantics trio. Product behavior does not
change.

Revision 2 is a human owner scope correction. Revision 1
pre-authorized removing Capture path `padding-bottom: 26px` at
`max-width: 960px`. This revision keeps the same three surfaces and
divider-removal contract, but does not authorize that spacing change.
Existing padding and spacing remain unchanged. No spacing adjustment
is currently authorized. A later spacing change would require the
rendered surface to be demonstrably incorrect after divider removal
and an explicit human approval.

## Governing authority / source of truth

CHAT-P1 defines the product purpose, local-first boundary, no-rewrite
invariant, and the one-URL public-share interface. This Work does not
change that Project contract.

Accepted CHAT-11 established the public onepager framing and remains
closed. This Work preserves that framing, copy, and markup structure.
CHAT-11 did not authorize CSS changes. This later Work authorizes only
the smallest CSS change needed to remove the specified dividers.

Accepted CHAT-14 and CHAT-15 remain closed. They own capture-root copy
and the install-aside presentation. This Work does not reopen them and
does not touch the install aside, Config row, or hero terminal demo.

The implemented onepager surface is `website/index.html`.
`website/styles.css` remains the visual source of truth. Current
divider treatment is CSS on existing elements. Markup does not need to
change unless a later implementation proves a CSS-only change is
impossible.

Operator-provided screenshots of the live onepager, plus current
`website/index.html` and `website/styles.css`, are the visual evidence
for this refinement. Repository inspection found:

1. Hero facts (`.hero-facts`): four items Input, Output, Network, and
   Model use. The strip has `border-top` and each item has
   `border-right`. At `max-width: 960px` and `max-width: 560px`, those
   column rules become stacked `border-bottom` rules.

2. Capture path (`.timeline`): T0, T1, T2, T3. The sequence has
   `border-top` as the horizontal timeline, 5px square `::before`
   markers on that line, and `border-right` between columns. At
   `max-width: 960px`, the first two items also gain `border-bottom`
   and existing `padding-bottom: 26px`. That padding is current
   spacing, not a divider. At `max-width: 560px`, items gain stacked
   `border-bottom`, and markers move to the left of each item.

3. Failure semantics (`.trio`): Fail visible, Never overwrite, and
   Persist, then report. The row has `border-top` and each article has
   `border-right`. At `max-width: 960px`, those column rules become
   stacked `border-bottom` rules.

CHAT-D1 remains the active portable bundle contract and does not govern
this Work.

After implementation, `website/styles.css` is the source of truth for
the divider treatment authorized by this Work. Human acceptance remains
a separate authority decision and includes review of the rendered
page.

## Authorized implementation surface

This authorization lives in
`authority/Projects/CHAT-P1/Work/CHAT-16.md`.

Implementation may change `website/styles.css` only, and only the
divider rules for `.hero-facts`, `.timeline`, and `.trio`, including
the responsive rules that currently convert those column dividers into
stacked borders. Padding, margin, gap, and other spacing rules are
not authorized.

`website/index.html` is authorized only if a CSS-only change cannot
remove the specified dividers. No other file is authorized.

## Scope

Remove the specified dividers. Keep the existing text, typography,
content, ordering, grid structure, marker treatment, padding, and
spacing. No spacing adjustment is currently authorized.

### 1. Hero facts strip

Current visible items, in order:

```text
INPUT
One public share URL

OUTPUT
One Markdown file

NETWORK
Ordinary HTTP, no browser

MODEL USE
None in the capture path
```

Remove all horizontal and vertical divider lines from this strip.
That includes:

- `.hero-facts` `border-top`;
- `.hero-facts li` `border-right`;
- the last-child `border-right: 0` companion;
- the responsive stacked `border-bottom` rules for `.hero-facts li`.

Keep the four items, their labels, their values, their order, and the
existing four-column / two-column / one-column grid behavior. Keep
`.hero-facts` `margin-top` and item padding. Do not restyle the
labels or values.

### 2. Capture path timeline

The T0, T1, T2, T3 sequence currently has one horizontal timeline,
small square markers, and vertical divider lines between the four
columns.

Keep the horizontal timeline and its markers exactly as part of the
visual structure. That means keep `.timeline` `border-top` and the
`li::before` marker rules, including the mobile marker position
(`top: 26px; left: 0` with `padding-left: 14px` at `max-width:
560px`) and the T3 `.terminal-state` marker fill.

Remove only the specified vertical column borders and the responsive
stacked `border-bottom` rules between T0, T1, T2, and T3. That
includes:

- `.timeline li` `border-right`;
- the last-child `border-right: 0` companion;
- the `max-width: 960px` stacked `border-bottom` on the first two
  items;
- the `max-width: 560px` stacked `border-bottom` on `.timeline li`.

Keep existing padding and spacing unchanged, including
`padding-bottom: 26px` on the first two items at `max-width: 960px`.
If that padding shares a CSS rule with `border-bottom`, remove only
the border property. Do not delete or change the padding declaration.

Do not otherwise redesign the timeline. Keep the four columns, copy,
heading treatment, T3 terminal-state text color, and existing
padding. No spacing adjustment is currently authorized.

### 3. Failure semantics trio

The Fail visible, Never overwrite, and Persist, then report row
currently has vertical divider lines between the columns.

Preserve the existing horizontal divider above the row. That means
keep `.trio` `border-top`.

Remove the vertical divider lines between the three columns. That
includes:

- `.trio article` `border-right`;
- the last-child `border-right: 0` companion;
- the `max-width: 960px` stacked `border-bottom` rules for
  `.trio article`.

Keep the existing stacked padding at `max-width: 960px`
(`padding: 24px 0`). Do not otherwise redesign this section. Keep
the three articles, copy, label treatment, and remaining desktop
padding.

Shared responsive layout rules that only set grid columns, such as
`.hero-facts, .timeline { grid-template-columns: 1fr 1fr; }`, stay.
Companion `border-right: 0` rules that exist only because the column
dividers exist may be deleted with those dividers.

## Non-goals

Do not:

- change copy, typography, color, or content order;
- redesign layout, spacing, or visual hierarchy beyond what removing
  the specified borders requires;
- change `.timeline` `border-top` or the timeline markers;
- change `.trio` `border-top`;
- restyle other page borders, including nav, bands, terminal, panels,
  pipeline, ledger, warning, install, footer, or buttons;
- modify `website/index.html` unless a CSS-only change is impossible;
- modify `chatmd.py` or tests;
- modify `README.md`;
- regenerate or modify `website/og.png` or other assets;
- change the install aside, Config row, hero terminal, navigation,
  footer, or metadata;
- add packaging, Homebrew, or public package publishing;
- deploy or publish `chatmd.wavesweb.nl`;
- reopen CHAT-15 or any prior CHAT Work;
- introduce forbidden CHAT-11 claims.

## Evidence requirements

- The hero facts strip has no `border-top`, no item `border-right`,
  and no stacked item `border-bottom`.
- Capture path retains `.timeline` `border-top` and the square
  `::before` markers, including the mobile marker position and the T3
  marker fill.
- Capture path has no column `border-right` and no stacked item
  `border-bottom`.
- Capture path padding and spacing remain unchanged, including
  `padding-bottom: 26px` at `max-width: 960px`.
- Failure semantics retains `.trio` `border-top`.
- Failure semantics has no article `border-right` and no stacked
  article `border-bottom`.
- Visible text, typography, content, and order in the three surfaces
  are unchanged.
- The implementation diff is `website/styles.css` only, unless
  markup must change to make the border removal possible.
- Other onepager sections, README, product files, tests, and assets
  are unchanged.
- Desktop, tablet, and mobile rendering of the three surfaces is
  visually verified after implementation.
- `git diff --check` and local-native render/validate pass.
- CHAT-15 and all prior CHAT Work remain closed.

Do not retain public conversation bodies, share identifiers,
credentials, cookies, or signed URLs in tracked evidence.

## Acceptance criteria

- [x] Hero facts strip has no horizontal divider lines.
- [x] Hero facts strip has no vertical divider lines.
- [x] Capture path retains its horizontal timeline and markers.
- [x] Capture path has no vertical column dividers.
- [x] Failure semantics retains its existing horizontal divider.
- [x] Failure semantics has no vertical column dividers.
- [x] Existing text, typography, content, ordering, spacing intent,
      responsive behavior, and functionality remain unchanged except
      where removal of the specified borders naturally affects
      rendering.
- [x] No unrelated visual cleanup or refactoring is included.
- [x] The intended implementation diff is `website/styles.css` only,
      unless markup must change to make the border removal possible.
- [x] README, product files, tests, assets, install aside, Config
      row, and hero terminal are unchanged.
- [x] `git diff --check` and local-native render/validate pass.
- [x] CHAT-15 and all prior CHAT Work remain closed.
- [x] A human accepts the rendered three surfaces against this Work
      contract.

## Completion boundary

CHAT-16 is complete when the three specified divider cleanups are in
place, the retained timeline and failure horizontal rules remain, copy
and layout are otherwise unchanged, the required verification passes,
and a human accepts the rendered result.

Do not mark this Work done, check human-accepted criteria, reconcile
authority, commit, or push unless a later human decision explicitly
authorizes that action.

## Implementation evidence

The accepted product implementation is the local working-tree diff
against HEAD `32dd9ed60e8c5c6640a9f50c571113ea98b6fb6f`.

Implementation changes:

- `website/styles.css`, divider rules for `.hero-facts`, `.timeline`,
  and `.trio` only, including the responsive stacked-border companions.

Authority closeout also changes:

- `authority/Projects/CHAT-P1/Work/CHAT-16.md`;
- render-owned navigation on `authority/Projects/CHAT-P1/CHAT-P1.md`.

`website/index.html` was not modified. Copy, typography, color, grid
structure, Capture path `border-top` and square markers, Failure
semantics `border-top`, and existing padding remain. Capture path
`padding-bottom: 26px` at `max-width: 960px` is preserved. The `.band`
section boundary below the hero is unchanged and outside this Work.

## Verification

Prepared LWA GO run
`go-20260920T173303.071602000Z-a7bf525c0434c5cd` froze CHAT-16 revision
2 at repository HEAD `32dd9ed60e8c5c6640a9f50c571113ea98b6fb6f`.
`prepared.commit` contains `prepared`. Authority SHA-256
`f38aae5d7e4422554851fcaa977993a6ae3fe11f43082575f655d6c3d0468913`.

`lwa run start` correctly refused the dirty working tree outside
`.codex/runs`. The blocking paths were the uncommitted CHAT-16
authority and implementation, plus unrelated pre-existing files
(`.DS_Store`, `uv.lock`, older `.codex/` material). Start requires the
prepared HEAD and a tree that is clean outside `.codex/runs`. Hiding
those files, stashing, or resetting would bypass that invariant.
Committing first would move HEAD away from the prepared baseline and
still prevent start. The run therefore remains prepared and unstarted.
It was not finalized or retained.

CHAT-16 evidence requirements do not require a started, finalized, or
retained run. Closeout uses the accepted CSS contract, live onepager
inspection, `git diff --check`, and authority render/validate.
Unittest, pyright, and ruff are not required because no product files
changed.

Recorded local verification:

- desktop 1280px, tablet 768px, and mobile 375px computed styles:
  hero facts have no top, right, or stacked bottom borders;
- Capture path keeps `.timeline` `border-top` and 5px square markers,
  including mobile `top: 26px; left: 0` and the T3 marker fill;
- Capture path has no column `border-right` and no stacked
  `border-bottom`;
- first two Capture path items keep `padding-bottom: 26px` at 768px;
- Failure semantics keeps `.trio` `border-top` and has no article
  `border-right` or stacked `border-bottom`;
- trio stacked padding remains `24px 0`;
- `git diff -- website/styles.css` - divider-rule removals only;
- `website/index.html`, README, product files, tests, and assets
  unchanged;
- `git diff --check` - passed, exit 0;
- `lwa render` / `lwa validate` - ChatMD authority root valid.

No public conversation body, share identifier, credential, cookie, or
signed URL is retained in tracked evidence.

## Human acceptance

Accepted at `2026-09-20T17:37:00Z` as complete for the CHAT-16
revision 2 boundary.

The human operator reviewed the rendered onepager and granted
acceptance of CHAT-16 revision 2 against this Work contract:

- Hero facts: no horizontal or vertical divider lines remain within
  the facts strip; copy, ordering, spacing, typography, and layout
  remain correct.
- Capture path: horizontal timeline and square markers remain;
  vertical column dividers are gone; existing spacing is preserved,
  including the authorized responsive padding behavior.
- Failure semantics: horizontal divider above the row remains;
  vertical column dividers are gone; existing content and spacing
  remain correct.
- The existing `.band` section boundary below the hero is explicitly
  accepted as unchanged and outside CHAT-16 scope.

The human operator also authorized authority reconciliation, commit of
the CHAT-16 change set, and push to `origin/main`. Deployment of
`chatmd.wavesweb.nl` remains outside this Work.

## Disposition

`CHAT-16` is completed.

The public onepager no longer draws the specified divider lines in the
hero facts strip, Capture path columns, or Failure semantics columns.
The Capture path timeline and markers remain. The Failure semantics
horizontal rule remains. Copy, spacing, and the rest of the page are
unchanged.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-16`
- Kind: `issue`
- Status: `done`
- Revision: `3`
- Authority: `local-native`
- Owner: [[Projects/CHAT-P1/CHAT-P1|CHAT-P1]]: chatmd

## Owned Documents

_None._

## Relations

_None._

## Backlinks

_None._
<!-- lwa:derived:end -->
