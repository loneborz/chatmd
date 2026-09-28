<!-- lwa:meta
{
  "id": "CHAT-21",
  "kind": "issue",
  "title": "Project anchored URL references in ChatGPT share text",
  "authority": "local-native",
  "revision": 2,
  "status": "done",
  "created_at": "2026-09-28T23:25:16Z",
  "updated_at": "2026-09-28T23:40:33Z",
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
# Project anchored URL references in ChatGPT share text

## Outcome

ChatMD preserves the reader-visible Markdown projection of the newly observed
ChatGPT public-share `content_reference.type == "url"` construct without
weakening fail-visible handling for other unknown anchored reference types.

## New upstream evidence

A current public ChatGPT share exposed four reader-visible `url` references
with the same structure. Observed fields included `matched_text`,
`start_idx`, `end_idx`, `alt`, `safe_urls`, `refs`, `title`, `prompt_text`,
`item`, `layout`, and `logo`. The `matched_text` contained ChatGPT private-use
marker syntax. Each source-provided `alt` was a complete Markdown link. A
temporary patch to an installed package copy projected the anchored `alt` and
successfully completed capture. That experiment is supporting evidence, not
the repository implementation or a replacement for these tests.

No share URL, conversation body, share identifier, or upstream payload is
retained in this Work or its tests.

## Governing authority / source of truth

CHAT-P1 defines the local-first boundary, preservation invariant, and
fail-visible behavior. CHAT-D1 governs canonical conversation content,
visible parts, citations, and deterministic projection semantics.

CHAT-3 established citation handling for the then-evidenced
`grouped_webpages` structure and fail-visible behavior for other anchored
reference types. This Work records a narrow compatibility extension based on
new upstream evidence discovered after CHAT-3. It supersedes that generic
unknown-reference treatment only for `content_reference.type == "url"` as
defined here. It does not reopen or revise the historical scope of CHAT-3 or
CHAT-4.

For this construct, `matched_text` is ChatGPT source encoding with private-use
marker syntax, not the desired standalone human-readable Markdown projection.
The exact non-empty `alt` string is the source-provided reader projection for
that anchored range. This range projection does not make `url` a canonical
`grouped_webpages` citation and does not change CHAT-D1 citation semantics.

The current `chatmd.py` and `test_chatmd.py` implementation are the technical
source of truth for parser behavior and regression structure. The repository
must not depend on the temporary installed-package patch.

## Scope

- Recognize only the evidenced `url` reference type as a supported anchored
  reader-visible source construct.
- Validate its anchor with the existing `_reference_anchor()` behavior.
- Require `alt` to be present as a non-empty string. Missing, non-string, or
  empty `alt` is malformed and fails visibly. Preserve every accepted `alt`
  string exactly, without trimming, rewriting, Markdown reparsing, or URL
  normalization.
- Replace exactly the validated anchored range with that `alt` string in the
  existing text-part projection. Preserve ordinary source text outside the
  range byte-for-byte and keep multiple references in source order.
- Treat this `url` projection as handled when normalizing canonical citations;
  do not create citation metadata for it.
- Keep all other unknown anchored visible reference types fail-visible.
- Preserve deterministic output and existing `grouped_webpages`, `file`,
  `hidden`, and `followup_a` behavior.

The projection must not select or synthesize a destination from `safe_urls`,
`item.url`, `refs`, or other fields. It uses the exact source-provided `alt`
only.

## Non-goals

Do not:

- generalize support to other reference or citation types;
- reinterpret `url` as `grouped_webpages` or emit `Citation` values for it;
- choose among `safe_urls`, parse a destination from `item.url`, or construct
  a replacement URL;
- change `_reference_anchor()` semantics;
- change CHAT-D1, CHAT-3, CHAT-4, or unrelated parser and capture behavior;
- retain live share identifiers, conversation bodies, or upstream payloads;
- modify or rely on an installed site-packages copy;
- commit or push the implementation.

## Evidence requirements

Privacy-safe synthetic tests must establish:

- an anchored `url` reference projects the exact source-provided `alt` at the
  correct position;
- ordinary text before and after the anchor is unchanged;
- multiple `url` references preserve source order;
- missing, empty, and non-string `alt` values fail visibly;
- malformed and mismatched anchors fail visibly through the existing anchor
  validation;
- `url` creates no grouped citation metadata;
- another unknown anchored type still fails visibly;
- existing `grouped_webpages`, `file`, `hidden`, and `followup_a` behavior
  remains covered and unchanged.

Run the repository-required checks:

- `python3 -m unittest -v`;
- `npx --yes pyright`;
- `uvx ruff check .`;
- `git diff --check`;
- `lwa render` and `lwa validate` for the authority tree.
- failed persistence leaves no partial Markdown output.

After the synthetic tests and quality gates pass, perform one live end-to-end
capture against the known failing public share if its URL is available at
execution time and network access permits. Use the URL only ephemerally. Do
not retain the URL, conversation body, identifiers, or payload in tracked
files, command logs committed as evidence, or test data. Confirm successful
parsing and complete Markdown capture, with all observed URL references
projected as Markdown links and no private-use marker text or partial
successful-looking output.

## Implementation evidence

- `chatmd.py` adds an exact anchored `alt` replacement for `url` references
  and keeps `url` out of canonical citation metadata. Unknown anchored types
  retain their fail-visible behavior.
- `test_chatmd.py` adds synthetic coverage for exact projection, surrounding
  Unicode text, multiple references, invalid `alt` values, and malformed
  anchors. Existing reference-type and no-partial-write tests remain in the
  suite.
- `python3 -m unittest -v`: 68 tests passed.
- `npx --yes pyright`: passed with 0 errors, 0 warnings, and 0 informations.
- `uvx ruff check .`: passed.
- `git diff --check`: passed.
- `test_writer_publishes_no_partial_file_on_failure` passed in the full suite.
- A live end-to-end run through the repository implementation completed with
  exit status 0 and one `CAPTURE COMPLETE` result. The captured Markdown
  contained all four exact source-provided `alt` links, no corresponding
  private-use markers, no URL citation metadata, and unchanged source text
  outside the projected ranges. No partial temporary files were present.
- The live URL, conversation body, identifiers, and payload were held only
  ephemerally. The captured Markdown and temporary output directory were
  removed after inspection.
- `lwa render` and `lwa validate` passed after the Work was created. They are
  rerun after this evidence and status update.
- The reviewed local diff contains only this Work, its rendered CHAT-P1 and
  CHAT-D1 navigation, `chatmd.py`, and `test_chatmd.py`. CHAT-3 and CHAT-4
  remain unchanged. No commit or push was made.

## Acceptance criteria

- [x] Only the evidenced anchored `url` reference type receives the
      source-provided `alt` projection.
- [x] Anchors pass the existing `_reference_anchor()` validation.
- [x] Missing, empty, non-string, or otherwise malformed `alt` data fails
      visibly.
- [x] The exact accepted `alt` string replaces only its anchored range.
- [x] Text outside anchored ranges is unchanged, including with multiple
      references in one message.
- [x] `url` does not become `grouped_webpages` citation metadata and no
      destination is selected or synthesized from other fields.
- [x] Unknown anchored visible reference types continue to fail visibly.
- [x] Existing `grouped_webpages`, `file`, `hidden`, and `followup_a` behavior
      remains unchanged.
- [x] Privacy-safe synthetic regression tests and all required repository
      checks pass.
- [x] Persistence failure leaves no partial Markdown output.
- [x] Live end-to-end validation is performed if the known share URL is
      available and network access permits, without retaining private or
      share-specific data.
- [x] The intended diff contains no unrelated changes.
- [x] The owner authorized updating CHAT-21 status after live validation
      passed.

## Human acceptance

The owner directed that CHAT-21 evidence and status be updated if live
validation passed. Live validation passed, so this explicit conditional
authorization was fulfilled. CHAT-21 is marked done. Commit and push remain
unauthorized.

## Completion boundary

CHAT-21 is complete when the narrow `url` projection is implemented and
verified, all other unknown anchored visible reference types remain
fail-visible, privacy-safe tests and required checks pass, live validation is
recorded if it is possible without retaining sensitive data, the intended
diff is reviewed, and a human accepts the result.

Do not mark this Work done, check human-accepted criteria, reconcile its
implementation, commit, or push unless a later human decision explicitly
authorizes those actions.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-21`
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
