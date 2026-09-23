# CHAT-19 Findings

## Root cause

The reported hang is explained by missing timeout behavior. The normal CLI
routes share HTML, image backend resolution, and image downloads through
`ShareSession._request()`, which previously called the opener and read the
response without a timeout. The reported stack ended in that response read,
so the existing code allowed an idle socket read to wait until interrupted.

## Upstream behavior

No upstream ChatGPT behavior change was demonstrated. A current public share
with a visible image passed through both the patched source capture and the
installed `chatmd` command, and the image was preserved. This is evidence for
the tested share only, not proof that every upstream asset response is
unchanged. The patch leaves the existing share parser and image-resolution
contract unchanged.

Collision handling passed. No share URL, conversation body, cookie,
credential, backend URL, or signed asset URL is retained here.

## Correction and limits

All `ShareSession` requests, including the standalone `fetch_share()` path,
now pass a 30-second timeout to the standard-library opener. Timeout and
expected network errors become `ParseError` failures. The share fetch reports
its phase directly; image resolution and image download keep their existing
phase-specific failure messages. Required image acquisition still fails the
capture.

The urllib timeout bounds socket inactivity during connection and reads. It
does not impose a total wall-clock deadline on a response that continues
making progress.

The deterministic regression tests use local fixtures and do not depend on
ChatGPT availability. A current public share with a visible image was also
captured during this closeout. Its URL and conversation contents were not
retained.
