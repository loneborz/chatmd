<!-- lwa:meta
{
  "id": "CHAT-4",
  "kind": "issue",
  "title": "Ship the first complete end-user chatmd workflow",
  "authority": "local-native",
  "revision": 1,
  "status": "active",
  "created_at": "2026-09-19T01:57:21Z",
  "updated_at": "2026-09-19T01:57:21Z",
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
# Ship the first complete end-user chatmd workflow

## Outcome

Implement the first complete end-user workflow for chatmd:

```text
chatmd <public-chatgpt-share-url>
```

The command fetches one public ChatGPT share URL through the existing parsing
core and deterministically creates one clean Markdown file on the user's
Desktop.

The first output is a standalone Markdown export for direct human use. It is
not the portable bundle directory contract from CHAT-D1 and does not introduce
manifest creation, asset publication, or consumer integration.

The canonical first-workflow Markdown shape is:

```markdown
# <conversation title>

> Source: <original share URL>

**User**

<exact visible message content>

**ChatGPT**

<exact visible message content>
```

Each visible message receives its own role heading and remains in normalized
conversation order. Existing Markdown, code blocks, tables, links, lists,
citations, and semantically relevant whitespace remain source content rather
than being rewritten.

## Governing authority / source of truth

CHAT-P1 defines the product purpose, product boundary, and no-rewrite
invariant.

CHAT-D1 directly governs canonical title, message, part, citation, ordering,
and preservation semantics. CHAT-4 defines only the first standalone
end-user Markdown export surface and must not change the CHAT-D1 bundle
contract.

CHAT-1 provides the public-share format evidence. CHAT-2 provides the
production parsing boundary and normalized conversation model. CHAT-3 provides
the current title, citation, and preservation implementation that the
serializer and CLI must consume without bypassing or duplicating.

The repository implementation, its tests, and the observable command result
are the technical source of truth for this Work after implementation.

## Scope

- Add deterministic Markdown serialization from the normalized `Conversation`
  model and the exact URL supplied to the command.
- Serialize the exact title when present as the document heading. When the
  normalized title is absent, use the deterministic document heading
  `# conversation` without changing the normalized title value.
- Serialize the exact original URL in the source line without URL cleanup,
  redirect resolution, or parameter rewriting.
- Emit one `**User**` or `**ChatGPT**` heading for every visible message and
  preserve every message in normalized conversation order.
- Serialize text parts without trimming, paraphrasing, Markdown
  normalization, citation expansion, or other content rewriting.
- Represent an unresolved `ImagePart` at its exact part position as the
  literal text `[Image in original conversation]`. Do not fetch, save, resize,
  or transform image assets.
- Keep structural separators deterministic while adding no content inside a
  message beyond the required unresolved-image placeholder.
- Add the intentionally small CLI with exactly one positional public share URL
  input and no stdout, stdin, clipboard, GUI, or multiple-URL mode.
- Derive one safe `.md` basename from the conversation title by trimming outer
  whitespace and dots, replacing path separators and control characters with
  `_`, collapsing runs of whitespace, and falling back to `conversation` when
  the result is empty. The filename derivation must not alter serialized
  conversation content.
- Write only beneath the user's Desktop by default. Create a new file with
  exclusive creation semantics and fail clearly without modifying an existing
  file when the derived path already exists.
- Leave image asset downloading, bundle directory creation, packaging,
  distribution, release automation, and all consumer integrations outside this
  Work.

## Non-goals

Do not implement:

- image asset downloading or local image links;
- clipboard output;
- stdout serialization mode;
- stdin input;
- multiple URL processing;
- a GUI, native macOS surface, or browser extension;
- packaging, installation, distribution, or release automation;
- LLM rewriting, summarization, enrichment, or citation rewriting;
- `manifest.json`, content identity, bundle hashing, or atomic portable bundle
  publication;
- a second parser, a second normalized conversation model, or a consumer-
  specific output format;
- automatic overwrite, automatic replacement, or silent collision renaming.

## Evidence requirements

Automated tests must establish the observable first-workflow behavior using
privacy-safe synthetic normalized conversations and fetch fixtures. They must
cover:

- exact deterministic Markdown output for a title-bearing conversation;
- the explicit absent-title heading and filename fallback without title
  synthesis in the normalized model;
- exact source URL preservation in the source line;
- every visible user and assistant message represented once and in order,
  including repeated roles and empty message content where the normalized
  model permits it;
- preservation of existing Markdown, code fences, tables, links, lists,
  citations, and semantically relevant whitespace in text parts;
- image placeholders at the exact order position among text and image parts;
- stable byte-for-byte serialization for the same normalized input;
- deterministic safe filename derivation, including path separators, control
  characters, whitespace, dots, and an empty result;
- Desktop-only default output, exclusive file creation, clear collision
  failure, and no partial output on fetch, parse, serialization, or write
  failure;
- clear CLI behavior for missing, extra, or invalid positional input;
- no stdout mode, stdin mode, clipboard behavior, multiple-URL behavior, asset
  download, or content rewriting being introduced.

Run the smallest useful repository quality gate for the completed
implementation:

- `python3 -m unittest -v`;
- `pyright`;
- `ruff check .`;
- `git diff --check`.

Review the complete intended implementation and authority diff. Retain no
public conversation body, share identifier, signed URL, cookie, credential,
or downloaded asset in tests or evidence.

## Acceptance criteria

- [ ] `chatmd <public-chatgpt-share-url>` accepts exactly one URL and creates
      one Markdown file on the user's Desktop.
- [ ] A title-bearing conversation produces the exact conversation-first
      Markdown structure defined by this Work, with a deterministic trailing
      newline and no unrelated sections.
- [ ] An absent normalized title uses `conversation` only for the document
      heading and default filename; the parser's title remains absent.
- [ ] The source line contains the exact original URL supplied by the user.
- [ ] Every visible message is represented exactly once, in normalized
      conversation order, with the correct `User` or `ChatGPT` heading.
- [ ] Message text is preserved exactly as represented by the normalized
      parser model, including Markdown, code blocks, tables, links, lists,
      citations, and semantically relevant whitespace.
- [ ] Unresolved images are represented exactly at their conversation part
      position as `[Image in original conversation]`, with no image download or
      asset transformation.
- [ ] Repeating the same normalized input and URL produces byte-identical
      Markdown content.
- [ ] The default filename is a deterministic safe `.md` basename derived from
      the title, with the documented fallback and sanitization behavior.
- [ ] An existing derived path is never silently overwritten or replaced; the
      command fails clearly and leaves the existing file unchanged.
- [ ] Fetch, parse, serialization, or file-creation failure does not publish a
      partial or misleading output file.
- [ ] Missing, extra, or invalid command-line input fails clearly without
      entering another input or output mode.
- [ ] `python3 -m unittest -v`, `pyright`, `ruff check .`, and `git diff
      --check` pass for the completed implementation.
- [ ] The complete intended implementation and authority diff is reviewed and
      remains within this Work.
- [ ] No image downloading, clipboard or stdout mode, stdin, multiple-URL
      processing, GUI or native macOS surface, browser extension,
      packaging/distribution/release automation, bundle publication, or LLM
      transformation is introduced.

## Completion boundary

CHAT-4 is complete when a user can run the one-URL `chatmd` command against a
supported public ChatGPT share and observe one deterministic, clean Markdown
file on the Desktop that satisfies the title, source, ordering, preservation,
image-placeholder, filename, and no-overwrite rules in this Work, with the
requested quality gate passing.

The portable CHAT-D1 bundle contract, image asset handling, package and
distribution mechanics, release automation, native or GUI surfaces, browser
extensions, clipboard and stdout modes, multiple-URL processing, and any LLM
transformation remain outside this completion boundary.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-4`
- Kind: `issue`
- Status: `active`
- Revision: `1`
- Authority: `local-native`
- Owner: [[Projects/CHAT-P1/CHAT-P1|CHAT-P1]]: chatmd

## Owned Documents

_None._

## Relations

- **governed-by** -> [[Projects/CHAT-P1/Documents/CHAT-D1|CHAT-D1]]: Portable Conversation Bundle Contract

## Backlinks

_None._
<!-- lwa:derived:end -->
