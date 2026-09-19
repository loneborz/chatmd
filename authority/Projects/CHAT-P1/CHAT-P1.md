<!-- lwa:meta
{
  "id": "CHAT-P1",
  "kind": "project",
  "title": "chatmd",
  "authority": "local-native",
  "revision": 2,
  "status": "active",
  "created_at": "2026-09-18T17:58:15Z",
  "updated_at": "2026-09-18T23:51:10Z",
  "owner": null,
  "relations": []
}
-->
# chatmd

## Purpose

Build a small, local-first conversion core that turns public ChatGPT shared conversations into portable, deterministic conversation bundles while preserving the original conversation content.

The primary interface should remain simple:

```text
chatmd <share-url>
```

The resulting bundle should support durable human-readable archival, machine-readable ingestion and reuse by other systems.

## Core invariant

chatmd must not rewrite conversation content.

User and assistant content should be preserved as faithfully as the source representation allows. The tool may add structural metadata required to represent the conversation, but must not summarize, paraphrase, clean up or otherwise alter message content.

## Product principles

- Prefer direct structured conversation data over rendered DOM scraping.
- Prefer ordinary HTTP fetching over browser automation.
- Keep fetching, parsing and serialization as separate boundaries.
- Keep output deterministic.
- Own a portable interchange contract rather than a consumer-specific format.
- Keep chatmd independent of Context World, Obsidian and other consumers.
- Do not use an LLM in the conversion path.
- Fail clearly when source content cannot be represented faithfully.
- Keep the implementation small enough to remain easy to inspect and maintain.

## Product boundary

ChatMD owns the conversion core and portable bundle contract. Context World, a possible future Obsidian plugin and other systems may consume that contract, but do not own it and must not make ChatMD dependent on their internal models or runtime environments.

The detailed bundle contract belongs in a project-owned LWA Document rather than in this Project object.

## Success condition

The project is proven when representative public ChatGPT share URLs can be fetched without browser automation, reconstructed into correctly ordered conversation messages, and converted into portable, deterministic conversation bundles without rewriting source-authored conversation content.

Bundles must provide a machine-readable semantic and integrity contract, a deterministic human-readable conversation projection and any required visible assets. Rich or non-text ChatGPT content must either have an explicit faithful representation or be reported as unsupported rather than silently discarded.
<!-- lwa:derived:start -->
## Object state

- ID: `CHAT-P1`
- Kind: `project`
- Status: `active`
- Revision: `2`
- Authority: `local-native`
- Owner: None

## Owned Work

- [[Projects/CHAT-P1/Work/CHAT-1|CHAT-1]]: Prove lossless ChatGPT share parsing
- [[Projects/CHAT-P1/Work/CHAT-2|CHAT-2]]: Implement deterministic ChatGPT share parsing core
- [[Projects/CHAT-P1/Work/CHAT-3|CHAT-3]]: Extend canonical conversation model with title and citations
- [[Projects/CHAT-P1/Work/CHAT-4|CHAT-4]]: Ship the first complete end-user chatmd workflow
- [[Projects/CHAT-P1/Work/CHAT-5|CHAT-5]]: Make local ChatMD capture reliable
- [[Projects/CHAT-P1/Work/CHAT-6|CHAT-6]]: Sync the public GitHub README with accepted ChatMD state

## Owned Documents

- [[Projects/CHAT-P1/Documents/CHAT-D1|CHAT-D1]]: Portable Conversation Bundle Contract

## Relations

_None._

## Backlinks

_None._
<!-- lwa:derived:end -->
