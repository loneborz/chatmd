# chatmd

ChatMD captures a public ChatGPT share as source-faithful local Markdown.

Shared conversations are transient web pages. ChatMD writes one durable Markdown
file from a public share URL without summarizing, paraphrasing, or otherwise
rewriting the visible conversation.

## What it does

Given one public ChatGPT share URL, ChatMD fetches the share over ordinary HTTP,
reconstructs the active visible conversation from ChatGPT's structured share
data, and writes a deterministic Markdown file into a local vault directory.

It is a capture boundary, not a knowledge-processing system. Successful captures
currently go to:

```text
/Users/marwan/My vault/Sources/ChatMD/YYYY/MM/
```

That capture root is machine-specific. ChatMD is not yet a portable packaged
CLI.

## Quick start

From a checkout of this repository:

```sh
python3 chatmd.py https://chatgpt.com/share/<public-share-id>
```

On success, ChatMD prints the exact persisted path:

```text
Saved: /Users/marwan/My vault/Sources/ChatMD/YYYY/MM/<conversation>.md
```

There is no install command. Run `chatmd.py` from the repository with Python 3.

This repository is currently configured for the author's machine. Captures are
written to `/Users/marwan/My vault/Sources/ChatMD`. On another machine, change
that capture root in `chatmd.py` before using the command unchanged. ChatMD
works end-to-end today, but it is not yet portable or packaged.

## Capture guarantees

- Visible conversation text is preserved as the structured share represents it.
- ChatMD does not use an LLM to rewrite, summarize, or clean up source content.
- Existing files are never silently overwritten.
- Filename collisions keep the original file and write a deterministic suffix
  such as `conversation-2.md`.
- Empty, whitespace-only, and other contentless exports are rejected.
- Failed fetch, parse, conversion, or filesystem operations do not create a
  successful-looking capture.
- `Saved: <absolute-path>` is printed only after persistence, and it is the
  exact file that was written.

Year and month directories come from the local capture date and are created when
missing. The filename is derived from the conversation title, with a
filesystem-safe fallback of `conversation.md`.

## How it works

```text
public share URL
  -> structured ChatGPT share data
  -> active visible conversation
  -> normalized model
  -> deterministic Markdown
  -> validated local capture
```

Public share HTML includes structured conversation data in its React Router
hydration stream. ChatMD reads that representation instead of scraping rendered
DOM so it can recover message order, roles, and source text directly.

The Markdown capture looks like this:

```markdown
# Conversation title

> Source: https://chatgpt.com/share/...

---

**User**

exact visible message content

---

**ChatGPT**

exact visible message content
```

If the share has no title, the document heading and default filename use
`conversation`. That fallback is projection only; ChatMD does not invent a title
in the conversation model.

## Content fidelity

Preserved:

- exact reader-visible title when present
- visible user and assistant messages on the active branch, in order
- source-authored Markdown, code fences, tables, links, lists, and whitespace
- inline citation markers as they appear in the source text
- visible file attachments as `[File: <filename>]` at their original position
- images as `[Image in original conversation]` at their original position

Intentionally excluded:

- system and tool messages
- reasoning, thought, execution, and model-context content
- thinking preambles and explicitly hidden messages
- tool-directed assistant messages and user system messages
- UI-only follow-up controls
- hidden citation internals

Image and file assets are not downloaded. The placeholders above are the current
accepted representation.

Unknown visible roles, content types, or multimodal parts fail with a clear
error instead of being silently dropped.

## Safety and failure behavior

Parsing is fail-visible: malformed share structure or unsupported visible
content stops the run rather than producing an incomplete transcript.

Persistence writes a complete Markdown body, then publishes it to the final
path. Failures return a non-zero exit status. Missing, extra, or invalid CLI
input also fails clearly. ChatMD accepts exactly one public HTTP(S) share URL.

## Development and verification

The runtime implementation uses the Python standard library. From the repository root:

```sh
python3 -m unittest -v
npx --yes pyright
uvx ruff check .
git diff --check
```

## Local Work Authority

Development authority is stored locally under
[`authority/Projects/CHAT-P1/`](authority/Projects/CHAT-P1/).

The repository keeps these as separate facts:

- authorized Work
- implementation
- verification
- human acceptance
- reconciliation

This README describes the current capture tool. The authority tree records how
that tool was authorized, verified, and accepted.

## Current limitations

ChatMD does not yet provide:

- image or file asset downloading
- portable capture-root configuration
- package installation, distribution, or release automation
- LLM summarization, rewriting, or knowledge extraction
- tagging, embeddings, RAG, or automatic promotion into a knowledge base
- the portable conversation bundle contract (`manifest.json`, `assets/`,
  content identity)

It captures one public share URL at a time. Private conversations and ChatGPT
authentication are outside the current workflow.
