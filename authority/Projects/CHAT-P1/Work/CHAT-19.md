<!-- lwa:meta
{
  "id": "CHAT-19",
  "kind": "issue",
  "title": "Bound external network waits during capture",
  "authority": "local-native",
  "revision": 1,
  "status": "active",
  "created_at": "2026-09-23T16:24:00Z",
  "updated_at": "2026-09-23T16:24:00Z",
  "owner": {
    "kind": "project",
    "id": "CHAT-P1"
  },
  "relations": []
}
-->
# Bound external network waits during capture

## Outcome

ChatMD must never wait indefinitely on an external HTTP request during a
capture.

A stalled ChatGPT share fetch, asset-resolution request, or resolved asset
download must terminate within a bounded period and fail clearly. This must
preserve ChatMD's existing source-fidelity and strict image-preservation
contract: a supported visible image that cannot be preserved still makes the
capture fail rather than producing incomplete Markdown.

This Work also determines, from evidence, whether the observed image-capture
hang is caused only by unbounded request behavior, by a changed upstream
ChatGPT asset flow, or by both. Do not treat an upstream change as established
unless investigation demonstrates it.

## Governing authority / source of truth

CHAT-P1 defines ChatMD as a small local-first conversion core that uses
ordinary HTTP, keeps fetching, parsing, asset acquisition, and serialization
as separate boundaries, preserves source-authored content, and fails clearly
when source content cannot be represented faithfully.

Accepted CHAT-5 defines reliable fail-visible capture and persistence.
Accepted CHAT-10 defines strict preservation of supported share-visible images
through one cookie-aware capture session. CHAT-10 explicitly requires backend
resolution failure, blob download failure, and unpreserved visible images to
fail the capture rather than publish misleading Markdown.

The current `chatmd.py`, `test_chatmd.py`, repository documentation, and
observable `chatmd` command behavior are the technical source of truth for
the current implementation. Human acceptance remains a separate authority
decision.

## Observed failure

On 2026-09-23, the installed `chatmd` CLI was run against a current public
ChatGPT share containing visible images and appeared to hang indefinitely.

Interrupting the process with Ctrl+C exposed execution blocked in the image
download path:

```text
acquire_images()
  -> session.get_bytes(download_url)
  -> ShareSession._request()
  -> self._open(request)
  -> urllib HTTPS/socket read
```

The current request boundary is:

```python
with self._open(request) as response:
    return response.read(), response.headers
```

No explicit bounded timeout is passed at that boundary.

The observed traceback proves that the process can remain blocked in an
external network read until interrupted. It does not by itself prove that
OpenAI or ChatGPT changed the upstream asset contract.

## Scope

Investigate and correct the unbounded external-request behavior on the normal
ChatMD capture path.

The investigation must determine, as far as available evidence allows, whether
the observed failure is:

1. missing or ineffective request timeout behavior only;
2. a changed ChatGPT asset-resolution or asset-download flow;
3. both; or
4. still uncertain after bounded investigation.

Implement the smallest robust correction supported by that evidence.

Required behavior:

- External HTTP operations used by normal capture have an explicit bounded
  failure path.
- A stalled request does not wait indefinitely.
- Timeout and expected network failures are converted into clear ChatMD
  failures instead of leaking an unhandled Python traceback during normal CLI
  use.
- Existing phase boundaries remain understandable. A failure should identify
  the relevant capture phase closely enough to distinguish share fetch, asset
  resolution, and asset download when the implementation can do so without
  unnecessary redesign.
- Strict image preservation remains unchanged. A supported visible image that
  cannot be preserved still fails the capture.
- Failed acquisition must not publish successful-looking or incomplete
  Markdown and must not print `CAPTURE COMPLETE`.
- Existing successful text-only and image-containing captures remain
  behaviorally compatible except for the new bounded network semantics.
- If investigation demonstrates an upstream ChatGPT contract change, adapt
  only the affected compatibility boundary and record the evidence for that
  conclusion.

The exact timeout value and whether one timeout or a small set of
phase-specific timeout values is appropriate are implementation decisions.
Choose the smallest design that is easy to reason about, test, and maintain.

## Non-goals

Do not:

- silently skip failed visible images;
- introduce best-effort capture as the default;
- weaken CHAT-10 source-fidelity or image-preservation guarantees;
- introduce browser automation;
- replace the Python standard-library HTTP approach without evidence that it
  is required;
- redesign unrelated parser, model, serialization, persistence, CLI, or
  capture-root behavior;
- add generalized retry, backoff, resilience, telemetry, or networking
  frameworks unless the observed failure demonstrates that they are required;
- add file-attachment downloading;
- implement CHAT-D1 portable bundle scope;
- retain public conversation bodies, share identifiers, cookies, credentials,
  backend download URLs, or short-lived signed asset URLs in tracked tests,
  fixtures, authority, or evidence;
- claim that a ChatGPT update caused the incident unless investigation
  demonstrates it.

## Evidence requirements

Add focused deterministic regression coverage for the discovered failure mode.

At minimum, tests must establish:

- a stalled or timed-out external request returns control within the test's
  bounded expectation rather than hanging;
- the timeout is translated into the intended ChatMD failure semantics;
- the normal CLI failure path remains non-zero and does not emit
  `CAPTURE COMPLETE`;
- image acquisition remains strict after timeout handling is introduced;
- existing backend resolution and blob-download failure behavior remains
  covered;
- successful mocked requests continue to work;
- text-only captures remain unchanged;
- tests do not depend on live ChatGPT availability;
- tracked tests and fixtures contain no real share identifiers, cookies,
  credentials, backend URLs tied to a live share, or signed asset URLs.

Where implementation-specific seams make it useful, cover both connection or
open failure and blocking read or timeout behavior. Do not overfit tests to a
single exception class if Python's stdlib can surface equivalent timeout
conditions through more than one documented path.

Run the repository quality gate:

- `python3 -m unittest -v`;
- `npx --yes pyright`;
- `uvx ruff check .`;
- `git diff --check`;
- local-native authority render and validate.

If safe and useful, perform one end-to-end capture against a disposable public
ChatGPT share containing at least one supported visible image after automated
verification. Any share URL and derived signed asset URL are runtime-only
evidence and must not be committed or retained in tracked authority.

## Acceptance criteria

- [ ] No external HTTP request on the normal ChatMD capture path can block
      indefinitely under the supported runtime model.
- [ ] A stalled request terminates through an explicit bounded failure path.
- [ ] Timeout and expected network failures produce a clear ChatMD error and a
      non-zero CLI result rather than requiring Ctrl+C.
- [ ] Normal timeout or network failure handling does not expose an unhandled
      Python traceback to the user.
- [ ] Failure reporting identifies the relevant capture phase closely enough
      to distinguish share fetch, image backend resolution, and image download
      where those phases are separately known.
- [ ] A supported visible image remains mandatory for a successful faithful
      capture.
- [ ] Failed image acquisition does not produce `CAPTURE COMPLETE`, a
      misleading final Markdown capture, or silently omitted visual evidence.
- [ ] Existing successful text-only capture behavior remains unchanged.
- [ ] Existing successful supported-image capture behavior remains unchanged
      apart from bounded network behavior.
- [ ] Investigation records whether an upstream ChatGPT behavior change was
      demonstrated, not demonstrated, or remains uncertain.
- [ ] Any upstream compatibility change is limited to the affected boundary
      and is backed by evidence.
- [ ] Deterministic regression coverage includes a stalled or timed-out
      request without depending on live ChatGPT.
- [ ] Existing relevant image-resolution and blob-download failure tests
      remain green.
- [ ] No public conversation body, live share identifier, credential, cookie,
      or signed asset URL is retained in tracked evidence or fixtures.
- [ ] `python3 -m unittest -v`, `npx --yes pyright`,
      `uvx ruff check .`, and `git diff --check` pass.
- [ ] Local-native authority render and validate pass.
- [ ] The complete intended diff contains no unrelated scope.
- [ ] A real end-to-end image capture is verified when safely possible after
      implementation.
- [ ] A human accepts the resulting runtime behavior against this Work
      contract.

## Completion boundary

CHAT-19 is complete only when the root cause has been investigated and reported
without overstating certainty, external network waits on the supported capture
path are bounded, timeout and expected network failures are fail-visible,
strict image preservation remains intact, regression and repository quality
checks pass, and a human accepts the resulting behavior.

Implementation or passing tests alone do not complete this Work.

Do not mark this Work done, check human-accepted criteria, reconcile authority,
commit implementation, or push implementation unless a later human decision
explicitly authorizes those actions.
