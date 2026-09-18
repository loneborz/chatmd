from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
import json
from typing import Callable
from urllib.request import urlopen


ROUTE = "routes/share.$shareId.($action)"
MARKER = "window.__reactRouterContext.streamController.enqueue("


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
class Message:
    role: str
    source_type: str
    parts: tuple[TextPart | ImagePart, ...]


@dataclass(frozen=True)
class Conversation:
    messages: tuple[Message, ...]


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


def fetch_share(url: str, opener: Callable[..., object] = urlopen) -> str:
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


def normalize(graph: HydrationGraph, message_refs: tuple[int, ...]) -> Conversation:
    messages: list[Message] = []
    for message_ref in message_refs:
        author_ref = graph.field_ref(message_ref, "author")
        content_ref = graph.field_ref(message_ref, "content")
        role = graph.field(author_ref, "role")
        content_type = graph.field(content_ref, "content_type")
        parts_ref = graph.field_ref(content_ref, "parts")
        if role not in {"user", "assistant"} or content_type not in {"text", "multimodal_text"} or parts_ref is None:
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
        messages.append(Message(role, content_type, tuple(parts)))
    return Conversation(tuple(messages))


def parse_share_html(html: str) -> Conversation:
    graph = decode_hydration(html)
    data_ref = locate_share_data(graph)
    branch = reconstruct_branch(graph, data_ref)
    return normalize(graph, project_visible(graph, branch))


def parse_share(url: str, fetcher: Callable[[str], str] = fetch_share) -> Conversation:
    return parse_share_html(fetcher(url))
