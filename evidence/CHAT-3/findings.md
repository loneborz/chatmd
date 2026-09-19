# CHAT-3 Source Evidence

## Current source inspected

On 2026-09-19, a current public ChatGPT share containing reader-visible web
citations and the JavaScript reader assets served with that share were
inspected. The share URL, conversation identifiers, message bodies and source
URLs are intentionally not retained.

## Conversation title

The share route's structured `serverResponse.data` object contains `title`.
The observed value is a string and matches the reader-visible page title. The
field is independent of `og_title`. A missing or null `title` therefore maps to
an absent canonical title; no other field is used as a fallback.

## Citation location and visibility

Visible assistant messages carry structured references in
`message.metadata.content_references`. The current reader exposes a
`grouped_webpages` reference only when its `style` is not `hidden` and its
`status` is neither `loading` nor `error`.

For an active `grouped_webpages` reference, each entry in `items`, plus each
entry in an item's `supporting_websites`, is a reader-visible source. Each
source supplies its own `url` and may supply `title`, `attribution`,
`source_name` and `snippet`. The reader omits blank optional strings. It also
derives display fallbacks such as a hostname when optional labels are absent;
those derived values are not source-native and are not canonicalized by
CHAT-3.

The observed `sources_footnote` reference drives the aggregate Sources UI and
is not an inline canonical citation. Other anchored reference types are not
silently treated as citations without evidence.

## Anchors and units

Each active grouped reference supplies `start_idx`, `end_idx` and
`matched_text`. The observed payload satisfies:

```text
message_text[start_idx:end_idx] == matched_text
```

The current reader converts strings with JavaScript `Array.from` before using
these offsets, establishing Unicode code points as the source-native unit.
The inspected payload contains non-ASCII text before citations: code-point
slicing matches `matched_text`, while slicing UTF-8 bytes at the same numeric
offsets does not. Canonical byte offsets must therefore be calculated as the
UTF-8 lengths of the exact text prefixes at `start_idx` and `end_idx`.

## Implementation boundary

CHAT-3 can encode the evidenced `grouped_webpages` format without using legacy
`metadata.citations`, search-result identifiers, `refs`, `safe_urls`, `alt`,
icons, routing fields or aggregate Sources metadata. Unsupported anchored
reference types must fail visibly until current source evidence establishes
their canonical mapping.
