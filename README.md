# chatmd

ChatMD captures a public ChatGPT share as a deterministic local Markdown Source
artifact.

Shared conversations are transient web pages. ChatMD writes one Markdown file
from a public share URL without summarizing, paraphrasing, or otherwise
rewriting the visible conversation. The portable conversation bundle specified
in CHAT-D1 is not the current output format.

## What it does

Given one public ChatGPT share URL, ChatMD fetches the share over ordinary HTTP,
reconstructs the active visible conversation from ChatGPT's structured share
data, and writes a deterministic Markdown file into a local vault directory.

It is a capture boundary, not a knowledge-processing system. Successful captures
currently go to:

```text
~/My vault/Sources/ChatMD/YYYY/MM/
```

That capture root is machine-specific. After one local install, ChatMD is invoked
as `chatmd`.

## Quick start

From a checkout of this repository, install the local `chatmd` command once:

```sh
uv tool install .
```

Then, from any directory:

```sh
chatmd https://chatgpt.com/share/<public-share-id>
```

Or copy the public share link in ChatGPT and run:

```sh
chatmd
```

Zero-argument `chatmd` reads the macOS clipboard and uses that text only when,
after surrounding whitespace is removed, it is one
`https://chatgpt.com/share/...` URL. It does not search other clipboard text
for a link. Explicit `chatmd <share-url>` does not read the clipboard.

On success, after the file is written, ChatMD prints a result in this form:

```text
CAPTURE COMPLETE

Saved:
~/My vault/Sources/ChatMD/YYYY/MM/<conversation>.md

Shared source:
https://chatgpt.com/share/<public-share-id>

SECURITY:
This shared link still exists.
Revoke it in ChatGPT > Settings > Data Controls > Shared Links.
```

`chatmd --help` behaves as a normal CLI command. Shell quotes are not required
around the share URL unless the URL itself needs quoting. Clipboard capture is
macOS-native and requires the `pbpaste` command.

This repository currently uses a machine-specific local capture root under
`~/My vault/Sources/ChatMD`. The `~` form is README notation for privacy, not
runtime home-directory expansion or a configuration setting. On another
machine, change the capture root in `chatmd.py` and reinstall before using the
command unchanged. The local `chatmd` command does not make that capture root
portable.

## Capture guarantees

- Visible conversation text is preserved as the structured share represents it.
- ChatMD does not use an LLM to rewrite, summarize, or clean up source content.
- Existing files are never silently overwritten.
- Filename collisions keep the original file and write a deterministic suffix
  such as `conversation-2.md`.
- Empty, whitespace-only, and other contentless exports are rejected.
- Failed fetch, parse, conversion, or filesystem operations do not create a
  successful-looking capture.
- The post-capture result is printed only after persistence. It reports
  `CAPTURE COMPLETE`, the exact file that was written, the original share URL,
  and an explicit warning that the shared link still exists.
- Failed validation, fetch, parse, or persistence does not print
  `CAPTURE COMPLETE` or the shared-link security warning.

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
input also fails clearly. ChatMD accepts one public HTTP(S) share URL as an
explicit argument, or a copied `https://chatgpt.com/share/...` URL from the
macOS clipboard when no URL is supplied. Clipboard-mode validation is stricter
than the explicit HTTP(S) URL check. A successful capture does not revoke the
public share; the CLI result tells the user to revoke it in ChatGPT settings.

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
- public package publishing, Homebrew distribution, or release automation
- LLM summarization, rewriting, or knowledge extraction
- tagging, embeddings, RAG, or automatic promotion into a knowledge base
- automatic shared-link revocation
- the portable conversation bundle contract specified in CHAT-D1
  (`manifest.json`, `assets/`, content identity)

It captures one public share URL at a time. Private conversations and ChatGPT
authentication are outside the current workflow. Zero-argument clipboard
capture is macOS-native and is not a watcher, daemon, or GUI.
