<!-- lwa:meta
{
  "id": "CHAT-9",
  "kind": "issue",
  "title": "Capture a copied ChatGPT share from the clipboard",
  "authority": "local-native",
  "revision": 2,
  "status": "done",
  "created_at": "2026-09-19T18:51:00Z",
  "updated_at": "2026-09-19T19:05:05Z",
  "owner": {
    "kind": "project",
    "id": "CHAT-P1"
  },
  "relations": []
}
-->
# Capture a copied ChatGPT share from the clipboard

## Outcome

ChatMD can capture a public ChatGPT share from the macOS clipboard when
invoked with no URL argument.

The intended daily workflow is:

```text
ChatGPT -> Share -> Copy link -> chatmd -> Enter
```

When an explicit URL is supplied:

```sh
chatmd https://chatgpt.com/share/...
```

preserve the current accepted capture path and behavior. Shell quotes remain
outside ChatMD syntax and are not required unless the URL itself needs
quoting. Quote removal is already accepted CHAT-8 behavior and is not new
implementation work.

When no URL argument is supplied:

```sh
chatmd
```

ChatMD must read the current macOS clipboard and use that text as the source
URL only when it is a valid ChatGPT public share link. After the source URL
is resolved, clipboard-driven capture must use the same existing
validation, fetch, parse, write, and success pipeline as explicit
invocation. Do not create a parallel capture implementation.

## Governing authority / source of truth

CHAT-P1 defines the product purpose, local-first boundary, no-rewrite
invariant, and the primary interface `chatmd <share-url>`. This Work
preserves that explicit interface and adds a bounded zero-argument
convenience path.

Accepted CHAT-5 defines the reliable local capture workflow. Accepted CHAT-7
defines the post-capture shared-link security result that this Work must
preserve. Accepted CHAT-8 defines the normal installed command
`chatmd <share-url>` and the non-editable `uv tool install .` setup step.

CHAT-4 excluded clipboard, stdin, stdout, GUI, and multiple-URL modes from
the first end-user workflow. This Work does not reopen CHAT-4. It adds a
later CLI-input convenience on the accepted installed `chatmd` command. It
does not add clipboard output, stdin capture, a GUI, or multiple-URL
processing.

The current `chatmd.py` and `test_chatmd.py` implementation are the technical
source of truth for capture, CLI argument handling, and success or failure
output. Repository inspection before this Work found:

- `main()` uses `argparse.ArgumentParser(prog="chatmd")` with a required
  positional `url` argument whose help text is `one public ChatGPT share URL`;
- `_validate_share_url()` accepts any absolute HTTP(S) URL with a network
  location and does not require a `chatgpt.com/share/...` path;
- `chatmd.main([])` currently fails as missing argparse input with exit
  status 2;
- `WorkflowTests.test_main_rejects_missing_extra_and_invalid_input` currently
  includes `[]` in that missing-input contract;
- `EntrypointTests` currently invoke the installed `chatmd` binary with no
  arguments and expect the same missing-argument failure;
- `test_help_is_a_normal_cli_command` currently asserts the required-URL help
  text;
- product code has no clipboard read, no `pbpaste` invocation, and no
  third-party clipboard dependency;
- the runtime implementation remains one stdlib module with console-script
  entrypoint `chatmd = "chatmd:main"`.

CHAT-D1 does not govern this Work because CHAT-9 does not change portable
bundle semantics, content identity, serialization, or the interchange
contract.

The repository implementation, tests, documented invocation, and observable
`chatmd` command result are the technical source of truth after
implementation. Human acceptance remains a separate authority decision.

## Scope

Add the smallest dependency-free macOS clipboard fallback at the CLI and
input boundary so zero-argument `chatmd` can resolve a copied public ChatGPT
share URL and then reuse the existing capture pipeline.

Inspected implementation direction:

- Keep clipboard resolution at the CLI and input boundary, before
  `parse_share(...)` and `write_markdown(...)`.
- Prefer the native macOS `pbpaste` command invoked through Python
  standard-library subprocess APIs.
- Do not add a third-party clipboard library unless repository evidence
  during implementation demonstrates that the native command is inadequate.
- Do not introduce a GUI, menu bar application, Shortcut, daemon, or
  cross-platform clipboard abstraction.
- After a source URL is resolved, call the same existing capture path used
  by explicit invocation. Do not duplicate fetch, parse, serialize, write,
  collision, or success-output logic.
- Do not read the clipboard when an explicit positional URL was supplied.
- Make the positional URL optional in argparse so `chatmd` and
  `chatmd <share-url>` are both valid invocations.
- Update `chatmd --help` so it clearly communicates both explicit URL
  invocation and zero-argument clipboard behavior.
- Update `README.md` so Quick start documents both invocations without
  presenting quote removal as new work and without changing the CHAT-8
  install command.
- Revise tests that currently treat missing URL input as an argparse-only
  failure, including the workflow missing-input case and the installed
  entrypoint no-argument case.
- Because CHAT-8 installs a non-editable copy, reinstall or otherwise
  refresh the installed `chatmd` command as part of entrypoint verification
  so the verified binary reflects this Work.

Clipboard-mode ChatGPT-share validation may be stricter than the existing
generic explicit URL validator. That distinction exists in the current
code and is authorized here to keep this Work bounded and backward
compatible. Do not tighten or redesign existing explicit URL validation
unless a current repository authority requires it, which inspection did
not find.

## Clipboard contract

For invocation with no URL argument:

- read the macOS clipboard through the native clipboard command;
- normalize only incidental surrounding whitespace needed to interpret
  copied text;
- treat the resulting clipboard contents as the candidate input, not as
  prose to search;
- require that candidate to be one valid public ChatGPT share URL shaped
  as `https://chatgpt.com/share/...`;
- if the clipboard is empty, unavailable, malformed, or not an acceptable
  ChatGPT share URL, fail clearly with a non-zero status;
- do not fetch anything on invalid clipboard input;
- do not write any capture file on invalid clipboard input;
- do not emit `CAPTURE COMPLETE`, `Saved:`, `Shared source:`, or the
  CHAT-7 post-capture security result on failure.

Do not search arbitrary clipboard prose for embedded links. A valid copied
share URL with surrounding whitespace must work. Ordinary HTTP(S) URLs that
are not accepted `chatgpt.com/share/...` clipboard values must fail clearly
in clipboard mode.

## Existing explicit URL compatibility

Preserve:

```sh
chatmd <url>
```

as the explicit and scriptable interface.

Do not access the clipboard when an explicit positional URL was supplied.
Do not remove explicit URL invocation. Do not make clipboard access a
prerequisite for the explicit path.

The current explicit validator remains a generic absolute HTTP(S) URL
check. Clipboard-mode validation may require the stricter
`https://chatgpt.com/share/...` shape. Document that distinction honestly
in help, README, and tests if the implementation keeps it.

## Platform boundary

This Work may introduce macOS-native clipboard fallback for the
zero-argument convenience path only.

Do not turn ChatMD into a GUI. Do not add a large cross-platform clipboard
abstraction. The explicit `chatmd <share-url>` interface must remain
available independently of clipboard convenience, including when the native
clipboard command is missing.

If the native clipboard command is unavailable or the clipboard cannot be
read, fail clearly rather than guessing, substituting another source, or
introducing silent fallback behavior.

## Implementation boundary

Clipboard resolution is authorized only at the CLI and input boundary.

The conversation parser, serializer, writer, collision behavior, capture
root, and CHAT-7 successful post-capture security result must remain
unchanged. CHAT-D1 bundle semantics are unchanged. After URL resolution,
explicit and clipboard invocation must share the same downstream capture
implementation.

## Non-goals

Do not:

- change ChatGPT share parsing;
- change Markdown serialization;
- change collision behavior;
- change capture-root behavior;
- change CHAT-D1 bundle semantics;
- change CHAT-7 post-capture security output;
- download image or file assets;
- add a browser extension;
- add a macOS Shortcut;
- add a menu bar application;
- automatically revoke shared links;
- add clipboard watching or a daemon;
- extract URLs from arbitrary clipboard prose;
- add third-party clipboard dependencies without concrete necessity;
- remove explicit URL invocation;
- redesign packaging or installation;
- perform unrelated cleanup;
- reopen CHAT-4's first-workflow contract;
- treat CHAT-8 quote-free explicit invocation as new work.

## Evidence requirements

- Focused tests prove `chatmd <share-url>` continues through the existing
  explicit invocation path and does not read the clipboard.
- Focused tests prove zero-argument `chatmd` reads isolated clipboard input
  and, when that input is a valid `https://chatgpt.com/share/...` URL, uses
  it as the capture source.
- Tests prove clipboard input is resolved before the existing capture
  pipeline, and that explicit and clipboard invocation share the same
  downstream capture implementation.
- Tests prove surrounding clipboard whitespace does not prevent a valid
  copied share URL from being accepted.
- Tests prove empty clipboard input, non-URL clipboard input, a normal
  HTTP(S) URL that is not an accepted `chatgpt.com/share/...` clipboard
  value, and clipboard-read or missing-native-command failure each fail
  clearly with a non-zero status, create no capture, and do not emit
  `CAPTURE COMPLETE`, `Saved:`, `Shared source:`, or the CHAT-7 security
  result.
- Clipboard tests isolate clipboard input. Do not make correctness depend
  on the operator's live clipboard contents.
- Existing relevant tests continue to pass. Tests that currently encode
  missing-URL argparse failure must be updated to the new zero-argument
  contract rather than preserved as stale requirements.
- `chatmd --help` is verified to describe both explicit URL invocation and
  zero-argument clipboard behavior.
- The installed `chatmd` entrypoint is verified, not only direct
  `chatmd.py` execution.
- Existing CHAT-7 successful post-capture security output remains covered.
- `python3 -m unittest -v` passes.
- `npx --yes pyright` passes.
- `uvx ruff check .` passes.
- `git diff --check` passes.
- Local-native render and validate pass for the authority-only baseline
  before execution. After implementation they are not required to
  reconcile this Work.
- The intended implementation diff is reviewed and contains no unrelated
  scope.

Do not retain public conversation bodies, share identifiers, credentials,
cookies, or signed URLs in tracked evidence.

## Acceptance criteria

- [x] `chatmd https://chatgpt.com/share/...` continues to work through the
      existing explicit invocation path.
- [x] `chatmd` with no positional URL reads the macOS clipboard and uses a
      valid copied `https://chatgpt.com/share/...` URL as the capture
      source.
- [x] Clipboard input is resolved before the existing capture pipeline,
      and explicit and clipboard invocation share the same downstream
      capture implementation.
- [x] An explicit URL never causes clipboard access.
- [x] Surrounding clipboard whitespace does not prevent a valid copied
      share URL from working.
- [x] Empty clipboard input fails clearly with non-zero status and creates
      no capture.
- [x] Non-URL clipboard input fails clearly with non-zero status and
      creates no capture.
- [x] A normal HTTP(S) URL that is not an accepted `chatgpt.com/share/...`
      clipboard value fails clearly and creates no capture.
- [x] Clipboard read failure or an unavailable native clipboard command
      fails clearly and creates no capture.
- [x] Failed clipboard resolution does not emit `CAPTURE COMPLETE`,
      `Saved:`, `Shared source:`, or the CHAT-7 security result.
- [x] Existing CHAT-7 successful post-capture security output remains
      unchanged.
- [x] Existing parser, serializer, writer, collision, and capture-root
      behavior remain unchanged.
- [x] `chatmd --help` clearly communicates both explicit URL invocation
      and zero-argument clipboard behavior.
- [x] README documents both explicit URL invocation and zero-argument
      clipboard capture without presenting quote removal as new work.
- [x] Existing relevant tests continue to pass, with focused tests added
      for clipboard behavior.
- [x] The installed `chatmd` entrypoint is verified, not only direct
      `chatmd.py` execution.
- [x] `python3 -m unittest -v`, `npx --yes pyright`, `uvx ruff check .`,
      and `git diff --check` pass, with failures and limitations reported
      honestly.
- [x] The intended implementation diff contains no unrelated scope.
- [x] Completion state remains explicit and separate from human
      acceptance.
- [x] A human accepts the resulting clipboard and explicit-invocation
      behavior against this Work contract.

## Completion boundary

CHAT-9 is complete when zero-argument `chatmd` captures a valid copied
ChatGPT public share URL through the existing capture pipeline, explicit
`chatmd <share-url>` remains unchanged, invalid clipboard input fails
clearly without fetching, writing, or emitting a successful capture
result, the required verification passes, and a human accepts the
behavior.

Do not mark this Work done, check human-accepted criteria, reconcile
authority, commit the implementation, or push unless a later human
decision explicitly authorizes that action.

## Implementation evidence

The accepted product implementation is the tracked diff on authority
baseline `93d0fb1c53cab200988c0dc82563ee779d9a3ed8`. It changes exactly:

- `README.md`;
- `chatmd.py`;
- `test_chatmd.py`.

`main()` keeps explicit `chatmd <share-url>` on the existing capture path
and does not read the clipboard when a positional URL is supplied. With no
URL argument, it reads the macOS clipboard through native `pbpaste` via
Python standard-library subprocess APIs, trims surrounding whitespace
only, and requires one `https://chatgpt.com/share/...` URL. Query and
fragment components are allowed. Arbitrary clipboard prose is not searched
for an embedded link. Clipboard-mode validation is stricter than the
unchanged generic explicit HTTP(S) URL check.

After URL resolution, both invocation forms call the same
`_validate_share_url()`, `parse_share()`, `write_markdown()`, and CHAT-7
success output. Missing `pbpaste` or a failed clipboard read fails clearly
without fetching or writing a capture.

README Quick start documents both invocations. No browser extension,
Shortcut, menu bar application, clipboard watcher, daemon, third-party
clipboard library, packaging redesign, automatic share revocation, or
CHAT-D1 bundle change was introduced. Parsing, serialization, collision,
capture-root, packaging, and CHAT-7 success output were not changed.

## Verification

Accepted LWA execution is run
`go-20260919T185626.014746000Z-792fd082e0ff79be`, frozen against CHAT-9
revision 1. The run finalized with disposition `completed` by executor
`cursor-grok-4.6`. Starting and resulting HEAD before the completion
commit remained `93d0fb1c53cab200988c0dc82563ee779d9a3ed8`.

Retained evidence is present at
`evidence/runs/go-20260919T185626.014746000Z-792fd082e0ff79be`. Retention
does not decide acceptance.

Recorded verification:

- `python3 -m unittest -v` - exit 0 at `2026-09-19T19:00:02Z` (48 tests,
  including focused clipboard tests and the CHAT-7 post-capture security
  result);
- `npx --yes pyright` - exit 0 at `2026-09-19T19:00:05Z`;
- `uvx ruff check .` - exit 0 at `2026-09-19T19:00:05Z`;
- `git diff --check` - exit 0 at `2026-09-19T19:00:05Z`;
- `uv tool install --reinstall .` - exit 0 at `2026-09-19T19:00:17Z`;
- `cd /tmp && command -v chatmd && chatmd --help` - exit 0 at
  `2026-09-19T19:00:18Z`;
- isolated installed `chatmd` with non-URL clipboard input - exit 0 at
  `2026-09-19T19:00:18Z`;
- installed `chatmd not-a-url` with a failing `pbpaste` on PATH still used
  the explicit validator and did not read the clipboard - exit 0 at
  `2026-09-19T19:00:18Z`;
- first isolated empty-clipboard wrapper - exit 1 at
  `2026-09-19T19:00:18Z` because the wrapper script quoting was wrong, not
  because product behavior failed;
- isolated installed `chatmd` with `https://example.com/share/example` on
  the clipboard - exit 0 at `2026-09-19T19:00:19Z`;
- first missing-`pbpaste` wrapper - exit 1 at `2026-09-19T19:00:19Z`
  because PATH hid `chatmd` itself, not because product behavior failed;
- corrected isolated empty-clipboard installed invocation - exit 0 at
  `2026-09-19T19:00:43Z`;
- corrected installed missing-`pbpaste` invocation - exit 0 at
  `2026-09-19T19:00:43Z`.

No public conversation body, share identifier, credential, cookie, or
signed URL is retained in tracked evidence.

## Human acceptance

Accepted at `2026-09-19T19:05:05Z` as complete for the CHAT-9 revision 1
boundary.

The human operator reviewed the implementation, automated verification,
installed-entrypoint behavior, and a real end-to-end clipboard capture,
then explicitly granted acceptance of CHAT-9 revision 1 and authorized
end-to-end closeout.

The accepted live result is: a ChatGPT share link was copied to the macOS
clipboard, the operator ran only `chatmd`, capture completed, and ChatMD
wrote:

`/Users/marwan/My vault/Sources/ChatMD/2026/09/n8n Development Scale.md`

The CLI reported `CAPTURE COMPLETE` and the expected CHAT-7 shared-link
security warning. Closeout inspection confirmed that file exists as
non-empty Markdown with the expected title heading and a ChatGPT share
source line. The share identifier is not retained here.

## Disposition

`CHAT-9` is completed.

Zero-argument `chatmd` captures a valid copied ChatGPT public share URL
through the existing capture pipeline. Explicit `chatmd <share-url>`
remains unchanged and does not read the clipboard. Invalid clipboard
input fails clearly without fetching, writing, or emitting a successful
capture result. Browser extensions, Shortcuts, menu bar applications,
clipboard watchers, daemons, third-party clipboard libraries, packaging
redesign, automatic revocation, and CHAT-D1 bundle work remain outside
this Work.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-9`
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
