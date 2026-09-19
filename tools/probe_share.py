#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROUTE = "routes/share.$shareId.($action)"
MARKER = "window.__reactRouterContext.streamController.enqueue("


class ScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.current: list[str] | None = None
        self.scripts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.current = []

    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.current is not None:
            self.scripts.append("".join(self.current))
            self.current = None


def extract_slots(html: str) -> list:
    parser = ScriptParser()
    parser.feed(html)

    decoder = json.JSONDecoder()
    candidates = []

    for script in parser.scripts:
        cursor = 0

        while True:
            i = script.find(MARKER, cursor)
            if i == -1:
                break

            start = i + len(MARKER)

            try:
                chunk, consumed = decoder.raw_decode(script[start:])
            except json.JSONDecodeError:
                break

            try:
                value = json.loads(chunk)
            except json.JSONDecodeError:
                cursor = start + consumed
                continue

            if isinstance(value, list):
                candidates.append(value)

            cursor = start + consumed

    if not candidates:
        raise RuntimeError("no React Router slot payload found")

    return max(candidates, key=len)


class Graph:
    def __init__(self, slots: list) -> None:
        self.slots = slots

    def value(self, ref):
        if isinstance(ref, int) and ref >= 0:
            return self.slots[ref]
        return None

    def field_ref(self, obj_ref, wanted_key: str):
        obj = self.value(obj_ref)

        if not isinstance(obj, dict):
            return None

        for encoded_key, value_ref in obj.items():
            if not encoded_key.startswith("_"):
                continue

            key_ref = int(encoded_key[1:])
            if self.slots[key_ref] == wanted_key:
                return value_ref

        return None

    def field(self, obj_ref, wanted_key: str):
        ref = self.field_ref(obj_ref, wanted_key)
        return self.value(ref)

    def object_refs(self, obj_ref) -> dict:
        obj = self.value(obj_ref)

        if not isinstance(obj, dict):
            return {}

        out = {}

        for encoded_key, value_ref in obj.items():
            if not encoded_key.startswith("_"):
                continue

            out[self.slots[int(encoded_key[1:])]] = value_ref

        return out

    def list_refs(self, list_ref) -> list:
        value = self.value(list_ref)
        return value if isinstance(value, list) else []


def share_data_ref(g: Graph) -> int:
    loader = g.field_ref(0, "loaderData")
    route = g.field_ref(loader, ROUTE)
    server = g.field_ref(route, "serverResponse")
    data = g.field_ref(server, "data")

    if data is None:
        raise RuntimeError("share serverResponse.data not found")

    return data


def canonical_branch(g: Graph, data_ref: int) -> list[int]:
    mapping_ref = g.field_ref(data_ref, "mapping")
    current_id = g.field(data_ref, "current_node")
    mapping = g.object_refs(mapping_ref)

    branch = []
    node_id = current_id

    while node_id is not None:
        node_ref = mapping.get(node_id)

        if node_ref is None:
            raise RuntimeError(f"mapping missing node {node_id!r}")

        branch.append(node_ref)

        parent_id = g.field(node_ref, "parent")
        if not parent_id:
            break

        node_id = parent_id

    branch.reverse()
    return branch


def message_summary(g: Graph, node_ref: int) -> dict:
    message_ref = g.field_ref(node_ref, "message")

    if message_ref is None:
        return {
            "node_id": g.field(node_ref, "id"),
            "message": None,
        }

    author_ref = g.field_ref(message_ref, "author")
    content_ref = g.field_ref(message_ref, "content")
    metadata_ref = g.field_ref(message_ref, "metadata")

    role = g.field(author_ref, "role")
    recipient = g.field(message_ref, "recipient")
    content_type = g.field(content_ref, "content_type")

    flags = {}

    for key in (
        "is_visually_hidden_from_conversation",
        "is_user_system_message",
        "is_thinking_preamble_message",
        "hide_inline_actions",
        "disable_turn_actions",
    ):
        value = g.field(metadata_ref, key)
        if value is not None:
            flags[key] = value

    parts = []

    parts_ref = g.field_ref(content_ref, "parts")
    if parts_ref is not None:
        for ref in g.list_refs(parts_ref):
            value = g.value(ref)

            if isinstance(value, str):
                parts.append({
                    "kind": "text",
                    "value": value,
                })
            else:
                parts.append({
                    "kind": type(value).__name__,
                })

    return {
        "node_id": g.field(node_ref, "id"),
        "message": {
            "id": g.field(message_ref, "id"),
            "role": role,
            "recipient": recipient,
            "content_type": content_type,
            "flags": flags,
            "parts": parts,
        },
    }


def probe(path: Path) -> dict:
    slots = extract_slots(path.read_text(errors="replace"))
    g = Graph(slots)
    data_ref = share_data_ref(g)

    branch = canonical_branch(g, data_ref)
    messages = [message_summary(g, ref) for ref in branch]

    linear_ref = g.field_ref(data_ref, "linear_conversation")
    linear_ids = [
        g.field(ref, "id")
        for ref in g.list_refs(linear_ref)
    ]

    branch_ids = [item["node_id"] for item in messages]

    classifications = Counter()

    for item in messages:
        message = item["message"]

        if message is None:
            classifications["root"] += 1
            continue

        key = (
            message["role"],
            message["content_type"],
            message["recipient"],
        )
        classifications[str(key)] += 1

    content_types = Counter(
        item["message"]["content_type"]
        for item in messages
        if item["message"] is not None
    )

    return {
        "fixture": path.name,
        "title": g.field(data_ref, "title"),
        "conversation_id": g.field(data_ref, "conversation_id"),
        "current_node": g.field(data_ref, "current_node"),
        "slot_count": len(slots),
        "branch_node_count": len(branch),
        "linear_node_count": len(linear_ids),
        "linear_matches_mapping_branch": branch_ids == linear_ids,
        "content_types": dict(content_types),
        "classifications": dict(classifications),
        "messages": messages,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    result = [probe(path) for path in args.files]

    text = json.dumps(result, ensure_ascii=False, indent=2)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n")
        print(args.out)
    else:
        print(text)


if __name__ == "__main__":
    main()
