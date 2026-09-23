<!-- lwa:meta
{
  "id": "CHAT-18",
  "kind": "issue",
  "title": "Import Codex shared conversations",
  "authority": "local-native",
  "revision": 1,
  "status": "active",
  "created_at": "2026-09-20T21:56:00Z",
  "updated_at": "2026-09-20T21:56:00Z",
  "owner": {
    "kind": "project",
    "id": "CHAT-P1"
  },
  "relations": [
    {
      "type": "related",
      "target": "CHAT-17"
    }
  ]
}
-->
# Import Codex shared conversations

## Outcome

A Codex share link should be ingestible by ChatMD as another conversation
source, not as a one-off export path.

The intended path is:

```text
Codex share URL
  -> Codex source adapter
  -> normalized ChatMD Conversation
  -> existing Markdown rendering and local capture
```

This Work first investigates the actual Codex share-link format and the
content that is accessible from it. If a public share can be fetched with
ordinary HTTP, reconstructed faithfully, and used without private
authentication or a fragile workaround, ChatMD should capture it through
the existing pipeline.

If Codex share URLs cannot be consumed reliably and lawfully from the
shared URL, this Work documents that constraint, makes such input fail
clearly, and stops. It must not invent a brittle special-case exporter.

The user-visible value is that a Codex conversation the user already chose
to share can become the same kind of local Markdown source that ChatMD
already produces for ChatGPT public shares.

## Governing authority / source of truth

CHAT-P1 defines the product purpose, local-first boundary, no-rewrite
invariant, fail-visible behavior, Python-stdlib preference, and current
primary interface. That Project currently names public ChatGPT shared
conversations as the source.

This Work must not silently rewrite CHAT-P1. If investigation proves Codex
ingestion is feasible, the smallest CHAT-P1 wording change needed to admit
a second public-share source is in scope as a consistency correction. It
must preserve the no-rewrite invariant, local-first boundary, ordinary-HTTP
preference, and fail-visible behavior.

CHAT-D1 remains the portable bundle contract. Its current
`source_identity` sketch is ChatGPT-share-specific. This Work does not
implement the bundle and is not governed by CHAT-D1. It must not invent a
second interchange contract. A later Document revision may be needed if
bundle work ever has to name Codex sources.

Accepted CHAT-1 and CHAT-2 own ChatGPT share-format evidence and the
production parsing core. They are the pattern for investigation-then-
adapter work, not code to clone for Codex. Accepted CHAT-4, CHAT-5,
CHAT-7, CHAT-8, CHAT-9, CHAT-10, and CHAT-13 own Markdown export, local
capture reliability, ChatGPT post-capture security text, the installed
CLI, clipboard convenience, image preservation, and capture-root
behavior.

The current `chatmd.py` implementation is the technical source of truth.
Repository inspection before this Work found:

- there is no Codex parser, fixture, or URL classifier;
- `_validate_share_url()` accepts any absolute HTTP(S) URL;
- clipboard mode accepts only `https://chatgpt.com/share/...`;
- `parse_share()` decodes ChatGPT React Router hydration and
  `routes/share.$shareId.($action)`;
- the normalized model is `Conversation(title, messages)` with `user` and
  `assistant` roles, text, image, file parts, and citations;
- `serialize_conversation()` projects assistant messages as `ChatGPT`;
- the CHAT-7 success result tells the user to revoke a ChatGPT shared
  link in ChatGPT settings;
- downstream write, collision, capture-root, and image-preservation logic
  consume the normalized model rather than ChatGPT HTML.

CHAT-17 is related Work for a universal capture-input boundary. Codex
ingestion must be independently deliverable through the current `chatmd
<url>` interface. If CHAT-17 is already accepted, reuse its ingestion
boundary. Do not block on CHAT-17, and do not implement universal
invocation in this Work.

Observed public Codex share behavior is the technical source of truth for
format and accessibility. Do not assume a URL shape, HTML structure, API,
or authentication model before that evidence exists.

The repository implementation, tests, documented invocation, and
observable `chatmd` command result are the technical source of truth after
implementation. Human acceptance remains a separate authority decision.

## Affected systems

- `chatmd.py` source classification, fetch, and parse boundaries;
- the normalized `Conversation` model only if Codex evidence requires a
  faithful representation that the current model cannot express without
  silent loss;
- `serialize_conversation()` role headings and source line only as needed
  for Codex captures;
- post-capture CLI success or failure text so ChatGPT-specific revocation
  copy is not emitted for Codex;
- `test_chatmd.py` and privacy-safe fixtures;
- `README.md` and `chatmd --help` if Codex capture becomes a supported
  source;
- `tools/probe_share.py` only if a Codex investigation helper is justified
  the same way CHAT-1 used a probe.

`website/` is outside this Work.

## Constraints

- Reuse the existing normalization and Markdown rendering architecture.
- Do not duplicate the Markdown exporter for Codex.
- Do not assume the implementation mechanism before inspecting current
  code and live share evidence.
- Prefer ordinary HTTP fetching over browser automation.
- Do not require Codex, ChatGPT, or OpenAI authentication.
- Do not extract private cookies, sessions, or local Codex app state.
- Do not use an LLM to transform conversation content.
- Fail clearly when a URL cannot be accessed or parsed.
- Preserve source-authored content. Do not summarize, paraphrase, or clean
  up messages.
- Keep secrets, share identifiers, conversation bodies, cookies, and
  signed URLs out of tracked evidence.
- CHAT-7 ChatGPT revocation text is ChatGPT-specific. A Codex capture must
  not tell the user to revoke a ChatGPT shared link unless that is
  actually the source.

## Scope

### 1. Investigate the share link

Use representative public Codex share URLs, where available, to determine:

- the actual share-link format;
- whether one ordinary HTTP request can retrieve the shared conversation;
- where structured conversation data exists, if it exists;
- how roles, message order, title, code, attachments, and references are
  represented;
- what content is reader-visible versus internal;
- whether images or other assets are retrievable without authentication;
- how a format change or missing field can fail visibly.

Keep fetching, parsing, and representation distinguishable.

### 2. Decide feasibility

Determine whether ingestion can be implemented robustly and lawfully from
the shared URL.

Feasible means:

- the share is intended as a public page or otherwise publicly accessible
  representation;
- ordinary HTTP is sufficient;
- visible conversation structure can be reconstructed without rendered-DOM
  guessing as the primary source;
- ChatMD would not need private authentication, session theft, or
  undocumented account APIs.

Not feasible means one or more of:

- the URL requires login or other private credentials;
- the accessible page does not contain reconstructable conversation data;
- the format is too unstable or incomplete to parse without silent loss;
- a working importer would depend on a fragile workaround.

If not feasible, document the constraint, make Codex-shaped input fail
clearly rather than through the ChatGPT parser, and stop.

### 3. Map into the normalized model

If feasible, map Codex conversation structure onto ChatMD's existing
`Conversation` representation:

- title, or legitimately absent title;
- ordered visible messages;
- roles;
- text, code, and other source-authored visible content;
- attachments or references where the public share actually exposes them.

Preserve relevant metadata that the current model can represent faithfully.
Do not synthesize missing titles, URLs, filenames, or citations.

If Codex requires a representation the current model cannot express,
either extend the model in the smallest fail-visible way or reject that
content as unsupported. Do not silently drop visible content.

Assistant role projection is a presentation decision. Do not assume the
ChatGPT heading is correct for Codex. Choose the smallest honest heading
supported by evidence and keep it deterministic.

### 4. Reuse the existing capture pipeline

After a normalized `Conversation` exists, use the existing Markdown
renderer, capture-root writer, collision behavior, and empty-content
rejection. Do not add a second exporter.

Image preservation may reuse CHAT-10 mechanics only when Codex evidence
shows an equivalent retrievable visible image. Otherwise leave images
outside this Work and fail visibly on unsupported visible image content.

### 5. Failure behavior

If the URL cannot be accessed, is not a Codex share after classification,
or cannot be parsed faithfully, fail with a non-zero status, write no
capture, and do not emit `CAPTURE COMPLETE` or ChatGPT revocation text.

A Codex-shaped URL must not be forced through ChatGPT hydration parsing
once the Codex share format has been identified.

### 6. Tests and documentation

Add tests or fixtures that verify the importer without depending
unnecessarily on live external state. Update README and help only if Codex
becomes a supported source.

## Non-goals

Do not:

- implement universal invocation, stdin, file routing, Services,
  Shortcuts, or a menu bar, which belong to CHAT-17 or later Work;
- duplicate Markdown serialization, capture-root writing, or collision
  handling;
- implement the CHAT-D1 portable bundle;
- capture private, authenticated, or local-only Codex sessions;
- use browser automation, cookie jars copied from a user profile, or
  undocumented account APIs;
- automatically revoke Codex or ChatGPT shares;
- download file-attachment bytes unless investigation proves they are
  public, required for a faithful capture, and representable without a
  new product contract;
- add LLM rewriting, summarization, or translation;
- treat ChatGPT share parsing as broken or reopen CHAT-1 through
  CHAT-10;
- update the public onepager;
- invent a workaround after a no-go feasibility result.

## Risks

- Codex share pages may require authentication or may not expose
  structured conversation data over ordinary HTTP.
- The URL may look enough like a ChatGPT share that the current parser
  fails opaquely or, worse, misreads unrelated HTML.
- Mapping Codex roles, tool output, diffs, or attachments onto a
  ChatGPT-shaped model can silently lose visible content.
- Reusing CHAT-7 ChatGPT revocation copy would be false for a Codex
  source.
- Live share investigation can leak conversation bodies or identifiers
  into tests and evidence.
- CHAT-D1 source identity is ChatGPT-specific. Implementing bundle
  semantics here would over-scope the Work.
- Waiting on CHAT-17 would couple two independently deliverable sources.

## Implementation sequence

1. Inspect the current ChatGPT fetch, parse, normalize, serialize, and
   write path and identify the adapter boundary.
2. Investigate representative public Codex share URLs the way CHAT-1
   investigated ChatGPT shares. Record format, accessibility, and
   limitations without committing conversation bodies.
3. Decide feasible or not feasible against the robustness and public-
   access rules in this Work.
4. If not feasible, document the constraint, add clear rejection for
   identified Codex share input, update tests, and stop.
5. If feasible, implement a Codex source adapter that returns the existing
   `Conversation` model.
6. Route classified Codex URLs through that adapter, then through the
   existing renderer and writer.
7. Adjust Codex-specific presentation and post-capture text only as
   evidence requires.
8. Add privacy-safe fixtures and tests that do not depend on live
   network state for correctness.
9. Apply the smallest CHAT-P1 wording correction if a second public-share
   source is now part of the product.
10. Update README and help to match the accepted result.

## Evidence requirements

- Investigation evidence records the observed share-link format, whether
  ordinary HTTP is sufficient, what structured data exists, and the
  feasibility decision with reasons.
- If not feasible, tests prove identified Codex share input fails clearly
  and is not parsed as a ChatGPT share, and no capture is written.
- If feasible, tests prove a privacy-safe Codex fixture maps into the
  normalized `Conversation` model and through the existing Markdown
  renderer without a second exporter.
- Tests prove inaccessible, malformed, and unsupported Codex input fail
  clearly, write no capture, and do not emit `CAPTURE COMPLETE` or
  ChatGPT revocation text.
- Correctness does not depend on a live external Codex share remaining
  available. Live checks, if used, are supplementary and must not retain
  conversation bodies or share identifiers.
- Existing ChatGPT capture tests continue to pass.
- `python3 -m unittest -v` passes.
- `npx --yes pyright` passes.
- `uvx ruff check .` passes.
- `git diff --check` passes.
- The intended implementation or investigation diff contains no unrelated
  scope.

Do not retain public conversation bodies, share identifiers, credentials,
cookies, or signed URLs in tracked evidence.

## Acceptance criteria

- [ ] The actual Codex share-link format and accessible content have been
      investigated from representative public evidence, or the absence of
      such evidence is recorded as the feasibility blocker.
- [ ] A written feasible or not-feasible decision exists, including
      robustness and public-access reasons.
- [ ] If not feasible, the constraint is documented in this Work, Codex-
      shaped input fails clearly, and no fragile workaround is
      introduced.
- [ ] If feasible, a Codex source adapter reconstructs a normalized
      ChatMD `Conversation` and reuses the existing Markdown rendering
      and local capture pipeline.
- [ ] Visible roles, messages, code, attachments, and references are
      preserved where the public share exposes them, or unsupported
      visible content fails visibly.
- [ ] Source-authored content is not rewritten.
- [ ] ChatGPT public-share capture remains unchanged.
- [ ] Inaccessible or unparsable Codex URLs fail clearly, write no
      capture, and do not emit a successful ChatGPT security result.
- [ ] Tests or fixtures verify the importer without unnecessary live
      external state.
- [ ] README and help match the accepted supported-source set.
- [ ] CHAT-D1 bundle publication is not implemented.
- [ ] Universal invocation surfaces from CHAT-17 are not implemented
      here.
- [ ] `python3 -m unittest -v`, `npx --yes pyright`, `uvx ruff check .`,
      and `git diff --check` pass, with failures and limitations reported
      honestly.
- [ ] The intended diff contains no unrelated scope.
- [ ] A human accepts the investigation result and, if implemented, the
      Codex capture behavior against this Work contract.

## Completion boundary

CHAT-18 is complete when Codex share-link feasibility is known from
evidence, and either:

- ChatMD ingests a supported public Codex share through a source adapter
  into the existing normalized conversation and Markdown capture
  pipeline, with clear failure for unusable URLs; or
- ingestion is documented as not currently possible, Codex-shaped input
  fails clearly, and no fragile workaround was added.

The required verification must pass, and a human must accept the result.

Do not mark this Work done, check human-accepted criteria, reconcile
authority, commit, or push unless a later human decision explicitly
authorizes that action.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-18`
- Kind: `issue`
- Status: `active`
- Revision: `1`
- Authority: `local-native`
- Owner: [[Projects/CHAT-P1/CHAT-P1|CHAT-P1]]: chatmd

## Owned Documents

_None._

## Relations

- **related** -> [[Projects/CHAT-P1/Work/CHAT-17|CHAT-17]]: Define a universal ChatMD capture invocation

## Backlinks

- **related** <- [[Projects/CHAT-P1/Work/CHAT-17|CHAT-17]]: Define a universal ChatMD capture invocation
<!-- lwa:derived:end -->
