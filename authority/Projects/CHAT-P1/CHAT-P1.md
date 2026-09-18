<!-- lwa:meta
{
  "id": "CHAT-P1",
  "kind": "project",
  "title": "chatmd",
  "authority": "local-native",
  "revision": 1,
  "status": "active",
  "created_at": "2026-09-18T17:58:15Z",
  "updated_at": "2026-09-18T17:58:15Z",
  "owner": null,
  "relations": []
}
-->
# chatmd

## Purpose

Build a small, local-first tool that converts public ChatGPT shared conversations into deterministic Markdown while preserving the original conversation content.

The primary interface should remain simple:

```text
chatmd <share-url>
```

The resulting Markdown should be suitable for durable human-readable archival, reuse and later ingestion into other context systems.

## Core invariant

chatmd must not rewrite conversation content.

User and assistant content should be preserved as faithfully as the source representation allows. The tool may add structural metadata required to represent the conversation, but must not summarize, paraphrase, clean up or otherwise alter message content.

## Product principles

- Prefer direct structured conversation data over rendered DOM scraping.
- Prefer ordinary HTTP fetching over browser automation.
- Keep fetching, parsing and serialization as separate boundaries.
- Keep output deterministic.
- Do not use an LLM in the conversion path.
- Fail clearly when source content cannot be represented faithfully.
- Keep the implementation small enough to remain easy to inspect and maintain.

## Initial success condition

The project is proven when representative public ChatGPT share URLs can be fetched without browser automation, reconstructed into correctly ordered conversation messages, and serialized to Markdown without rewriting textual conversation content.

Rich or non-text ChatGPT content must either have an explicit faithful representation or be reported as unsupported rather than silently discarded.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-P1`
- Kind: `project`
- Status: `active`
- Revision: `1`
- Authority: `local-native`
- Owner: None

## Owned Work

- [[Projects/CHAT-P1/Work/CHAT-1|CHAT-1]]: Prove lossless ChatGPT share parsing

## Owned Documents

_None._

## Relations

_None._

## Backlinks

_None._
<!-- lwa:derived:end -->
