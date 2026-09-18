# CHAT-1 Findings

## Conclusion

Current public ChatGPT share pages can be fetched and reconstructed without browser automation. The representative shares expose structured conversation data in a React Router hydration stream embedded in the returned HTML.

The active branch can be recovered deterministically from `mapping` and `current_node`. No rendered DOM scraping or LLM transformation is required.

## Evidence

Three representative public shares were investigated: ordinary prose, Markdown-rich content, and multimodal content with images.

All three were fetched through ordinary HTTP without ChatGPT account authentication.

Machine-readable structural proof: `evidence/CHAT-1/probe-summary.json`

Research probe: `tools/probe_share.py`

Full HTML and full message bodies are intentionally not committed.

## Structured source and ordering

The relevant share route exposes `serverResponse.data`, which contains the conversation graph.

Recover the active branch by locating `current_node` in `mapping`, walking parent links to the root, then reversing the path.

For all three fixtures this branch exactly matched `linear_conversation`. The latter is useful as a validation oracle, but is not required as the primary parser source.

## Visibility projection

The graph contains visible transcript messages plus internal content such as system messages, tool messages, tool-directed assistant messages, model editable context, thoughts, reasoning recaps, execution output, tool-call code, thinking preambles, and explicitly hidden messages.

Initial keep rules:

- visible user `text` or `multimodal_text`, excluding user-system and explicitly hidden messages;
- visible assistant `text` addressed to `all`, excluding thinking preambles and explicitly hidden messages.

Projection is based on source metadata, not text heuristics.

## Text preservation

Representative source strings contain headings, lists, fenced code, tables, links, blockquotes, and multiple blank lines.

These strings exist directly in structured message content. Frontend inspection showed ordinary text extraction begins from message content parts joined directly together, so chatmd should preserve supported message text directly rather than reproduce ChatGPT clipboard or DOM serialization.

Specialized representations such as writing blocks or ChatGPT-specific citation annotations need an explicit serialization policy. They must not be silently discarded or rewritten during parsing.

## Rich content

In the representative multimodal fixtures every observed non-text part was an `image_asset_pointer`. Unknown future visible content types or multimodal part types must fail visibly rather than being silently omitted.

Image pointers use `sediment://`. A fresh anonymous cookie-aware HTTP session that first fetched the public share page could resolve an image through the ChatGPT backend and download the original JPEG with the expected dimensions and byte size.

Asset downloading remains outside CHAT-1 implementation scope.

## Fail-visible behavior

- Preserve known textual content exactly.
- Represent known image parts as typed image parts.
- Exclude known internal content through explicit projection rules.
- Reject unknown visible content types or multimodal part types.
- Fail when expected share structure is missing or malformed.
- Fail on broken graph relationships or an unresolved active node.
- Never silently emit an incomplete transcript.

## Smallest viable architecture

```text
HTTP session
  -> share HTML
  -> hydration payload decoder
  -> conversation graph parser
  -> active branch reconstruction
  -> visibility projection
  -> normalized conversation model
  -> deterministic Markdown serializer
```

Fetcher, parser, projection, and serializer should remain independently testable.

Browser automation, DOM scraping, and an LLM in the conversion path are not justified by current evidence. CHAT-1 does not select an implementation language.

## Completion boundary

CHAT-1 proves feasibility and parser requirements. It does not implement the production parser, final serializer, CLI, packaging, installation, asset downloading, historical compatibility, or private conversation support.
