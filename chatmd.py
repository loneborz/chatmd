from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
import unicodedata
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timezone
from email.message import Message as Headers
from html.parser import HTMLParser
from itertools import pairwise
from pathlib import Path
from typing import Protocol, Self
from urllib.parse import urlsplit
from urllib.request import urlopen

ROUTE = "routes/share.$shareId.($action)"
MARKER = "window.__reactRouterContext.streamController.enqueue("
CAPTURE_ROOT = Path("/Users/marwan/My vault/Sources/ChatMD")


class ParseError(ValueError):
    """The public share does not match the supported structured format."""


class UnsupportedContentError(ParseError):
    """A visible message contains content that cannot be preserved."""


@dataclass(frozen=True)
class TextPart:
    text: str
    source_type: str = "text"


@dataclass(frozen=True)
class ImagePart:
    asset_pointer: str
    source_type: str = "image_asset_pointer"


@dataclass(frozen=True)
class FilePart:
    filename: str
    source_type: str = "file"


@dataclass(frozen=True)
class Citation:
    start_byte: int
    end_byte: int
    marker: str
    url: str
    title: str | None = None
    attribution: str | None = None
    snippet: str | None = None


@dataclass(frozen=True)
class Message:
    role: str
    source_type: str
    parts: tuple[TextPart | ImagePart | FilePart, ...]
    citations: tuple[Citation, ...] = ()


@dataclass(frozen=True)
class Conversation:
    title: str | None
    messages: tuple[Message, ...]


class _ShareResponse(Protocol):
    headers: Headers

    def read(self) -> bytes: ...

    def __enter__(self) -> Self: ...

    def __exit__(self, *args: object) -> None: ...


class _ScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.current: list[str] | None = None
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script":
            self.current = []

    def handle_data(self, data: str) -> None:
        if self.current is not None:
            self.current.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self.current is not None:
            self.scripts.append("".join(self.current))
            self.current = None


class HydrationGraph:
    def __init__(self, slots: list[object]) -> None:
        self.slots = slots

    def value(self, ref: object) -> object | None:
        if isinstance(ref, int) and not isinstance(ref, bool) and 0 <= ref < len(self.slots):
            return self.slots[ref]
        return None

    def field_ref(self, obj_ref: object, wanted_key: str) -> int | None:
        obj = self.value(obj_ref)
        if not isinstance(obj, dict):
            return None

        for encoded_key, value_ref in obj.items():
            if not isinstance(encoded_key, str) or not encoded_key.startswith("_"):
                continue
            try:
                key = self.value(int(encoded_key[1:]))
            except ValueError:
                continue
            if key == wanted_key:
                return value_ref if isinstance(value_ref, int) else None
        return None

    def field(self, obj_ref: object, wanted_key: str) -> object | None:
        return self.value(self.field_ref(obj_ref, wanted_key))

    def object_refs(self, obj_ref: object) -> dict[object, int]:
        obj = self.value(obj_ref)
        if not isinstance(obj, dict):
            raise ParseError("expected an encoded object")

        decoded: dict[object, int] = {}
        for encoded_key, value_ref in obj.items():
            if not isinstance(encoded_key, str) or not encoded_key.startswith("_"):
                continue
            try:
                key = self.value(int(encoded_key[1:]))
            except ValueError as error:
                raise ParseError("invalid encoded object key") from error
            if key is None or not isinstance(value_ref, int):
                raise ParseError("invalid encoded object entry")
            decoded[key] = value_ref
        return decoded

    def list_refs(self, list_ref: object) -> list[object]:
        value = self.value(list_ref)
        if not isinstance(value, list):
            raise ParseError("expected an encoded list")
        return value


def fetch_share(url: str, opener: Callable[[str], _ShareResponse] = urlopen) -> str:
    with opener(url) as response:
        body = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
    return body.decode(charset)


def decode_hydration(html: str) -> HydrationGraph:
    parser = _ScriptParser()
    parser.feed(html)
    decoder = json.JSONDecoder()
    candidates: list[list[object]] = []

    for script in parser.scripts:
        cursor = 0
        while (marker := script.find(MARKER, cursor)) != -1:
            start = marker + len(MARKER)
            try:
                chunk, consumed = decoder.raw_decode(script[start:])
            except json.JSONDecodeError:
                cursor = start
                continue
            cursor = start + consumed
            if not isinstance(chunk, str):
                continue
            try:
                slots = json.loads(chunk)
            except json.JSONDecodeError:
                continue
            if isinstance(slots, list):
                candidates.append(slots)

    if not candidates:
        raise ParseError("no React Router hydration payload found")
    return HydrationGraph(max(candidates, key=len))


def locate_share_data(graph: HydrationGraph) -> int:
    ref: int | None = 0
    for field in ("loaderData", ROUTE, "serverResponse", "data"):
        ref = graph.field_ref(ref, field)
        if ref is None:
            raise ParseError("share serverResponse.data not found")
    return ref


def reconstruct_branch(graph: HydrationGraph, data_ref: int) -> tuple[int, ...]:
    mapping_ref = graph.field_ref(data_ref, "mapping")
    current_node = graph.field(data_ref, "current_node")
    if mapping_ref is None or not isinstance(current_node, str):
        raise ParseError("share mapping or current_node is missing")
    mapping = graph.object_refs(mapping_ref)
    roots: list[str] = []

    for mapped_id, node_ref in mapping.items():
        if not isinstance(mapped_id, str):
            raise ParseError("mapping contains a non-string node id")
        parent_ref = graph.field_ref(node_ref, "parent")
        if parent_ref is None:
            if graph.field_ref(node_ref, "message") is not None:
                raise ParseError(f"message-bearing node {mapped_id!r} is missing parent")
            roots.append(mapped_id)
            continue
        parent = graph.value(parent_ref)
        if not isinstance(parent, str) or not parent:
            raise ParseError(f"invalid parent for node {mapped_id!r}")

    if len(roots) != 1:
        raise ParseError("mapping must contain exactly one message-less root without parent")
    root_id = roots[0]
    branch: list[int] = []
    seen: set[str] = set()
    node_id: object = current_node

    while True:
        if not isinstance(node_id, str) or node_id in seen:
            raise ParseError("invalid or cyclic active conversation branch")
        seen.add(node_id)
        node_ref = mapping.get(node_id)
        if node_ref is None:
            raise ParseError(f"mapping missing node {node_id!r}")
        branch.append(node_ref)
        if node_id == root_id:
            break
        node_id = graph.field(node_ref, "parent")

    branch.reverse()
    return tuple(branch)


def project_visible(graph: HydrationGraph, branch: tuple[int, ...]) -> tuple[int, ...]:
    visible: list[int] = []
    for index, node_ref in enumerate(branch):
        message_ref = graph.field_ref(node_ref, "message")
        if message_ref is None:
            if index == 0:
                continue
            raise ParseError("unexpected message-less node in active conversation branch")
        author_ref = graph.field_ref(message_ref, "author")
        content_ref = graph.field_ref(message_ref, "content")
        role = graph.field(author_ref, "role")
        content_type = graph.field(content_ref, "content_type")
        recipient = graph.field(message_ref, "recipient")
        metadata_ref = graph.field_ref(message_ref, "metadata")

        if graph.field(metadata_ref, "is_visually_hidden_from_conversation") is True:
            continue
        if role in {"system", "tool"}:
            continue
        if role == "user":
            if graph.field(metadata_ref, "is_user_system_message") is True:
                continue
            if content_type not in {"text", "multimodal_text"}:
                raise UnsupportedContentError(f"unsupported visible user content type {content_type!r}")
            visible.append(message_ref)
            continue
        if role == "assistant":
            if graph.field(metadata_ref, "is_thinking_preamble_message") is True:
                continue
            if content_type in {
                "code", "execution_output", "model_editable_context", "reasoning_recap", "thoughts"
            }:
                continue
            if content_type != "text":
                raise UnsupportedContentError(f"unsupported visible assistant content type {content_type!r}")
            if recipient == "all":
                visible.append(message_ref)
            elif isinstance(recipient, str) and recipient:
                continue
            else:
                raise ParseError("visible assistant text has missing or malformed recipient")
            continue
        raise UnsupportedContentError(f"unsupported visible message role {role!r}")
    return tuple(visible)


def _optional_text(graph: HydrationGraph, obj_ref: int, field: str) -> str | None:
    value = graph.field(obj_ref, field)
    return value if isinstance(value, str) and value.strip() else None


@dataclass(frozen=True)
class _VisibleAnnotation:
    start: int
    end: int
    filename: str | None = None


def _reference_anchor(
    graph: HydrationGraph, reference_ref: int, text: str
) -> tuple[int, int]:
    start = graph.field(reference_ref, "start_idx")
    end = graph.field(reference_ref, "end_idx")
    marker = graph.field(reference_ref, "matched_text")
    if (
        not isinstance(start, int)
        or isinstance(start, bool)
        or not isinstance(end, int)
        or isinstance(end, bool)
        or start < 0
        or end <= start
        or end > len(text)
        or not isinstance(marker, str)
    ):
        raise ParseError("active citation anchor or marker is malformed")
    if text[start:end] != marker:
        raise ParseError("active citation marker does not match its anchor")
    return start, end


def _visible_annotations(
    graph: HydrationGraph, message_ref: int, text: str
) -> tuple[_VisibleAnnotation, ...]:
    metadata_ref = graph.field_ref(message_ref, "metadata")
    references_ref = graph.field_ref(metadata_ref, "content_references")
    if references_ref is None:
        return ()

    annotations: list[_VisibleAnnotation] = []
    for reference_ref in graph.list_refs(references_ref):
        if not isinstance(reference_ref, int) or not isinstance(graph.value(reference_ref), dict):
            raise ParseError("content reference is malformed")
        reference_type = graph.field(reference_ref, "type")
        if reference_type in {"sources_footnote", "hidden", "grouped_webpages"}:
            continue
        if reference_type == "file":
            start, end = _reference_anchor(graph, reference_ref, text)
            filename = graph.field(reference_ref, "name")
            if not isinstance(filename, str) or not filename:
                raise ParseError("visible file attachment filename is missing")
            annotations.append(_VisibleAnnotation(start, end, filename))
            continue
        if reference_type == "followup_a":
            start, end = _reference_anchor(graph, reference_ref, text)
            annotations.append(_VisibleAnnotation(start, end))
            continue
        if graph.field_ref(reference_ref, "matched_text") is not None:
            raise UnsupportedContentError(
                f"unsupported visible citation type {reference_type!r}"
            )

    annotations.sort(key=lambda item: (item.start, item.end))
    for previous, current in pairwise(annotations):
        if current.start < previous.end:
            raise ParseError("visible annotation ranges overlap")
    return tuple(annotations)


def _project_parts(
    parts: list[TextPart | ImagePart], annotations: tuple[_VisibleAnnotation, ...]
) -> tuple[TextPart | ImagePart | FilePart, ...]:
    if not annotations:
        return tuple(parts)

    projected: list[TextPart | ImagePart | FilePart] = []
    annotation_index = 0
    text_offset = 0
    for part in parts:
        if not isinstance(part, TextPart):
            projected.append(part)
            continue

        part_start = text_offset
        part_end = part_start + len(part.text)
        if annotation_index < len(annotations) and annotations[annotation_index].start < part_start:
            raise ParseError("visible annotation anchor is outside text parts")
        part_annotations: list[_VisibleAnnotation] = []
        while annotation_index < len(annotations) and annotations[annotation_index].start < part_end:
            annotation = annotations[annotation_index]
            if annotation.end > part_end:
                raise ParseError("visible annotation crosses a content part boundary")
            part_annotations.append(annotation)
            annotation_index += 1

        cursor = 0
        for annotation in part_annotations:
            local_start = annotation.start - part_start
            local_end = annotation.end - part_start
            if local_start > cursor:
                projected.append(TextPart(part.text[cursor:local_start]))
            if annotation.filename is not None:
                projected.append(FilePart(annotation.filename))
            cursor = local_end
        if cursor < len(part.text):
            projected.append(TextPart(part.text[cursor:]))
        text_offset = part_end

    if annotation_index != len(annotations):
        raise ParseError("visible annotation anchor is outside text parts")
    return tuple(projected)


def _citation_items(graph: HydrationGraph, reference_ref: int) -> list[int]:
    items_ref = graph.field_ref(reference_ref, "items")
    if items_ref is None:
        raise ParseError("active citation items are missing")
    items: list[int] = []
    for item_ref in graph.list_refs(items_ref):
        if not isinstance(item_ref, int) or not isinstance(graph.value(item_ref), dict):
            raise ParseError("active citation item is malformed")
        items.append(item_ref)
        supporting_ref = graph.field_ref(item_ref, "supporting_websites")
        if supporting_ref is not None:
            for supporting in graph.list_refs(supporting_ref):
                if not isinstance(supporting, int) or not isinstance(graph.value(supporting), dict):
                    raise ParseError("active citation supporting website is malformed")
                items.append(supporting)
    return items


def _normalize_citations(graph: HydrationGraph, message_ref: int, text: str) -> tuple[Citation, ...]:
    metadata_ref = graph.field_ref(message_ref, "metadata")
    references_ref = graph.field_ref(metadata_ref, "content_references")
    if references_ref is None:
        return ()

    citations: list[Citation] = []
    for reference_ref in graph.list_refs(references_ref):
        if not isinstance(reference_ref, int) or not isinstance(graph.value(reference_ref), dict):
            raise ParseError("content reference is malformed")
        reference_type = graph.field(reference_ref, "type")
        if reference_type in {"sources_footnote", "hidden", "file", "followup_a"}:
            continue
        if reference_type != "grouped_webpages":
            if graph.field_ref(reference_ref, "matched_text") is not None:
                raise UnsupportedContentError(
                    f"unsupported visible citation type {reference_type!r}"
                )
            continue
        if graph.field(reference_ref, "style") == "hidden" or graph.field(
            reference_ref, "status"
        ) in {"loading", "error"}:
            continue

        items = _citation_items(graph, reference_ref)
        if not items:
            continue
        marker = graph.field(reference_ref, "matched_text")
        start, end = _reference_anchor(graph, reference_ref, text)
        if not isinstance(marker, str):
            raise ParseError("active citation anchor or marker is malformed")
        start_byte = len(text[:start].encode("utf-8"))
        end_byte = len(text[:end].encode("utf-8"))

        for item_ref in items:
            url = graph.field(item_ref, "url")
            if not isinstance(url, str):
                raise ParseError("active citation destination URL is missing")
            try:
                parsed = urlsplit(url)
            except ValueError as error:
                raise ParseError("active citation destination URL is not absolute") from error
            if not parsed.scheme or not parsed.netloc:
                raise ParseError("active citation destination URL is not absolute")
            citations.append(Citation(
                start_byte,
                end_byte,
                marker,
                url,
                _optional_text(graph, item_ref, "title"),
                _optional_text(graph, item_ref, "attribution")
                or _optional_text(graph, item_ref, "source_name"),
                _optional_text(graph, item_ref, "snippet"),
            ))
    return tuple(citations)


def normalize(
    graph: HydrationGraph,
    message_refs: tuple[int, ...],
    title: str | None = None,
) -> Conversation:
    messages: list[Message] = []
    for message_ref in message_refs:
        author_ref = graph.field_ref(message_ref, "author")
        content_ref = graph.field_ref(message_ref, "content")
        role = graph.field(author_ref, "role")
        content_type = graph.field(content_ref, "content_type")
        parts_ref = graph.field_ref(content_ref, "parts")
        if (
            not isinstance(role, str)
            or role not in {"user", "assistant"}
            or not isinstance(content_type, str)
            or content_type not in {"text", "multimodal_text"}
            or parts_ref is None
        ):
            raise ParseError("projected message is malformed")

        parts: list[TextPart | ImagePart] = []
        for part_ref in graph.list_refs(parts_ref):
            part = graph.value(part_ref)
            if isinstance(part, str):
                parts.append(TextPart(part))
                continue
            if isinstance(part, dict):
                part_type = graph.field(part_ref, "content_type")
                pointer = graph.field(part_ref, "asset_pointer")
                if (
                    content_type == "multimodal_text"
                    and part_type == "image_asset_pointer"
                    and isinstance(pointer, str)
                ):
                    parts.append(ImagePart(pointer))
                    continue
                raise UnsupportedContentError(f"unsupported visible multimodal part type {part_type!r}")
            raise UnsupportedContentError(f"unsupported visible multimodal part {type(part).__name__}")
        source_text = "".join(part.text for part in parts if isinstance(part, TextPart))
        annotations = _visible_annotations(graph, message_ref, source_text)
        citations = _normalize_citations(graph, message_ref, source_text)
        messages.append(Message(role, content_type, _project_parts(parts, annotations), citations))
    return Conversation(title, tuple(messages))


def parse_share_html(html: str) -> Conversation:
    graph = decode_hydration(html)
    data_ref = locate_share_data(graph)
    branch = reconstruct_branch(graph, data_ref)
    title = graph.field(data_ref, "title")
    if title is not None and not isinstance(title, str):
        raise ParseError("share title is malformed")
    return normalize(graph, project_visible(graph, branch), title)


def parse_share(url: str, fetcher: Callable[[str], str] = fetch_share) -> Conversation:
    return parse_share_html(fetcher(url))


_IMAGE_PLACEHOLDER = "[Image in original conversation]"
_ROLE_HEADINGS = {"user": "User", "assistant": "ChatGPT"}


def serialize_conversation(conversation: Conversation, source_url: str) -> str:
    title = conversation.title if conversation.title is not None else "conversation"
    sections = [f"# {title}", f"> Source: {source_url}"]
    for message in conversation.messages:
        try:
            role_heading = _ROLE_HEADINGS[message.role]
        except KeyError as error:
            raise ParseError(f"unsupported visible message role {message.role!r}") from error
        content: list[str] = []
        for part in message.parts:
            if isinstance(part, TextPart):
                content.append(part.text)
            elif isinstance(part, ImagePart):
                content.append(_IMAGE_PLACEHOLDER)
            elif isinstance(part, FilePart):
                content.append(f"[File: {part.filename}]")
            else:
                raise UnsupportedContentError(
                    f"unsupported normalized conversation part {type(part).__name__}"
                )
        sections.extend(("---", f"**{role_heading}**", "".join(content)))
    return "\n\n".join(sections) + "\n"


def safe_filename(title: str | None) -> str:
    candidate = "" if title is None else title
    while candidate:
        trimmed = candidate.strip().strip(".")
        if trimmed == candidate:
            break
        candidate = trimmed
    candidate = "".join(
        "_" if char in "/\\" or unicodedata.category(char) == "Cc" else char
        for char in candidate
    )
    candidate = re.sub(r"\s+", " ", candidate).strip()
    return candidate or "conversation"


def _has_meaningful_content(conversation: Conversation) -> bool:
    return any(
        (isinstance(part, TextPart) and bool(part.text.strip()))
        or isinstance(part, ImagePart)
        or (isinstance(part, FilePart) and bool(part.filename.strip()))
        for message in conversation.messages
        for part in message.parts
    )


def _capture_date() -> date:
    return datetime.now(timezone.utc).astimezone().date()


def _capture_directory(capture_root: Path | None = None) -> Path:
    root = CAPTURE_ROOT if capture_root is None else capture_root
    capture_date = _capture_date()
    return root / f"{capture_date:%Y}" / f"{capture_date:%m}"


def write_markdown(
    conversation: Conversation,
    source_url: str,
    capture_root: Path | None = None,
) -> Path:
    if not _has_meaningful_content(conversation):
        raise ParseError("conversation has no meaningful content")
    body = serialize_conversation(conversation, source_url)
    output_dir = _capture_directory(capture_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"{safe_filename(conversation.title)}.md"
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.",
        dir=output_dir,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as temporary:
            descriptor = -1
            temporary.write(body)
            temporary.flush()
            os.fsync(temporary.fileno())
        candidate = target
        suffix = 2
        while True:
            try:
                os.link(temporary_name, candidate)
                return candidate.resolve()
            except FileExistsError:
                candidate = output_dir / f"{target.stem}-{suffix}{target.suffix}"
                suffix += 1
    finally:
        if descriptor != -1:
            os.close(descriptor)
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass


def _validate_share_url(url: str) -> None:
    if not url or any(ord(char) < 32 or ord(char) == 127 for char in url):
        raise ValueError("expected an absolute HTTP(S) share URL")
    try:
        parsed = urlsplit(url)
    except ValueError as error:
        raise ValueError("invalid share URL") from error
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("expected an absolute HTTP(S) share URL")


def _capture_complete_message(output: Path, source_url: str) -> str:
    return (
        "CAPTURE COMPLETE\n"
        "\n"
        "Saved:\n"
        f"{output}\n"
        "\n"
        "Shared source:\n"
        f"{source_url}\n"
        "\n"
        "SECURITY:\n"
        "This shared link still exists.\n"
        "Revoke it in ChatGPT > Settings > Data Controls > Shared Links."
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="chatmd")
    parser.add_argument("url", help="one public ChatGPT share URL")
    arguments = parser.parse_args(argv)
    try:
        _validate_share_url(arguments.url)
        conversation = parse_share(arguments.url)
        output = write_markdown(conversation, arguments.url)
        print(_capture_complete_message(output, arguments.url))
    except (OSError, ParseError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
