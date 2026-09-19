<!-- lwa:meta
{
  "id": "CHAT-10",
  "kind": "issue",
  "title": "Preserve share-visible images during capture",
  "authority": "local-native",
  "revision": 2,
  "status": "done",
  "created_at": "2026-09-19T21:10:05Z",
  "updated_at": "2026-09-19T21:28:05Z",
  "owner": {
    "kind": "project",
    "id": "CHAT-P1"
  },
  "relations": []
}
-->
# Preserve share-visible images during capture

## Outcome

A successful ChatMD capture of a public ChatGPT share containing a supported
visible user image must preserve the exact share-visible image bytes locally
before the public share can be revoked.

The placeholder `[Image in original conversation]` is no longer a successful
complete capture when the share exposes retrievable visual evidence.

What is preserved is the share-visible image representation. ChatGPT may
sanitize or resize that representation. Original upload bytes are not
guaranteed.

## Governing authority / source of truth

CHAT-P1 defines the product purpose, local-first boundary, no-rewrite
invariant, fail-visible behavior, and Python-stdlib preference.

Accepted CHAT-1 established that public image assets can be resolved through a
fresh anonymous cookie-aware HTTP session. Accepted CHAT-2 retains visible
`image_asset_pointer` parts as structured data. Accepted CHAT-4 serialized
unresolved images as `[Image in original conversation]` and left downloading
outside that Work. Accepted CHAT-5 defines reliable non-overwriting Markdown
persistence. Accepted CHAT-7 defines the post-capture shared-link security
result. This Work must keep that security result truthful: ChatMD still does
not revoke the share.

CHAT-D1 describes a future portable bundle with `manifest.json`, `assets/`,
and content identity. This Work does not implement that bundle and is not
governed by CHAT-D1.

The current `chatmd.py` and `test_chatmd.py` implementation are the technical
source of truth for parsing, serialization, persistence, and CLI behavior.

Live investigation evidence, not retained as tracked artifacts, established
the current public-share image representation and retrieval path:

- visible user images are `image_asset_pointer` objects;
- `asset_pointer` is shaped as
  `sediment://file_<id>?shared_conversation_id=<id>`;
- the object also exposes `size_bytes`, `width`, `height`, and
  `metadata.sanitized == true`;
- matching attachment metadata may expose filename, MIME type, size, width,
  height, and the same file id;
- retrieval uses one cookie-aware stdlib HTTP session for the share fetch and
  `GET https://chatgpt.com/backend-api/files/download/{file_id}?shared_conversation_id={share_id}`;
- a successful JSON response contains a short-lived signed `download_url`;
- that URL is fetched immediately and is not durable evidence;
- backend resolution returned 401 without the share-session cookies;
- the signed blob required no cookies and expired after about five minutes;
- a controlled original PNG of 1206 x 2622 / 144623 bytes appeared in the
  public share as 941 x 2048 / 202545 bytes with `sanitized=true`.

Do not encode the disposable live share identifier into production tests.

The repository implementation, tests, documented behavior, and observable
`chatmd` command result are the technical source of truth after
implementation. Human acceptance remains a separate authority decision.

## Scope

Implement only capture-time preservation of supported visible image assets.

Inspected implementation direction:

- Keep one cookie-aware Python standard-library HTTP session for the capture
  operation only. Do not persist cookies or signed URLs.
- Extend image-pointer extraction so the normalized model retains the
  information required for acquisition: the exact `asset_pointer`, parsed
  file id and shared conversation id, and evidenced size, dimensions,
  filename, and MIME type when present.
- Parse `sediment://file_<id>?shared_conversation_id=<id>` safely and fail
  visibly when the pointer cannot be parsed.
- Resolve each visible image through the evidenced backend download endpoint
  using the same cookies as the share fetch, then immediately fetch the
  signed `download_url`.
- Persist the returned bytes exactly. Do not transcode, resize, strip
  metadata, or optimize images.
- Choose the smallest coherent local representation beside the current
  Markdown capture: a sibling directory named from the published Markdown
  stem plus `-images`, with portable relative Markdown image links at the
  original conversation position. Do not use Obsidian-only syntax.
- Name stored files deterministically and safely. Do not assume the source
  filename is unique. Preserve existing Markdown collision behavior, and do
  not overwrite existing files.
- Once this capability is enabled, a supported visible image that cannot be
  preserved makes the capture fail. Do not publish a successful-looking
  Markdown file that implies the visual evidence was preserved.
- Validate retrieved bytes against evidenced metadata that is actually
  present: size when `size_bytes` or an equivalent matching attachment size
  is present, and PNG dimensions when width or height is present. Do not
  invent validation beyond that evidence.
- Keep text-only captures, file-attachment placeholders, CLI invocation,
  capture-root, and the CHAT-7 post-capture security result unchanged except
  where image persistence requires the Markdown image syntax.
- Update only the documentation that must change so it states that supported
  visible images are preserved locally as the share-visible representation,
  that original upload bytes are not guaranteed, and that file attachments
  remain placeholders.

## Non-goals

Do not implement:

- file attachment downloading;
- `manifest.json`, content identity, or the complete CHAT-D1 bundle;
- multi-source support;
- asset transcoding, resizing, re-encoding, or image optimization;
- persistent HTTP sessions or persistent cookies;
- automatic share revocation;
- capture-root configuration or unrelated capture-root changes;
- assistant-generated images beyond currently supported visible user image
  parts;
- packaging, distribution, or release automation;
- unrelated cleanup or refactoring.

## Evidence requirements

Add focused tests covering at least:

- image pointer extraction retains the information required for acquisition;
- one cookie-aware session spans share fetch and asset resolution;
- successful image acquisition;
- local Markdown references the preserved relative asset;
- multiple images receive deterministic non-colliding names;
- backend resolution failure;
- blob download failure;
- malformed asset pointer;
- expected metadata mismatch where evidence supports validation;
- no signed URL or cookie material appears in persisted output;
- text-only captures continue behaving exactly as before.

Use mocks and fixtures. Unit tests must not depend on live ChatGPT or OpenAI
endpoints. Do not retain public conversation bodies, share identifiers,
credentials, cookies, or signed URLs in tracked evidence.

Existing relevant tests continue to pass, with current unresolved-image
placeholder expectations updated to the new successful image representation.

Verification must include:

- `python3 -m unittest -v`;
- `npx --yes pyright`;
- `uvx ruff check .`;
- `git diff --check`;
- local-native render and validate for the authority-only Work object.

Review the intended implementation diff and confirm it contains no unrelated
scope.

## Acceptance criteria

- [x] A successful capture of a share with a supported visible user image
      preserves the share-visible image bytes locally.
- [x] The Markdown capture references each preserved image with a portable
      relative Markdown path at the original conversation position.
- [x] Stored image names are deterministic and collision-safe, including
      when source filenames repeat.
- [x] The cookie jar and HTTP session exist only for the capture operation.
- [x] Signed download URLs and cookies are not serialized into Markdown or
      persisted as evidence.
- [x] Capture fails visibly, without `CAPTURE COMPLETE` or a misleading
      Markdown file, when a supported visible image cannot be preserved.
- [x] Malformed asset pointers, backend resolution failure, unsuccessful
      resolution responses, blob download failure, empty bytes, and evidenced
      size or PNG dimension mismatches fail visibly.
- [x] File attachments remain `[File: <filename>]` placeholders.
- [x] Text-only capture behavior remains unchanged.
- [x] Existing atomic and non-overwriting persistence behavior is preserved
      as far as the current architecture allows.
- [x] The CHAT-7 post-capture shared-link security result remains truthful.
- [x] README describes share-visible image preservation accurately, including
      sanitization or resize, and does not claim original-upload fidelity or
      file-attachment downloading.
- [x] Focused tests cover the required acquisition, persistence, failure,
      secret-nonpersistence, and text-only regression cases.
- [x] `python3 -m unittest -v`, `npx --yes pyright`, `uvx ruff check .`, and
      `git diff --check` pass, with failures and limitations reported
      honestly.
- [x] The intended implementation diff contains no unrelated scope.
- [x] Completion state remains explicit and separate from human acceptance.
- [x] A human accepts the resulting image-preservation behavior against this
      Work contract.

## Completion boundary

CHAT-10 is complete when a successful capture of a supported visible user
image writes the share-visible image bytes beside the Markdown capture,
references those files with portable relative Markdown paths, fails visibly
instead of publishing a placeholder-only capture when acquisition cannot be
completed, required verification passes, and a human accepts the behavior.

Do not mark this Work done, check human-accepted criteria, reconcile
authority, commit the implementation, or push unless a later human decision
explicitly authorizes that action.

## Implementation evidence

The accepted product implementation is the local working-tree diff against
HEAD `e606684010d4f5217f794214bfc2d0657045b820`. It is not yet committed.
It changes exactly:

- `README.md`;
- `chatmd.py`;
- `test_chatmd.py`;
- `authority/Projects/CHAT-P1/Work/CHAT-10.md`;
- render-owned navigation on `authority/Projects/CHAT-P1/CHAT-P1.md`.

Capture uses one cookie-aware stdlib HTTP session for the share fetch,
backend image resolution, and immediate blob download. The cookie jar exists
only for that run. Visible `image_asset_pointer` parts retain the parsed file
id, shared conversation id, and evidenced size, dimensions, filename, and
MIME type when present. Successful captures write share-visible image bytes
into a sibling `<stem>-images/` directory and reference them with ordinary
relative Markdown image syntax at the original part position.

No file-attachment downloading, `manifest.json`, content identity, CHAT-D1
bundle, persistent cookies or signed URLs, capture-root redesign, or
automatic share revocation was introduced. The CHAT-7 post-capture security
wording is unchanged.

## Verification

No prepared LWA GO run exists for CHAT-10. Closeout uses the repository
quality gate, authority render/validate, and the human-observed live capture.
Absence of a GO bundle does not decide acceptance.

Recorded local verification after implementation, re-run at closeout:

- `python3 -m unittest -v` - 59 tests, exit 0;
- `npx --yes pyright` - 0 errors, 0 warnings, 0 informations, exit 0;
- `uvx ruff check .` - all checks passed, exit 0;
- `git diff --check` - passed, exit 0;
- `lwa render` / `lwa validate` - ChatMD authority root valid
  (1 project, 10 issues, 1 document, 12 objects).

Focused tests cover pointer extraction, cookie-aware session spanning,
successful acquisition, relative Markdown asset links, repeated-filename
non-collision, backend resolution failure including unsuccessful JSON
status, blob download failure, malformed pointers, size and PNG dimension
mismatch, empty bytes, secret-nonpersistence, unpreserved-image
non-publication, text-only Markdown-only output, and no `CAPTURE COMPLETE`
on image acquisition failure.

Closeout inspection of the accepted live files, without retaining the share
identifier or conversation body, confirmed:

- Markdown
  `/Users/marwan/My vault/Sources/ChatMD/2026/09/Asset preservation test-2.md`
  exists and contains
  `![img2.PNG](Asset%20preservation%20test-2-images/01-img2.PNG)`;
- image
  `/Users/marwan/My vault/Sources/ChatMD/2026/09/Asset preservation test-2-images/01-img2.PNG`
  is a PNG of 202545 bytes whose IHDR is 941 x 2048;
- that Markdown does not contain cookie material, a signed blob URL, or
  backend download URLs;
- an earlier same-title capture remains as
  `Asset preservation test.md` and was not overwritten.

No public conversation body, share identifier, credential, cookie, or
signed URL is retained in tracked evidence.

## Human acceptance

Accepted at `2026-09-19T21:27:00Z` as complete for the CHAT-10 revision 1
boundary.

The human operator reviewed the implementation, automated verification, and
a real end-to-end capture of a disposable public share containing one
supported visible user image, then explicitly granted acceptance of CHAT-10
and authorized authority reconciliation without commit or push.

The accepted live result is:

- the local CHAT-10 working tree captured the live share;
- ChatMD wrote
  `/Users/marwan/My vault/Sources/ChatMD/2026/09/Asset preservation test-2.md`;
- it preserved the share-visible image at
  `/Users/marwan/My vault/Sources/ChatMD/2026/09/Asset preservation test-2-images/01-img2.PNG`;
- preserved size 202545 bytes and dimensions 941 x 2048, matching the
  previously investigated share-visible representation rather than the
  original upload;
- Markdown referenced the local asset as
  `![img2.PNG](Asset%20preservation%20test-2-images/01-img2.PNG)`;
- the public share was then revoked;
- a new capture attempt against the revoked share failed visibly with
  `share serverResponse.data not found`;
- the already captured local image remained present at 202545 bytes after
  revocation.

The previously verified Markdown and local asset remain the durable local
evidence. The share identifier is not retained here.

## Disposition

`CHAT-10` is completed.

A successful capture of a supported visible user image preserves the
share-visible image bytes beside the Markdown capture and references them
with portable relative Markdown paths. After the public share is revoked,
the local image remains. File-attachment downloading, original-upload
fidelity, persistent cookies or signed URLs, automatic revocation, and the
CHAT-D1 portable bundle remain outside this Work.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-10`
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
