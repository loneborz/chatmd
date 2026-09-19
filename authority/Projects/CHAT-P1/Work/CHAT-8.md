<!-- lwa:meta
{
  "id": "CHAT-8",
  "kind": "issue",
  "title": "Make ChatMD a normal local CLI command",
  "authority": "local-native",
  "revision": 3,
  "status": "done",
  "created_at": "2026-09-19T16:14:44Z",
  "updated_at": "2026-09-19T16:39:30Z",
  "owner": {
    "kind": "project",
    "id": "CHAT-P1"
  },
  "relations": []
}
-->
# Make ChatMD a normal local CLI command

## Outcome

ChatMD can be invoked as `chatmd <share-url>` from a normal shell without
manually invoking the Python source file.

After one intentional local installation or setup step, the user can run:

```sh
chatmd https://chatgpt.com/share/...
```

from a normal shell and from directories outside the ChatMD repository. The
documented Quick start uses that invocation. `chatmd --help` behaves as a
normal CLI command. Shell quotes are not part of ChatMD syntax and are not
required in examples unless the URL itself needs quoting.

## Governing authority / source of truth

CHAT-P1 defines the product purpose, local-first boundary, no-rewrite
invariant, and the primary interface `chatmd <share-url>`.

Accepted CHAT-5 defines the reliable local capture workflow. Accepted CHAT-6
documents the previously accepted public product state, including the
unpackaged `python3 chatmd.py` invocation. Accepted CHAT-7 defines the
post-capture shared-link security result that this Work must preserve.

The current `chatmd.py` and `test_chatmd.py` implementation are the technical
source of truth for capture, CLI argument handling, and success or failure
output. Repository inspection before this Work found a one-file
implementation with `argparse.ArgumentParser(prog="chatmd")` and `main()`,
and no package metadata, console-script entrypoint, or install command.

CHAT-D1 does not govern this Work because CHAT-8 does not change portable
bundle semantics, content identity, serialization, or the interchange
contract.

The repository implementation, tests, documented install command, and
observable `chatmd` command result are the technical source of truth after
implementation. Human acceptance remains a separate authority decision.

## Scope

Introduce the smallest robust local CLI installation and entrypoint mechanism
that places a real `chatmd` executable on PATH without hardcoding this
machine's repository path into product behavior.

Inspected implementation decision:

- Keep the existing one-file `chatmd.py` capture implementation as the
  underlying behavior, including `main()`.
- Add a minimal PEP 621 `pyproject.toml` that installs ChatMD as a
  one-module Python project and exposes the console-script entrypoint
  `chatmd = "chatmd:main"`.
- Do not introduce a src layout, lockfile, extras, plugin system, or other
  packaging architecture beyond that entrypoint.
- Document one local install command, run from a ChatMD checkout:

```sh
uv tool install .
```

That command is the chosen setup step because this machine already has `uv`,
does not have `pipx`, already uses `uvx` for repository quality checks, and
already has `~/.local/bin` on PATH. The installed command is a copy of the
package at install time and must not remain coupled to live repository source
files. Product source must not embed this machine's repository path.

Also required:

- Keep the existing ChatMD capture implementation as the underlying behavior.
- Make the installation and setup path explicit and reproducible in
  `README.md`.
- Update `README.md` so Quick start reflects the real accepted invocation
  `chatmd <share-url>`, without presenting `python3 chatmd.py` as the normal
  way to run ChatMD.
- Test the installed or entrypoint behavior appropriately, including
  `chatmd --help` and invocation from a working directory outside the
  repository.
- Preserve the existing CHAT-7 post-capture security result.
- Ignore generated packaging artifacts so they do not become product source.

## Non-goals

Do not:

- implement a browser extension, macOS Shortcut, or menu bar UI;
- add Homebrew distribution unless the chosen PATH mechanism clearly
  requires it, which the inspected `uv tool` path does not;
- publish ChatMD to a public package index or add release automation;
- automatically revoke shared links;
- capture authenticated or private ChatGPT conversations;
- eliminate the public share flow;
- change parsing, serialization, collision, capture-root, or CHAT-D1 bundle
  semantics;
- change the CHAT-7 post-capture security result;
- add capture-root configuration, image downloading, or unrelated cleanup.

## Evidence requirements

- Focused tests prove `chatmd --help` behaves as a normal CLI command.
- Tests prove the installed or generated `chatmd` entrypoint can be invoked
  from a working directory outside the ChatMD repository.
- Existing capture and workflow tests continue to pass, including the CHAT-7
  post-capture security result.
- The documented install command is exercised once as local verification.
- After that install, `chatmd --help` is invoked from a directory outside
  the repository.
- `python3 -m unittest -v` passes.
- `npx --yes pyright` passes.
- `uvx ruff check .` passes.
- `git diff --check` passes.
- Local-native render and validate pass for the authority-only baseline
  before execution. After implementation they are not required to reconcile
  this Work.

Do not retain public conversation bodies, share identifiers, credentials,
cookies, or signed URLs in tracked evidence.

## Acceptance criteria

- [x] After the documented local install command, `chatmd` is a real
      executable available from a normal shell.
- [x] `chatmd https://chatgpt.com/share/...` is the documented normal
      invocation and does not require manually running `python3 chatmd.py`.
- [x] `chatmd` can be invoked from a directory outside the ChatMD
      repository.
- [x] `chatmd --help` behaves as a normal CLI command.
- [x] README Quick start matches the accepted `chatmd` invocation and states
      the exact install command.
- [x] Shell quotes are not required in documented examples unless the URL
      itself needs quoting.
- [x] The existing capture implementation remains the underlying behavior.
- [x] The CHAT-7 post-capture security result is unchanged.
- [x] Parsing, serialization, collision, capture-root, and CHAT-D1 bundle
      semantics are unchanged.
- [x] Product source does not hardcode this machine's repository path.
- [x] Focused tests, the complete test suite, `npx --yes pyright`,
      `uvx ruff check .`, and `git diff --check` pass, with failures and
      limitations reported honestly.
- [x] A human accepts the resulting install and invocation behavior against
      this Work contract.

## Completion boundary

CHAT-8 is complete when the documented local install step makes `chatmd`
invocable from a normal shell and from outside the repository, README Quick
start matches that invocation, the required verification passes, and a human
accepts the behavior.

Do not mark this Work done, check human-accepted criteria, reconcile
authority, commit the implementation, or push unless a later human decision
explicitly authorizes that action.

## Implementation evidence

The accepted product implementation is the tracked diff on authority baseline
`402bb91cd80af0d16ac21ae10d245203bdbf1cc7`. It changes exactly:

- `.gitignore`;
- `README.md`;
- `chatmd.py`;
- `pyproject.toml`;
- `test_chatmd.py`.

A minimal PEP 621 `pyproject.toml` installs ChatMD as a one-module project and
exposes the console-script entrypoint `chatmd = "chatmd:main"`. The accepted
local setup command is the non-editable install:

```sh
uv tool install .
```

After that install, `chatmd <share-url>` is the normal invocation from any
directory, including outside the repository. `chatmd --help` behaves as a
normal CLI command. The installed module loads from the uv tool environment
and not from the ChatMD repository checkout. Product source does not hardcode
this machine's repository path.

`chatmd.py` keeps the existing capture implementation, including `main()` and
the CHAT-7 post-capture security result. The only `chatmd.py` source change is
a behavior-preserving `timezone.utc` to `datetime.UTC` alias required after
declaring `requires-python = ">=3.11"`. README Quick start documents
`uv tool install .` and unquoted `chatmd https://chatgpt.com/share/<public-share-id>`.

No browser extension, macOS Shortcut, menu bar UI, Homebrew distribution,
public package publishing, automatic share revocation, private capture, or
CHAT-D1 bundle change was introduced. Parsing, serialization, collision,
capture-root, and CHAT-D1 bundle semantics were not changed.

## Verification

Accepted LWA execution is replacement run
`go-20260919T162630.723585000Z-b1b9bf601d57588d`, frozen against CHAT-8
revision 2. The run finalized with disposition `completed` by executor
`cursor-grok-4.6-extra-high`. Starting and resulting HEAD before the
completion commit remained `402bb91cd80af0d16ac21ae10d245203bdbf1cc7`.

The superseded revision-1 run
`go-20260919T161540.026473000Z-8ca89802aa6e0366` is historical evidence of the
rejected editable install model. It is not evidence for this accepted result.

All eight recorded verification attempts exited 0:

- `python3 -m unittest -v` - exit 0 at `2026-09-19T16:26:58Z` (44 tests,
  including the CHAT-7 post-capture security result);
- `npx --yes pyright` - exit 0 at `2026-09-19T16:27:01Z`;
- `uvx ruff check .` - exit 0 at `2026-09-19T16:27:01Z`;
- `git diff --check` - exit 0 at `2026-09-19T16:27:01Z`;
- `uv tool install --reinstall .` - exit 0 at `2026-09-19T16:27:02Z`;
- `cd /tmp && command -v chatmd && chatmd --help` - exit 0 at
  `2026-09-19T16:27:02Z`;
- `chatmd not-a-url` from `/tmp` reached the normal CLI validator with exit 2
  and `expected an absolute HTTP(S) share URL` - recorded wrapper exit 0 at
  `2026-09-19T16:27:02Z`;
- from `/tmp`, the loaded module was under
  `~/.local/share/uv/tools/chatmd/` and not the repository checkout, with no
  `Editable project location` - exit 0 at `2026-09-19T16:27:04Z`.

No retained run bundle was added because CHAT-8 does not require durable
retained evidence.

## Human acceptance

Accepted at `2026-09-19T16:39:30Z` as complete for the CHAT-8 revision 2
boundary.

The human operator explicitly granted acceptance of CHAT-8 revision 2 and
authorized end-to-end finalization. The accepted result is one local setup
command `uv tool install .`, normal usage `chatmd <share-url>`,
`chatmd --help` as a normal CLI, a non-editable installed tool that loads from
the uv tool environment rather than the repository checkout, and unchanged
ChatMD capture behavior including the CHAT-7 post-capture security output.

## Disposition

`CHAT-8` is completed.

ChatMD is invocable as a normal local `chatmd` command after one non-editable
`uv tool install .` step. Capture behavior, including CHAT-7 post-capture
security output, remains intact. Browser extensions, Shortcuts, Homebrew
distribution, public publishing, automatic revocation, private capture, and
CHAT-D1 bundle work remain outside this Work.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-8`
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
