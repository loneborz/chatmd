<!-- lwa:meta
{
  "id": "CHAT-15",
  "kind": "issue",
  "title": "Polish the ChatMD install aside capture-root card",
  "authority": "local-native",
  "revision": 1,
  "status": "done",
  "created_at": "2026-09-20T14:04:05Z",
  "updated_at": "2026-09-20T14:11:28Z",
  "owner": {
    "kind": "project",
    "id": "CHAT-P1"
  },
  "relations": []
}
-->
# Polish the ChatMD install aside capture-root card

## Outcome

Make the existing public onepager capture-root card easier to scan and
less cramped, without redesigning the install section.

Accepted CHAT-14 already aligned that card with CHAT-13 runtime
capture-root behavior. This Work does not reopen CHAT-14. It refines
only the rendered presentation of that same card: copy hierarchy,
whitespace, grouping, and command wrap.

The technical meaning remains: `CHATMD_CAPTURE_ROOT` is required
machine-local runtime input that chooses where captures are saved.
This Work does not change product behavior.

## Governing authority / source of truth

CHAT-P1 defines the product purpose, local-first boundary, no-rewrite
invariant, and the one-URL public-share interface. This Work does not
change that Project contract.

Accepted CHAT-13 defines destination behavior and remains closed. The
installed `chatmd` command resolves an absolute capture root from
`CHATMD_CAPTURE_ROOT`. Product source does not encode a machine-specific
destination. This Work does not reopen CHAT-13.

Accepted CHAT-14 defined the public onepager capture-root copy and
remains closed. Its accepted meaning, exact export command, GitHub CTA
destination and label, Config row, and hero Saved-path text remain in
force. This Work may change only the install-aside presentation of that
already accepted meaning.

Accepted CHAT-11 established the public onepager framing and remains
closed. This Work preserves that framing.

The implemented onepager surface is `website/index.html`.
`website/styles.css` remains the visual source of truth. This Work may
change markup inside the existing `<aside class="install-note">` and the
smallest CSS required for that aside's readability. It does not
authorize a wider install-section redesign.

Current rendered-card evidence, after CHAT-14:

- heading `Set the capture directory`;
- explanation that `CHATMD_CAPTURE_ROOT` tells ChatMD where captures
  are saved on this machine;
- exact command `export CHATMD_CAPTURE_ROOT="/path/to/captures"` inside
  `.cmd`, wrapping via `<wbr>` after `=`;
- closer `Configure it once, then run chatmd from anywhere.`;
- `.mono-label` `More on GitHub` immediately before the GitHub CTA;
- CTA `loneborz/chatmd` to `https://github.com/loneborz/chatmd`.

That card is technically correct and still cramped: explanation, command,
closer, GitHub label, and CTA share one undifferentiated stack, and the
command wrap reads as overflow rather than a designed two-line command.

## Authorized implementation surface

This authorization lives in
`authority/Projects/CHAT-P1/Work/CHAT-15.md`.

Implementation may change:

- `website/index.html`, only inside the existing
  `<aside class="install-note">`;
- `website/styles.css`, only rules required by that aside's
  presentation.

No other file is authorized.

## Scope

Refine the existing install aside so the rendered hierarchy is:

```text
SET THE CAPTURE DIRECTORY

Choose where ChatMD saves captures.

export CHATMD_CAPTURE_ROOT="/path/to/captures"

Set it once, then run chatmd from anywhere.

MORE ON GITHUB

[loneborz/chatmd CTA]
```

Required meaning: the card still tells the reader that
`CHATMD_CAPTURE_ROOT` chooses where ChatMD saves captures, that the
export line is the setup command, and that the setting is done once
before running `chatmd`.

Keep this exact command unless a later human decision changes it:

```sh
export CHATMD_CAPTURE_ROOT="/path/to/captures"
```

Keep the GitHub CTA destination
`https://github.com/loneborz/chatmd` and visible label
`loneborz/chatmd`. The CTA may be grouped with the `MORE ON GITHUB`
label. Do not change its destination or label.

Improve whitespace and grouping so explanation, command, closing
sentence, GitHub label, and CTA are distinct to scan. Related items
sit tightly; those groups separate more generously.

Present the export command as an intentional two-line command, not as
an accidentally overflowing one-liner. There must be no horizontal
scrollbar in the aside at desktop, tablet, or mobile widths.

Minimal markup and CSS inside this aside are allowed. Reuse existing
classes where they still fit. Do not add a copy button, a fourth
install step, or a second card. Do not restyle the numbered install
steps, section heading, or the two-column install grid beyond what
those existing layout rules already do.

## Non-goals

Do not:

- reopen CHAT-14 or any prior CHAT Work;
- modify `chatmd.py` or tests;
- modify `README.md`;
- change the hero, Config row, install numbered steps, navigation,
  footer, or metadata;
- regenerate or modify `website/og.png` or other assets;
- redesign the wider install section;
- add packaging, Homebrew, or public package publishing;
- deploy or publish `chatmd.wavesweb.nl`;
- invent configuration files, CLI destination flags, or new
  destination behavior;
- introduce forbidden CHAT-11 claims.

## Evidence requirements

- The rendered aside matches the Scope hierarchy and meaning.
- The export command text remains
  `export CHATMD_CAPTURE_ROOT="/path/to/captures"`.
- The GitHub CTA destination and label are unchanged.
- The command presentation is an intentional wrap with no horizontal
  scrollbar at approximately 1280px, 768px, and 375px.
- Explanation, command, closer, GitHub label, and CTA are visually
  grouped rather than equally cramped.
- The implementation diff is `website/index.html` and
  `website/styles.css` only, confined to this aside.
- Hero, Config row, README, product files, tests, and assets are
  unchanged.
- `git diff --check` and local-native render/validate pass.
- CHAT-14 and all prior CHAT Work remain closed.

## Acceptance criteria

- [x] The aside heading remains `Set the capture directory`.
- [x] The explanation is `Choose where ChatMD saves captures.`
- [x] The command text is exactly
      `export CHATMD_CAPTURE_ROOT="/path/to/captures"`.
- [x] The closer is `Set it once, then run chatmd from anywhere.`
- [x] A `MORE ON GITHUB` label sits immediately before the GitHub CTA.
- [x] The GitHub CTA destination and label remain
      `https://github.com/loneborz/chatmd` and `loneborz/chatmd`.
- [x] Whitespace and grouping make explanation, command, closer, GitHub
      label, and CTA easier to scan than the CHAT-14 card.
- [x] The command wrap looks intentional at 1280px, 768px, and 375px.
- [x] The aside has no horizontal scrollbar at those widths.
- [x] The numbered install steps and section framing are unchanged.
- [x] Hero, Config row, README, product files, tests, and assets are
      unchanged.
- [x] CSS changes are limited to this aside's presentation.
- [x] `git diff --check` and local-native render/validate pass.
- [x] CHAT-14 and all prior CHAT Work remain closed.
- [x] A human accepts the rendered card against this Work contract.

## Completion boundary

CHAT-15 is complete when the existing capture-root card matches the
authorized hierarchy, remains faithful to CHAT-13/CHAT-14 meaning, is
easier to scan without a horizontal scrollbar, leaves the rest of the
onepager unchanged, passes required verification, and a human accepts
the rendered result.

Do not mark this Work done, check human-accepted criteria, reconcile
authority, commit, or push unless a later human decision explicitly
authorizes that action.

## Implementation evidence

The accepted product implementation is the local working-tree diff
against HEAD `0f33ca845ffb8dac29e3e60a825ccb6e195a9a99`.

Implementation changes:

- `website/index.html`, inside `<aside class="install-note">` only;
- `website/styles.css`, install-aside presentation rules only.

Authority closeout also changes:

- `authority/Projects/CHAT-P1/Work/CHAT-15.md`;
- render-owned navigation on `authority/Projects/CHAT-P1/CHAT-P1.md`.

The rendered card hierarchy is:

```text
SET THE CAPTURE DIRECTORY
Choose where ChatMD saves captures.
export CHATMD_CAPTURE_ROOT=
"/path/to/captures"
Set it once, then run chatmd from anywhere.
MORE ON GITHUB
[loneborz/chatmd]
```

The export command `textContent` remains
`export CHATMD_CAPTURE_ROOT="/path/to/captures"`. The path is a
`.cmd-path` block so the wrap is a designed two-line command. Setup
copy and the GitHub cluster are separate groups (`install-note-setup`
and `install-note-more`). CTA destination and label are unchanged.
Hero, Config row, numbered install steps, README, product files,
tests, and assets are unchanged. CHAT-14 was not reopened.

## Verification

No prepared LWA GO run exists for CHAT-15. Closeout uses the copy
contract, `git diff --check`, authority render/validate, and live
onepager wrap inspection. Unittest, pyright, and ruff are not required
because no product files changed.

Recorded local verification:

- live card at 1280px, 768px, and 375px: no horizontal overflow;
- command wrap is a two-line `.cmd-path` block at all three widths;
- grouping gaps: heading-to-lede 10px, lede-to-command 14px,
  command-to-closer 12px, closer-to-GitHub 28px, label-to-CTA 10px;
- GitHub CTA href `https://github.com/loneborz/chatmd`, label
  `loneborz/chatmd`;
- `git diff --check` - passed, exit 0;
- `lwa render` / `lwa validate` - ChatMD authority root valid.

Impeccable layout detect reported pre-existing cramped-padding warnings
on hero, band, and pipeline containers. None were in the install aside.
They were left unchanged as out of scope.

No public conversation body, share identifier, credential, cookie, or
signed URL is retained in tracked evidence.

## Human acceptance

Accepted at `2026-09-20T14:11:28Z` as complete for the CHAT-15
revision 1 boundary.

The human operator specified the rendered hierarchy, authorized the
smallest necessary CSS and markup for readability, and explicitly
granted acceptance of CHAT-15 together with authority reconciliation,
commit of the CHAT-15 change set, and push to `origin/main`.

## Disposition

`CHAT-15` is completed.

The existing capture-root card is easier to scan: short explanation,
intentional two-line export command, closer, then a GitHub cluster.
CHAT-13/CHAT-14 meaning is preserved. The wider install section, hero,
Config row, and product behavior are unchanged.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-15`
- Kind: `issue`
- Status: `done`
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
