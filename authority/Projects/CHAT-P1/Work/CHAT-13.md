<!-- lwa:meta
{
  "id": "CHAT-13",
  "kind": "issue",
  "title": "Make the ChatMD capture root portable across machines",
  "authority": "local-native",
  "revision": 3,
  "status": "done",
  "created_at": "2026-09-20T12:27:26Z",
  "updated_at": "2026-09-20T13:00:20Z",
  "owner": {
    "kind": "project",
    "id": "CHAT-P1"
  },
  "relations": []
}
-->
# Make the ChatMD capture root portable across machines

## Outcome

ChatMD must not require a machine-specific or vault-specific capture
destination to be encoded in application code.

The same installed `chatmd` command must be usable when the capture root
lives somewhere else on another machine, without editing product source and
without reinstalling just to change that destination.

This Work does not change what ChatMD captures. It changes only how the local
capture directory is chosen, so that choice is supplied at runtime from
outside product source.

Revision 2 is a human owner product-boundary correction. Revision 1 still
bound the default destination to `My vault/Sources/ChatMD` under the current
user's home directory. That remains too specific: it removes only the
`/Users/marwan` prefix and still embeds a vault name and vault-relative
layout in ChatMD.

## Governing authority / source of truth

CHAT-P1 defines the product purpose, local-first boundary, no-rewrite
invariant, and the primary interface `chatmd <share-url>`. ChatMD must stay
independent of Context World, Obsidian, and other consumers. This Work
preserves that interface, the accepted zero-argument clipboard path, and
that consumer independence.

Accepted CHAT-5 defines reliable local capture: year and month directories
from the local capture date, atomic publish, collision-safe filenames,
rejection of contentless exports, and reporting of the exact final path.
CHAT-5 also recorded this operator's then-current vault path and left
generalized storage configuration out of that Work. This Work does not
reopen CHAT-5's reliability contract. The CHAT-5 path was that Work's local
destination, not a permanent product default that later machines must share.

Accepted CHAT-8 defines the normal installed command and the non-editable
`uv tool install .` setup step. Because that install copies product source
at install time, a destination constant inside `chatmd.py` cannot be changed
on another machine without editing source and reinstalling. This Work must
remove that requirement. It does not reopen the CHAT-8 install model.

Accepted CHAT-9 requires clipboard and explicit invocation to share the same
write path after a source URL is resolved. This Work must keep that shared
path and must not make clipboard capture depend on a different destination
rule.

Accepted CHAT-6 and CHAT-12 document the current machine-specific capture
root. This Work does not reopen those documentation contracts. It may update
`README.md` so the accepted product state is no longer described as requiring
a source edit and reinstall to use a different capture root.

The current `chatmd.py` and `test_chatmd.py` implementation are the technical
source of truth for capture, CLI argument handling, and destination
behavior. Repository inspection before this Work found:

- `CAPTURE_ROOT` is a module-level absolute path
  `Path("/Users/marwan/My vault/Sources/ChatMD")`;
- `write_markdown(...)` already accepts an optional `capture_root` used by
  tests, and `_capture_directory(...)` already prefers that argument over
  `CAPTURE_ROOT`;
- `main()` never passes `capture_root`, so every CLI capture uses the
  hardcoded constant;
- `WorkflowTests.test_default_capture_root_is_the_authorized_vault_path`
  asserts that exact `/Users/marwan/...` value;
- `argparse` exposes only an optional positional share URL;
- product code has no runtime source for a capture destination outside that
  constant;
- README currently tells another machine to change `chatmd.py` and
  reinstall, and lists portable capture-root configuration as a current
  limitation;
- README also documents that `chatmd` is invoked from any directory, so the
  capture root is a stable destination rather than the current working
  directory.

CHAT-D1 remains the active portable bundle contract. The current output does
not implement it. CHAT-D1 does not govern this Work because this Work does
not change portable bundle semantics, content identity, serialization, or
the interchange contract.

The repository implementation, tests, documented destination behavior, and
observable `chatmd` command result are the technical source of truth after
implementation. Human acceptance remains a separate authority decision.

## Scope

Stop encoding the capture destination in product source. Resolve it at
runtime from outside that source, then reuse the existing writer.

Required product boundary:

- Product source must not contain a machine-absolute capture path.
- Product source must not contain a vault name or vault-relative filesystem
  layout used as the capture destination.
- The same installed command must be able to capture into different capture
  roots without editing product source and without a destination-driven
  reinstall.
- `chatmd` and `chatmd <share-url>` remain the normal invocations. This Work
  must not make a destination into a required extra share-URL-style
  positional argument, and must not make capture depend on the current
  working directory.
- If a capture root cannot be resolved, fail clearly with a non-zero status,
  write no capture, and do not emit `CAPTURE COMPLETE` or the CHAT-7
  security result.
- Keep YYYY/MM routing, directory creation, collision behavior, atomic
  publish, contentless rejection, image-sidecar placement, and the CHAT-7
  successful post-capture security result unchanged under whatever root is
  resolved.
- Pass the resolved root into the existing
  `write_markdown(..., capture_root=...)` parameter. Do not duplicate
  writer, collision, or success-output logic.
- Keep the runtime implementation in the Python standard library.
- Do not discover Obsidian vaults, scan the filesystem for a vault name, or
  otherwise couple ChatMD to a consumer's storage layout.
- This operator must still be able to send captures to the existing local
  vault. That location may be supplied at runtime from outside product
  source; it must not remain compiled into ChatMD.
- Update tests that currently treat `/Users/marwan/My vault/Sources/ChatMD`
  as the only authorized default.
- Update `README.md` so it no longer says another machine must edit
  `chatmd.py` and reinstall to change the capture root, and so it does not
  present a vault-specific layout as product source behavior.
- Because CHAT-8 installs a non-editable copy, reinstall or otherwise
  refresh the installed `chatmd` command as part of verification so the
  verified binary reflects this Work.

The first install or reinstall that ships this Work is expected. After that
install, changing the capture root on this machine or another machine must
not require a further source edit.

This Work authorizes the smallest stdlib-only runtime resolution that
satisfies the boundary above. It does not name or require a particular
mechanism. Implementation inspection after this authority is accepted
chooses that mechanism.

## Non-goals

Do not:

- change ChatGPT share parsing;
- change Markdown serialization;
- change collision, atomic-publish, or contentless-export behavior;
- change CHAT-D1 bundle semantics;
- change the CHAT-7 post-capture security result;
- change clipboard capture except insofar as it continues to use the same
  writer;
- introduce a generalized storage, settings, or plugin framework;
- discover, infer, or hardcode an Obsidian vault or other consumer layout;
- use the current working directory as the capture root;
- add Homebrew distribution, public package publishing, or release
  automation;
- change the CHAT-8 non-editable `uv tool install .` model;
- modify the website;
- reopen CHAT-5, CHAT-6, CHAT-8, CHAT-9, or CHAT-12;
- perform unrelated cleanup.

## Evidence requirements

- Focused tests prove product source does not encode a machine-absolute
  capture path or a vault-specific destination layout.
- Focused tests prove the same installed or in-process `chatmd` behavior can
  capture into two different capture roots without changing product source.
- Tests prove that an unresolvable capture root fails clearly with a
  non-zero status, creates no capture, and does not emit `CAPTURE COMPLETE`,
  `Saved:`, `Shared source:`, or the CHAT-7 security result.
- Existing writer tests continue to pass with an injected capture root,
  including year/month routing, collision preservation, contentless
  rejection, and image-sidecar placement.
- Tests prove `chatmd` and `chatmd <share-url>` remain the capture
  invocations once a capture root is available through the chosen runtime
  resolution.
- README no longer instructs a source edit and reinstall to change the
  capture root, and no longer presents a vault-specific layout as compiled
  product behavior.
- `python3 -m unittest -v` passes.
- `npx --yes pyright` passes.
- `uvx ruff check .` passes.
- `git diff --check` passes.
- Local-native render and validate pass for the authority-only baseline
  before execution.
- Because CHAT-8 installs a non-editable copy, the documented install or
  reinstall is exercised once as local verification of this Work.

Automated filesystem tests must use temporary or isolated directories and
must not write fixtures into this operator's existing vault.

Do not retain public conversation bodies, share identifiers, credentials,
cookies, or signed URLs in tracked evidence.

## Acceptance criteria

- [x] Product source does not encode a machine-specific or vault-specific
      capture destination.
- [x] The same installed ChatMD can capture into a capture root other than
      this machine's current vault path without editing product source and
      without a destination-driven reinstall.
- [x] `chatmd` and `chatmd <share-url>` remain the normal capture
      invocations once a capture root can be resolved.
- [x] An unresolvable capture root fails clearly and writes no capture.
- [x] Year/month routing, collision behavior, atomic publish, contentless
      rejection, image-sidecar placement, clipboard capture, and the CHAT-7
      post-capture security result remain unchanged under the resolved root.
- [x] ChatMD does not discover or depend on an Obsidian vault or other
      consumer storage layout.
- [x] README matches the accepted destination behavior and no longer says
      to edit `chatmd.py` and reinstall to use ChatMD with a different
      capture root.
- [x] Focused tests, the complete test suite, `npx --yes pyright`,
      `uvx ruff check .`, and `git diff --check` pass, with failures and
      limitations reported honestly.
- [x] A human accepts the resulting destination behavior against this Work
      contract.

## Completion boundary

CHAT-13 is complete when the installed `chatmd` command resolves its capture
root at runtime from outside product source, that source no longer encodes a
machine-specific or vault-specific destination, another machine can use a
different capture root without editing product code, the required
verification passes, and a human accepts the behavior.

Do not mark this Work done, check human-accepted criteria, reconcile
authority, commit the implementation, or push unless a later human decision
explicitly authorizes that action.

## Implementation evidence

The accepted product implementation is the local working-tree diff against
HEAD `f2ef19413e83920dc6cc2aca07f679a7a37d9bfa`. It is not yet committed.
The product change is exactly:

- `README.md`;
- `chatmd.py`;
- `test_chatmd.py`.

Authority closeout also changes:

- `authority/Projects/CHAT-P1/Work/CHAT-13.md`;
- render-owned navigation on `authority/Projects/CHAT-P1/CHAT-P1.md`.

Product source no longer contains a machine-absolute capture path or a
vault-specific destination layout. `main()` resolves an absolute capture
root from the process environment variable `CHATMD_CAPTURE_ROOT` after
share-URL validation, then passes that root into
`write_markdown(..., capture_root=...)`. `chatmd` and `chatmd <share-url>`
remain the capture invocations. A missing, empty, or non-absolute value
fails before fetch or write and does not emit `CAPTURE COMPLETE` or the
CHAT-7 security result.

YYYY/MM routing, collision behavior, atomic publish, contentless rejection,
image-sidecar placement, clipboard capture, and the CHAT-7 successful
post-capture security result are unchanged under the resolved root. No
configuration file, settings framework, CLI destination argument, current
working directory default, Obsidian vault discovery, website change, or
CHAT-D1 bundle work was introduced.

README documents `CHATMD_CAPTURE_ROOT` as machine-local runtime input and no
longer says another machine must edit `chatmd.py` and reinstall.

## Verification

No prepared LWA GO run exists for CHAT-13. Closeout uses the repository
quality gate, authority render/validate, installed-command verification,
and the human-observed live capture. Absence of a GO bundle does not
decide acceptance.

Recorded local verification after implementation, re-run at closeout:

- `python3 -m unittest -v` - 62 tests, exit 0;
- `npx --yes pyright` - 0 errors, 0 warnings, 0 informations, exit 0;
- `uvx ruff check .` - all checks passed, exit 0;
- `git diff --check` - passed, exit 0.

Implementation-time installed-command verification, not re-run at
closeout:

- `uv tool install --reinstall .` - installed `chatmd==0.1.0`;
- from `/tmp`, `chatmd --help` names `CHATMD_CAPTURE_ROOT`;
- from `/tmp`, unset `CHATMD_CAPTURE_ROOT` with
  `chatmd https://example.com/share/example` exited 2 with
  `CHATMD_CAPTURE_ROOT is not set` and no `CAPTURE COMPLETE`;
- the installed module resolved `/tmp/chatmd-a` and `/tmp/chatmd-b`
  without a source edit.

Closeout inspection of the accepted live file, without retaining the share
identifier or conversation body, confirmed:

- Markdown
  `/Users/marwan/My vault/Sources/ChatMD/2026/09/Loop Graphs for Agents.md`
  exists, is 8289 bytes, begins with `# Loop Graphs for Agents`, and
  contains a ChatGPT share source line.

No public conversation body, share identifier, credential, cookie, or
signed URL is retained in tracked evidence.

## Human acceptance

Accepted at `2026-09-20T13:00:20Z` as complete for the CHAT-13 revision 2
boundary.

The human operator made `CHATMD_CAPTURE_ROOT` persistent in shell
configuration. A fresh shell resolved:

`/Users/marwan/My vault/Sources/ChatMD`

The operator then ran the normal installed `chatmd` command with a valid
ChatGPT share URL on the clipboard. Capture completed and wrote:

`/Users/marwan/My vault/Sources/ChatMD/2026/09/Loop Graphs for Agents.md`

No destination argument, source edit, or reinstall was required for that
capture. The operator explicitly granted acceptance of CHAT-13 and
authorized authority reconciliation without commit or push.

## Disposition

`CHAT-13` is completed.

The installed `chatmd` command resolves its capture root at runtime from
`CHATMD_CAPTURE_ROOT`. Product source no longer encodes a machine-specific
or vault-specific destination. The same install can capture into a
different root without editing product code. Configuration files, CLI
destination flags, vault discovery, website updates, and CHAT-D1 bundle
work remain outside this Work.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-13`
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
