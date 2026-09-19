import io
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from email.message import Message as Headers
from pathlib import Path
from unittest.mock import patch

import chatmd

REPO_ROOT = Path(__file__).resolve().parent

CAPTURE_DATE = date(2026, 9, 19)
SOURCE_URL = "https://chatgpt.com/share/example"
POST_CAPTURE_SUCCESS_MARKERS = (
    "CAPTURE COMPLETE",
    "Saved:",
    "Shared source:",
    "SECURITY:",
    "This shared link still exists.",
    "ChatGPT > Settings > Data Controls > Shared Links",
)


def user_conversation(title: str | None = "Capture", text: str = "hello") -> chatmd.Conversation:
    return chatmd.Conversation(
        title,
        (chatmd.Message("user", "text", (chatmd.TextPart(text),)),),
    )


def markdown_files(root: Path) -> list[Path]:
    return sorted(
        path.resolve()
        for path in root.rglob("*.md")
        if not path.name.startswith(".")
    )


def capture_complete_text(path: Path, source_url: str) -> str:
    return (
        "CAPTURE COMPLETE\n"
        "\n"
        "Saved:\n"
        f"{path}\n"
        "\n"
        "Shared source:\n"
        f"{source_url}\n"
        "\n"
        "SECURITY:\n"
        "This shared link still exists.\n"
        "Revoke it in ChatGPT > Settings > Data Controls > Shared Links.\n"
    )


def assert_no_successful_capture_result(test: unittest.TestCase, *streams: str) -> None:
    combined = "".join(streams)
    for marker in POST_CAPTURE_SUCCESS_MARKERS:
        test.assertNotIn(marker, combined)

MISSING = object()


class Slots:
    def __init__(self) -> None:
        self.values: list[object] = []

    def add(self, value: object) -> int:
        self.values.append(value)
        return len(self.values) - 1

    def text(self, value: str) -> int:
        return self.add(value)

    def obj(self, **fields: int) -> int:
        return self.add({f"_{self.text(key)}": value for key, value in fields.items()})

    def array(self, *refs: int) -> int:
        return self.add(list(refs))

    def encode(self, value: object) -> int:
        if isinstance(value, dict):
            return self.obj(**{key: self.encode(item) for key, item in value.items()})
        if isinstance(value, list):
            return self.array(*(self.encode(item) for item in value))
        return self.add(value)


def citation_fixture(
    text: str,
    references: list[dict[str, object]] | None = None,
    title: object = MISSING,
) -> str:
    s = Slots()
    s.add({})

    def message(role: str, body: str, content_references: list[dict[str, object]] | None = None) -> int:
        metadata_fields = {}
        if content_references is not None:
            metadata_fields["content_references"] = s.encode(content_references)
        return s.obj(
            author=s.obj(role=s.text(role)),
            content=s.obj(content_type=s.text("text"), parts=s.array(s.text(body))),
            metadata=s.obj(**metadata_fields),
            recipient=s.text("all"),
        )

    root = s.obj(id=s.text("root"))
    user = s.obj(
        id=s.text("user"), parent=s.text("root"), message=message("user", "question")
    )
    assistant = s.obj(
        id=s.text("assistant"), parent=s.text("user"),
        message=message("assistant", text, references),
    )
    mapping = s.obj(root=root, user=user, assistant=assistant)
    data_fields = {"mapping": mapping, "current_node": s.text("assistant")}
    if title is not MISSING:
        data_fields["title"] = s.encode(title)
    data = s.obj(**data_fields)
    loader = s.obj(**{chatmd.ROUTE: s.obj(serverResponse=s.obj(data=data))})
    s.values[0] = {f"_{s.text('loaderData')}": loader}
    return f"<script>{chatmd.MARKER}{json.dumps(json.dumps(s.values))})</script>"


def grouped_reference(
    marker: str,
    start: object,
    end: object,
    *,
    url: object = "https://example.com/exact?b=2&a=1#fragment",
    **item_fields: object,
) -> dict[str, object]:
    item = {"url": url, **item_fields}
    return {
        "type": "grouped_webpages",
        "matched_text": marker,
        "start_idx": start,
        "end_idx": end,
        "status": "done",
        "style": None,
        "items": [item],
    }


def fixture(
    *,
    assistant_recipient: object = "all",
    unexpected_message_less: bool = False,
    unknown_content: bool = False,
    unknown_part: bool = False,
) -> str:
    s = Slots()
    s.add({})
    all_ref = s.text("all")

    def message(
        role: str,
        content_type: str,
        parts: tuple[int, ...],
        recipient: object = "all",
        **flags: bool,
    ) -> int:
        author = s.obj(role=s.text(role))
        content = s.obj(content_type=s.text(content_type), parts=s.array(*parts))
        metadata = s.obj(**{key: s.add(value) for key, value in flags.items()})
        fields = {"author": author, "content": content, "metadata": metadata}
        if recipient is not None:
            fields["recipient"] = all_ref if recipient == "all" else s.add(recipient)
        return s.obj(**fields)

    root = s.obj(id=s.text("root"))
    image = s.obj(
        content_type=s.text("video_pointer" if unknown_part else "image_asset_pointer"),
        asset_pointer=s.text("sediment://asset/example"),
    )
    user_text = s.text("  exact **source**\n\n")
    user = s.obj(
        id=s.text("user"), parent=s.text("root"),
        message=message(
            "user", "audio" if unknown_content else "multimodal_text", (user_text, image)
        ),
    )
    user_system = s.obj(
        id=s.text("user_system"), parent=s.text("user"),
        message=message(
            "user", "text", (s.text("user system"),), is_user_system_message=True
        ),
    )
    system = s.obj(
        id=s.text("system"), parent=s.text("user_system"),
        message=message("system", "text", (s.text("system"),)),
    )
    tool = s.obj(
        id=s.text("tool"), parent=s.text("system"),
        message=message("tool", "text", (s.text("tool"),)),
    )
    tool_directed = s.obj(
        id=s.text("tool_directed"), parent=s.text("tool"),
        message=message("assistant", "text", (s.text("tool call"),), recipient="web.run"),
    )
    code = s.obj(
        id=s.text("code"), parent=s.text("tool_directed"),
        message=message("assistant", "code", (s.text("code"),), recipient="python"),
    )
    execution = s.obj(
        id=s.text("execution"), parent=s.text("code"),
        message=message("assistant", "execution_output", (s.text("output"),)),
    )
    recap = s.obj(
        id=s.text("recap"), parent=s.text("execution"),
        message=message("assistant", "reasoning_recap", (s.text("recap"),)),
    )
    reasoning = s.obj(
        id=s.text("reasoning"), parent=s.text("recap"),
        message=message("assistant", "thoughts", (s.text("not visible"),)),
    )
    context = s.obj(
        id=s.text("context"), parent=s.text("reasoning"),
        message=message("assistant", "model_editable_context", (s.text("context"),)),
    )
    preamble = s.obj(
        id=s.text("preamble"), parent=s.text("context"),
        message=message(
            "assistant", "text", (s.text("preamble"),), is_thinking_preamble_message=True
        ),
    )
    assistant_fields = {
        "id": s.text("assistant"),
        "parent": s.text("preamble"),
    }
    if not unexpected_message_less:
        assistant_fields["message"] = message(
            "assistant", "text", (s.text("answer"),), recipient=assistant_recipient
        )
    assistant = s.obj(**assistant_fields)
    hidden = s.obj(
        id=s.text("hidden"), parent=s.text("assistant"),
        message=message(
            "assistant", "text", (s.text("secret"),),
            is_visually_hidden_from_conversation=True,
        ),
    )
    mapping = s.obj(
        root=root, user=user, user_system=user_system, system=system, tool=tool,
        tool_directed=tool_directed, code=code, execution=execution, recap=recap,
        reasoning=reasoning, context=context, preamble=preamble, assistant=assistant,
        hidden=hidden,
    )
    data = s.obj(mapping=mapping, current_node=s.text("hidden"))
    server = s.obj(data=data)
    route = s.obj(serverResponse=server)
    loader = s.obj(**{chatmd.ROUTE: route})
    s.values[0] = {f"_{s.text('loaderData')}": loader}
    encoded = json.dumps(json.dumps(s.values))
    return f"<script>{chatmd.MARKER}{encoded})</script>"


class FakeResponse:
    def __init__(self, body: bytes) -> None:
        self.body = body
        self.headers = Headers()
        self.headers["Content-Type"] = "text/html; charset=utf-8"

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self) -> bytes:
        return self.body


class ParserTests(unittest.TestCase):
    def test_boundaries_and_normalized_visible_branch(self) -> None:
        html = fixture()
        graph = chatmd.decode_hydration(html)
        data_ref = chatmd.locate_share_data(graph)
        branch = chatmd.reconstruct_branch(graph, data_ref)
        visible = chatmd.project_visible(graph, branch)

        self.assertEqual(len(branch), 14)
        self.assertEqual(len(visible), 2)
        self.assertEqual(
            chatmd.normalize(graph, visible),
            chatmd.Conversation(None, (
                chatmd.Message("user", "multimodal_text", (
                    chatmd.TextPart("  exact **source**\n\n"),
                    chatmd.ImagePart("sediment://asset/example"),
                )),
                chatmd.Message("assistant", "text", (chatmd.TextPart("answer"),)),
            )),
        )

    def test_title_is_exact_or_explicitly_absent(self) -> None:
        self.assertEqual(
            chatmd.parse_share_html(citation_fixture("answer", title="  Exact title  ")).title,
            "  Exact title  ",
        )
        self.assertIsNone(chatmd.parse_share_html(citation_fixture("answer")).title)

    def test_active_citation_preserves_text_and_converts_code_points_to_utf8_bytes(self) -> None:
        marker = "\ue200cite\ue202source\ue201"
        text = f"é {marker} unchanged"
        reference = grouped_reference(
            marker,
            2,
            2 + len(marker),
            title="Exact source title",
            attribution="Exact attribution",
            snippet="Exact supporting snippet",
        )

        conversation = chatmd.parse_share_html(citation_fixture(text, [reference]))

        self.assertEqual(conversation.messages[1].parts, (chatmd.TextPart(text),))
        self.assertEqual(conversation.messages[1].citations, (
            chatmd.Citation(
                3,
                3 + len(marker.encode()),
                marker,
                "https://example.com/exact?b=2&a=1#fragment",
                "Exact source title",
                "Exact attribution",
                "Exact supporting snippet",
            ),
        ))

    def test_repeated_markers_keep_distinct_anchors(self) -> None:
        marker = "\ue200cite\ue202same\ue201"
        text = f"{marker} and {marker}"
        second = len(marker) + 5
        references = [
            grouped_reference(marker, 0, len(marker)),
            grouped_reference(marker, second, second + len(marker), url="https://example.org/two"),
        ]

        citations = chatmd.parse_share_html(citation_fixture(text, references)).messages[1].citations

        self.assertEqual([(item.start_byte, item.end_byte) for item in citations], [
            (0, len(marker.encode())),
            (len(f"{marker} and ".encode()), len(text.encode())),
        ])

    def test_marker_shaped_text_without_structured_reference_is_ordinary_text(self) -> None:
        text = "ordinary \ue200cite\ue202not-active\ue201 text"
        message = chatmd.parse_share_html(citation_fixture(text)).messages[1]
        self.assertEqual(message.parts, (chatmd.TextPart(text),))
        self.assertEqual(message.citations, ())

    def test_hidden_reference_is_excluded_without_rewriting_message_text(self) -> None:
        marker = "\ue200memcite\ue201"
        text = f"before {marker} after"
        reference = {
            "type": "hidden",
            "matched_text": marker,
            "start_idx": len("before "),
            "end_idx": len("before ") + len(marker),
            "invalid": False,
            "refs": [],
            "safe_urls": [],
        }

        message = chatmd.parse_share_html(citation_fixture(text, [reference])).messages[1]

        self.assertEqual(message.parts, (chatmd.TextPart(text),))
        self.assertEqual(message.citations, ())

    def test_file_reference_becomes_a_structural_part_at_its_anchor(self) -> None:
        marker = "\ue200filecite\ue202turn0file0\ue201"
        text = f"before {marker} after"
        reference = {
            "type": "file",
            "matched_text": marker,
            "start_idx": len("before "),
            "end_idx": len("before ") + len(marker),
            "name": "notes.md",
        }

        message = chatmd.parse_share_html(citation_fixture(text, [reference])).messages[1]

        self.assertEqual(message.parts, (
            chatmd.TextPart("before "),
            chatmd.FilePart("notes.md"),
            chatmd.TextPart(" after"),
        ))
        self.assertEqual(message.citations, ())

    def test_followup_reference_removes_only_its_anchored_control_text(self) -> None:
        label = "Ask a follow-up"
        text = f"before {label} after"
        reference = {
            "type": "followup_a",
            "matched_text": label,
            "start_idx": len("before "),
            "end_idx": len("before ") + len(label),
            "prompt_text": "Ask a follow-up with more detail",
        }

        message = chatmd.parse_share_html(citation_fixture(text, [reference])).messages[1]

        self.assertEqual(message.parts, (
            chatmd.TextPart("before "),
            chatmd.TextPart(" after"),
        ))
        self.assertEqual(message.citations, ())

    def test_optional_citation_fields_are_not_synthesized(self) -> None:
        marker = "\ue200cite\ue202source\ue201"
        citation = chatmd.parse_share_html(citation_fixture(
            marker, [grouped_reference(marker, 0, len(marker))]
        )).messages[1].citations[0]
        self.assertIsNone(citation.title)
        self.assertIsNone(citation.attribution)
        self.assertIsNone(citation.snippet)

    def test_inactive_structured_reference_is_not_a_citation(self) -> None:
        marker = "\ue200cite\ue202source\ue201"
        for field, value in (("style", "hidden"), ("status", "loading"), ("status", "error")):
            with self.subTest(field=field, value=value):
                reference = grouped_reference(marker, 0, len(marker))
                reference[field] = value
                message = chatmd.parse_share_html(citation_fixture(marker, [reference])).messages[1]
                self.assertEqual(message.citations, ())

    def test_malformed_active_citations_fail_visibly(self) -> None:
        marker = "\ue200cite\ue202source\ue201"
        cases = {
            "anchor or marker": grouped_reference(marker, None, len(marker)),
            "does not match": grouped_reference(marker, 1, len(marker)),
            "URL is missing": grouped_reference(marker, 0, len(marker), url=None),
            "URL is not absolute": grouped_reference(marker, 0, len(marker), url="relative/path"),
        }
        for error, reference in cases.items():
            with self.subTest(error=error), self.assertRaisesRegex(chatmd.ParseError, error):
                chatmd.parse_share_html(citation_fixture(marker, [reference]))

    def test_unsupported_anchored_reference_type_fails_visibly(self) -> None:
        marker = "\ue200cite\ue202source\ue201"
        reference: dict[str, object] = {"type": "future_citation", "matched_text": marker}
        with self.assertRaisesRegex(chatmd.UnsupportedContentError, "citation type"):
            chatmd.parse_share_html(citation_fixture(marker, [reference]))

    def test_production_parser_boundary(self) -> None:
        self.assertEqual(chatmd.parse_share_html(fixture()).messages[0].role, "user")

    def test_unknown_visible_content_fails(self) -> None:
        with self.assertRaisesRegex(chatmd.UnsupportedContentError, "visible user content"):
            chatmd.parse_share_html(fixture(unknown_content=True))

    def test_unknown_visible_multimodal_part_fails(self) -> None:
        with self.assertRaisesRegex(chatmd.UnsupportedContentError, "multimodal part"):
            chatmd.parse_share_html(fixture(unknown_part=True))

    def test_unexpected_message_less_branch_node_fails(self) -> None:
        with self.assertRaisesRegex(chatmd.ParseError, "unexpected message-less node"):
            chatmd.parse_share_html(fixture(unexpected_message_less=True))

    def test_missing_assistant_recipient_fails(self) -> None:
        with self.assertRaisesRegex(chatmd.ParseError, "missing or malformed recipient"):
            chatmd.parse_share_html(fixture(assistant_recipient=None))

    def test_malformed_assistant_recipient_fails(self) -> None:
        with self.assertRaisesRegex(chatmd.ParseError, "missing or malformed recipient"):
            chatmd.parse_share_html(fixture(assistant_recipient=42))

    def test_missing_mapped_node_fails(self) -> None:
        graph = chatmd.decode_hydration(fixture())
        data_ref = chatmd.locate_share_data(graph)
        current_ref = graph.field_ref(data_ref, "current_node")
        assert current_ref is not None
        graph.slots[current_ref] = "missing"
        with self.assertRaisesRegex(chatmd.ParseError, "mapping missing node"):
            chatmd.reconstruct_branch(graph, data_ref)

    def test_message_bearing_node_missing_parent_fails(self) -> None:
        graph = chatmd.decode_hydration(fixture())
        data_ref = chatmd.locate_share_data(graph)
        mapping = graph.object_refs(graph.field_ref(data_ref, "mapping"))
        node = graph.value(mapping["hidden"])
        assert isinstance(node, dict)
        parent_key = next(key for key in node if graph.value(int(key[1:])) == "parent")
        del node[parent_key]
        with self.assertRaisesRegex(chatmd.ParseError, "message-bearing node"):
            chatmd.reconstruct_branch(graph, data_ref)

    def test_second_message_less_node_missing_parent_fails(self) -> None:
        graph = chatmd.decode_hydration(fixture(unexpected_message_less=True))
        data_ref = chatmd.locate_share_data(graph)
        mapping = graph.object_refs(graph.field_ref(data_ref, "mapping"))
        node = graph.value(mapping["assistant"])
        assert isinstance(node, dict)
        parent_key = next(key for key in node if graph.value(int(key[1:])) == "parent")
        del node[parent_key]
        with self.assertRaisesRegex(chatmd.ParseError, "exactly one message-less root"):
            chatmd.reconstruct_branch(graph, data_ref)

    def test_malformed_parent_values_fail(self) -> None:
        for parent in ("", True, 1, []):
            with self.subTest(parent=parent):
                graph = chatmd.decode_hydration(fixture())
                data_ref = chatmd.locate_share_data(graph)
                mapping = graph.object_refs(graph.field_ref(data_ref, "mapping"))
                parent_ref = graph.field_ref(mapping["hidden"], "parent")
                assert parent_ref is not None
                graph.slots[parent_ref] = parent
                with self.assertRaisesRegex(chatmd.ParseError, "invalid parent"):
                    chatmd.reconstruct_branch(graph, data_ref)

    def test_missing_parent_message_less_root_succeeds(self) -> None:
        graph = chatmd.decode_hydration(fixture())
        data_ref = chatmd.locate_share_data(graph)
        branch = chatmd.reconstruct_branch(graph, data_ref)
        self.assertIsNone(graph.field_ref(branch[0], "parent"))
        self.assertEqual(len(branch), 14)

    def test_cycle_fails(self) -> None:
        graph = chatmd.decode_hydration(fixture())
        data_ref = chatmd.locate_share_data(graph)
        mapping = graph.object_refs(graph.field_ref(data_ref, "mapping"))
        user_parent = graph.field_ref(mapping["user"], "parent")
        assert user_parent is not None
        graph.slots[user_parent] = "assistant"
        with self.assertRaisesRegex(chatmd.ParseError, "cyclic active conversation branch"):
            chatmd.reconstruct_branch(graph, data_ref)

    def test_fetch_is_isolated_and_injectable(self) -> None:
        calls: list[str] = []

        def opener(url: str) -> FakeResponse:
            calls.append(url)
            return FakeResponse("héllo".encode())

        self.assertEqual(chatmd.fetch_share("https://chatgpt.com/share/example", opener), "héllo")
        self.assertEqual(calls, ["https://chatgpt.com/share/example"])


class WorkflowTests(unittest.TestCase):
    def test_serialization_preserves_structure_and_source_content(self) -> None:
        user_text = "  # existing\n\n```python\nprint('exact')\n```\n\n> quoted\n\n---\n"
        assistant_text = "answer\n\n---\n"
        source_url = "https://chatgpt.com/share/example?b=2&a=1#fragment"
        conversation = chatmd.Conversation(
            "  Exact title  ",
            (
                chatmd.Message("user", "text", (chatmd.TextPart(user_text),)),
                chatmd.Message("assistant", "text", (chatmd.TextPart(assistant_text),)),
            ),
        )

        expected = "\n\n".join((
            "#   Exact title  ",
            f"> Source: {source_url}",
            "---",
            "**User**",
            user_text,
            "---",
            "**ChatGPT**",
            assistant_text,
        )) + "\n"
        result = chatmd.serialize_conversation(conversation, source_url)

        self.assertEqual(result, expected)
        self.assertEqual(result.count("\n\n---\n\n"), 3)
        self.assertIn(user_text, result)
        self.assertIn(assistant_text, result)

    def test_serialization_preserves_image_position_and_repeated_or_empty_messages(self) -> None:
        conversation = chatmd.Conversation(
            None,
            (
                chatmd.Message("user", "multimodal_text", (
                    chatmd.TextPart("before"),
                    chatmd.ImagePart("sediment://asset/example"),
                    chatmd.TextPart("after"),
                )),
                chatmd.Message("user", "text", ()),
                chatmd.Message("assistant", "text", (chatmd.TextPart("answer"),)),
            ),
        )

        result = chatmd.serialize_conversation(conversation, "https://chatgpt.com/share/example")

        self.assertEqual(result.count("**User**"), 2)
        self.assertEqual(result.count("**ChatGPT**"), 1)
        self.assertEqual(result.count("\n\n---\n\n"), 3)
        self.assertIn("before[Image in original conversation]after", result)
        self.assertIn("after\n\n---\n\n**User**", result)
        self.assertIn("**User**\n\n\n\n---\n\n**ChatGPT**", result)
        self.assertTrue(result.endswith("\n"))
        self.assertEqual(
            result,
            chatmd.serialize_conversation(conversation, "https://chatgpt.com/share/example"),
        )

    def test_serialization_emits_file_placeholder_at_structural_part_position(self) -> None:
        conversation = chatmd.Conversation(
            "File export",
            (chatmd.Message("assistant", "text", (
                chatmd.TextPart("before "),
                chatmd.FilePart("notes.md"),
                chatmd.TextPart(" after"),
            )),),
        )

        result = chatmd.serialize_conversation(conversation, "https://chatgpt.com/share/example")

        self.assertIn("before [File: notes.md] after", result)

    def test_absent_title_uses_only_projection_fallback(self) -> None:
        conversation = chatmd.Conversation(None, ())

        result = chatmd.serialize_conversation(conversation, "https://chatgpt.com/share/example")

        self.assertIsNone(conversation.title)
        self.assertTrue(result.startswith("# conversation\n"))
        self.assertEqual(chatmd.safe_filename(conversation.title), "conversation")

    def test_safe_filename_is_deterministic_and_filesystem_safe(self) -> None:
        cases = {
            "  ... Project / \\ Notes ...  ": "Project _ _ Notes.md",
            " . .foo. . ": "foo.md",
            "many   spaces": "many spaces.md",
            "bad\x00name\x1fname": "bad_name_name.md",
            "...": "conversation.md",
            "": "conversation.md",
            None: "conversation.md",
        }
        for title, expected in cases.items():
            with self.subTest(title=title):
                self.assertEqual(chatmd.safe_filename(title) + ".md", expected)

    def test_default_capture_root_is_the_authorized_vault_path(self) -> None:
        self.assertEqual(
            chatmd.CAPTURE_ROOT,
            Path("/Users/marwan/My vault/Sources/ChatMD"),
        )

    def test_writer_routes_to_year_month_and_creates_missing_directories(self) -> None:
        conversation = user_conversation("Vault export", "exact source text")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with (
                patch("chatmd.CAPTURE_ROOT", root),
                patch("chatmd._capture_date", return_value=CAPTURE_DATE),
            ):
                output = chatmd.write_markdown(conversation, SOURCE_URL)

            expected = (root / "2026" / "09" / "Vault export.md").resolve()
            self.assertEqual(output, expected)
            self.assertTrue(expected.is_file())
            self.assertEqual(
                expected.read_text(encoding="utf-8"),
                chatmd.serialize_conversation(conversation, SOURCE_URL),
            )
            self.assertEqual(markdown_files(root), [expected])

    def test_writer_uses_existing_safe_filename_behavior(self) -> None:
        conversation = user_conversation("  ... Project / \\ Notes ...  ", "body")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with (
                patch("chatmd.CAPTURE_ROOT", root),
                patch("chatmd._capture_date", return_value=CAPTURE_DATE),
            ):
                output = chatmd.write_markdown(conversation, SOURCE_URL)
            self.assertEqual(output.name, "Project _ _ Notes.md")

    def test_writer_collision_preserves_existing_file_and_uses_suffix(self) -> None:
        conversation = user_conversation("conversation", "first capture")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with (
                patch("chatmd.CAPTURE_ROOT", root),
                patch("chatmd._capture_date", return_value=CAPTURE_DATE),
            ):
                first = chatmd.write_markdown(conversation, SOURCE_URL)
                original = first.read_text(encoding="utf-8")
                second = chatmd.write_markdown(
                    user_conversation("conversation", "second capture"),
                    SOURCE_URL,
                )
                third = chatmd.write_markdown(
                    user_conversation("conversation", "third capture"),
                    SOURCE_URL,
                )

            directory = root / "2026" / "09"
            self.assertEqual(first, (directory / "conversation.md").resolve())
            self.assertEqual(second, (directory / "conversation-2.md").resolve())
            self.assertEqual(third, (directory / "conversation-3.md").resolve())
            self.assertEqual(first.read_text(encoding="utf-8"), original)
            self.assertIn("second capture", second.read_text(encoding="utf-8"))
            self.assertIn("third capture", third.read_text(encoding="utf-8"))
            self.assertEqual(set(markdown_files(root)), {first, second, third})

    def test_writer_rejects_contentless_exports_without_a_final_file(self) -> None:
        cases = {
            "title-only shell": chatmd.Conversation("Desktop export", ()),
            "whitespace text": user_conversation("Whitespace", "  \n\t"),
            "empty text part": user_conversation("Empty", ""),
            "empty file part": chatmd.Conversation(
                "File shell",
                (chatmd.Message("assistant", "text", (chatmd.FilePart("  "),)),),
            ),
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, conversation in cases.items():
                with (
                    self.subTest(name=name),
                    patch("chatmd.CAPTURE_ROOT", root),
                    patch("chatmd._capture_date", return_value=CAPTURE_DATE),
                    self.assertRaisesRegex(chatmd.ParseError, "no meaningful content"),
                ):
                    chatmd.write_markdown(conversation, SOURCE_URL)
            self.assertEqual(list(root.rglob("*")), [])

    def test_writer_keeps_image_or_file_parts_as_meaningful_content(self) -> None:
        conversations = (
            chatmd.Conversation(
                "Image only",
                (chatmd.Message("user", "multimodal_text", (
                    chatmd.ImagePart("sediment://asset/example"),
                )),),
            ),
            chatmd.Conversation(
                "File only",
                (chatmd.Message("assistant", "text", (chatmd.FilePart("notes.md"),)),),
            ),
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with (
                patch("chatmd.CAPTURE_ROOT", root),
                patch("chatmd._capture_date", return_value=CAPTURE_DATE),
            ):
                for conversation in conversations:
                    output = chatmd.write_markdown(conversation, SOURCE_URL)
                    self.assertTrue(output.is_file())
                    self.assertEqual(
                        output.read_text(encoding="utf-8"),
                        chatmd.serialize_conversation(conversation, SOURCE_URL),
                    )

    def test_writer_publishes_no_partial_file_on_failure(self) -> None:
        invalid = chatmd.Conversation(
            "failed export",
            (chatmd.Message("system", "text", (chatmd.TextPart("not visible"),)),),
        )
        valid = user_conversation("write failure", "complete body")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with (
                patch("chatmd.CAPTURE_ROOT", root),
                patch("chatmd._capture_date", return_value=CAPTURE_DATE),
                self.assertRaises(chatmd.ParseError),
            ):
                chatmd.write_markdown(invalid, SOURCE_URL)
            self.assertEqual(markdown_files(root), [])

            with (
                patch("chatmd.CAPTURE_ROOT", root),
                patch("chatmd._capture_date", return_value=CAPTURE_DATE),
                patch("chatmd.os.link", side_effect=OSError("link failed")),
                self.assertRaisesRegex(OSError, "link failed"),
            ):
                chatmd.write_markdown(valid, SOURCE_URL)
            self.assertEqual(markdown_files(root), [])

    def test_main_reports_capture_complete_only_after_persistence(self) -> None:
        source_url = "https://chatgpt.com/share/example?b=2&a=1#fragment"
        conversation = user_conversation("Title", "visible body")
        stdout = io.StringIO()
        saved = Path("/tmp/chatmd-isolated/2026/09/Title.md")
        write_state = {"called": False}

        def write_markdown(written: chatmd.Conversation, url: str) -> Path:
            self.assertEqual(written, conversation)
            self.assertEqual(url, source_url)
            self.assertEqual(stdout.getvalue(), "")
            write_state["called"] = True
            return saved

        with (
            patch("chatmd.parse_share", return_value=conversation) as parse_share,
            patch("chatmd.write_markdown", side_effect=write_markdown) as write_markdown_mock,
            patch("chatmd._read_macos_clipboard") as read_clipboard,
            redirect_stdout(stdout),
        ):
            self.assertEqual(chatmd.main([source_url]), 0)

        parse_share.assert_called_once_with(source_url)
        write_markdown_mock.assert_called_once_with(conversation, source_url)
        read_clipboard.assert_not_called()
        self.assertTrue(write_state["called"])
        self.assertEqual(stdout.getvalue(), capture_complete_text(saved, source_url))

    def test_main_reports_actual_path_after_collision_and_preserves_existing_file(self) -> None:
        conversation = user_conversation("Title", "first body")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first_out = io.StringIO()
            second_out = io.StringIO()
            with (
                patch("chatmd.CAPTURE_ROOT", root),
                patch("chatmd._capture_date", return_value=CAPTURE_DATE),
                patch("chatmd.parse_share", return_value=conversation),
            ):
                with redirect_stdout(first_out):
                    self.assertEqual(chatmd.main([SOURCE_URL]), 0)
                original = (root / "2026" / "09" / "Title.md").read_text(encoding="utf-8")
                with redirect_stdout(second_out):
                    self.assertEqual(chatmd.main([SOURCE_URL]), 0)

            first = (root / "2026" / "09" / "Title.md").resolve()
            second = (root / "2026" / "09" / "Title-2.md").resolve()
            self.assertEqual(first_out.getvalue(), capture_complete_text(first, SOURCE_URL))
            self.assertEqual(second_out.getvalue(), capture_complete_text(second, SOURCE_URL))
            self.assertEqual(first.read_text(encoding="utf-8"), original)
            self.assertTrue(second.is_file())

    def test_main_fetch_or_parse_failure_is_nonzero_without_capture_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for error in (OSError("fetch failed"), chatmd.ParseError("share is malformed")):
                stdout = io.StringIO()
                stderr = io.StringIO()
                with (
                    self.subTest(error=error),
                    patch("chatmd.CAPTURE_ROOT", root),
                    patch("chatmd.parse_share", side_effect=error),
                    patch("chatmd.write_markdown") as write_markdown,
                    redirect_stdout(stdout),
                    redirect_stderr(stderr),
                    self.assertRaises(SystemExit) as caught,
                ):
                    chatmd.main([SOURCE_URL])
                self.assertEqual(caught.exception.code, 2)
                self.assertIn(str(error), stderr.getvalue())
                write_markdown.assert_not_called()
                assert_no_successful_capture_result(self, stdout.getvalue(), stderr.getvalue())
            self.assertEqual(markdown_files(root), [])

    def test_main_persistence_failure_does_not_emit_capture_complete(self) -> None:
        conversation = user_conversation("Title", "visible body")
        for error in (
            OSError("write failed"),
            chatmd.ParseError("conversation has no meaningful content"),
        ):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with (
                self.subTest(error=error),
                patch("chatmd.parse_share", return_value=conversation),
                patch("chatmd.write_markdown", side_effect=error) as write_markdown,
                redirect_stdout(stdout),
                redirect_stderr(stderr),
                self.assertRaises(SystemExit) as caught,
            ):
                chatmd.main([SOURCE_URL])
            self.assertEqual(caught.exception.code, 2)
            write_markdown.assert_called_once_with(conversation, SOURCE_URL)
            self.assertIn(str(error), stderr.getvalue())
            self.assertEqual(stdout.getvalue(), "")
            assert_no_successful_capture_result(self, stdout.getvalue(), stderr.getvalue())

    def test_main_rejects_extra_and_invalid_explicit_input(self) -> None:
        for arguments in (["https://example.com/one", "https://example.com/two"], ["not-a-url"]):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with (
                self.subTest(arguments=arguments),
                patch("chatmd._read_macos_clipboard") as read_clipboard,
                redirect_stdout(stdout),
                redirect_stderr(stderr),
                self.assertRaises(SystemExit) as error,
            ):
                chatmd.main(arguments)
            self.assertEqual(error.exception.code, 2)
            read_clipboard.assert_not_called()
            assert_no_successful_capture_result(self, stdout.getvalue(), stderr.getvalue())

    def test_help_is_a_normal_cli_command(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            redirect_stdout(stdout),
            redirect_stderr(stderr),
            self.assertRaises(SystemExit) as caught,
        ):
            chatmd.main(["--help"])
        self.assertEqual(caught.exception.code, 0)
        help_text = stdout.getvalue()
        self.assertIn("usage: chatmd", help_text)
        self.assertIn("optional public HTTP(S) share URL", help_text)
        self.assertIn("https://chatgpt.com/share/", help_text)
        self.assertIn("macOS clipboard", help_text)
        self.assertNotIn("chatmd.py", help_text)
        self.assertEqual(stderr.getvalue(), "")
        assert_no_successful_capture_result(self, help_text, stderr.getvalue())


class ClipboardTests(unittest.TestCase):
    def test_zero_argument_uses_valid_clipboard_share_url(self) -> None:
        source_url = "https://chatgpt.com/share/example?b=2&a=1#fragment"
        conversation = user_conversation("Title", "visible body")
        stdout = io.StringIO()
        saved = Path("/tmp/chatmd-isolated/2026/09/Title.md")

        with (
            patch("chatmd._read_macos_clipboard", return_value=f"\n  {source_url}  \n"),
            patch("chatmd.parse_share", return_value=conversation) as parse_share,
            patch("chatmd.write_markdown", return_value=saved) as write_markdown,
            redirect_stdout(stdout),
        ):
            self.assertEqual(chatmd.main([]), 0)

        parse_share.assert_called_once_with(source_url)
        write_markdown.assert_called_once_with(conversation, source_url)
        self.assertEqual(stdout.getvalue(), capture_complete_text(saved, source_url))

    def test_explicit_url_does_not_read_clipboard(self) -> None:
        conversation = user_conversation()
        saved = Path("/tmp/chatmd-isolated/2026/09/Capture.md")
        with (
            patch("chatmd._read_macos_clipboard") as read_clipboard,
            patch("chatmd.parse_share", return_value=conversation) as parse_share,
            patch("chatmd.write_markdown", return_value=saved),
            redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(chatmd.main([SOURCE_URL]), 0)
        read_clipboard.assert_not_called()
        parse_share.assert_called_once_with(SOURCE_URL)

    def test_clipboard_failures_are_nonzero_without_capture_or_success_output(self) -> None:
        cases = (
            ("   \n", "clipboard is empty"),
            ("not a url", "clipboard is not a URL"),
            ("see https://chatgpt.com/share/example", "clipboard is not a URL"),
            ("https://example.com/share/example", "clipboard is not a ChatGPT share URL"),
            ("http://chatgpt.com/share/example", "clipboard is not a ChatGPT share URL"),
        )
        for contents, message in cases:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with (
                self.subTest(contents=contents),
                tempfile.TemporaryDirectory() as temporary,
                patch("chatmd.CAPTURE_ROOT", Path(temporary)),
                patch("chatmd._read_macos_clipboard", return_value=contents),
                patch("chatmd.parse_share") as parse_share,
                patch("chatmd.write_markdown") as write_markdown,
                redirect_stdout(stdout),
                redirect_stderr(stderr),
                self.assertRaises(SystemExit) as caught,
            ):
                chatmd.main([])
            self.assertEqual(caught.exception.code, 2)
            self.assertIn(message, stderr.getvalue())
            parse_share.assert_not_called()
            write_markdown.assert_not_called()
            self.assertEqual(markdown_files(Path(temporary)), [])
            assert_no_successful_capture_result(self, stdout.getvalue(), stderr.getvalue())

    def test_clipboard_command_failure_does_not_capture(self) -> None:
        failures = (
            FileNotFoundError("pbpaste"),
            subprocess.CompletedProcess(["pbpaste"], 1, stdout="", stderr="failed"),
        )
        for result in failures:
            stdout = io.StringIO()
            stderr = io.StringIO()
            side_effect = result if isinstance(result, Exception) else None
            return_value = None if isinstance(result, Exception) else result
            with (
                self.subTest(result=result),
                tempfile.TemporaryDirectory() as temporary,
                patch("chatmd.CAPTURE_ROOT", Path(temporary)),
                patch("chatmd.subprocess.run", side_effect=side_effect, return_value=return_value),
                patch("chatmd.parse_share") as parse_share,
                patch("chatmd.write_markdown") as write_markdown,
                redirect_stdout(stdout),
                redirect_stderr(stderr),
                self.assertRaises(SystemExit) as caught,
            ):
                chatmd.main([])
            self.assertEqual(caught.exception.code, 2)
            if isinstance(result, FileNotFoundError):
                self.assertIn("pbpaste is unavailable", stderr.getvalue())
            else:
                self.assertIn("unable to read the macOS clipboard", stderr.getvalue())
            parse_share.assert_not_called()
            write_markdown.assert_not_called()
            self.assertEqual(markdown_files(Path(temporary)), [])
            assert_no_successful_capture_result(self, stdout.getvalue(), stderr.getvalue())


class EntrypointTests(unittest.TestCase):
    def test_installed_chatmd_runs_from_outside_the_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            venv = root / "venv"
            outside = root / "outside"
            outside.mkdir()
            subprocess.run(
                ["uv", "venv", str(venv)],
                check=True,
                cwd=outside,
                capture_output=True,
                text=True,
            )
            python = venv / "bin" / "python"
            subprocess.run(
                ["uv", "pip", "install", "--python", str(python), str(REPO_ROOT)],
                check=True,
                cwd=outside,
                capture_output=True,
                text=True,
            )
            show = subprocess.run(
                ["uv", "pip", "show", "--python", str(python), "chatmd"],
                check=True,
                cwd=outside,
                capture_output=True,
                text=True,
            )
            module = subprocess.run(
                [
                    str(python),
                    "-c",
                    "import chatmd; from pathlib import Path; print(Path(chatmd.__file__).resolve())",
                ],
                check=True,
                cwd=outside,
                capture_output=True,
                text=True,
            )
            module_path = Path(module.stdout.strip()).resolve()
            self.assertNotIn("Editable project location", show.stdout)
            self.assertTrue(
                str(module_path).startswith(str((venv / "lib").resolve())),
                module_path,
            )
            self.assertFalse(str(module_path).startswith(str(REPO_ROOT)))
            chatmd_bin = venv / "bin" / "chatmd"
            self.assertTrue(chatmd_bin.is_file(), chatmd_bin)
            help_result = subprocess.run(
                [str(chatmd_bin), "--help"],
                cwd=outside,
                capture_output=True,
                text=True,
                check=False,
            )
            fake_bin = root / "fake-bin"
            fake_bin.mkdir()
            pbpaste = fake_bin / "pbpaste"
            pbpaste.write_text("#!/bin/sh\nprintf '%s' 'not a url'\n", encoding="utf-8")
            pbpaste.chmod(0o755)
            isolated_env = os.environ.copy()
            isolated_env["PATH"] = str(fake_bin)
            missing_result = subprocess.run(
                [str(chatmd_bin)],
                cwd=outside,
                capture_output=True,
                text=True,
                check=False,
                env=isolated_env,
            )
            self.assertEqual(help_result.returncode, 0, help_result.stderr)
            self.assertIn("usage: chatmd", help_result.stdout)
            self.assertIn("optional public HTTP(S) share URL", help_result.stdout)
            self.assertIn("https://chatgpt.com/share/", help_result.stdout)
            self.assertIn("macOS clipboard", help_result.stdout)
            self.assertNotIn("chatmd.py", help_result.stdout)
            self.assertNotIn(str(REPO_ROOT), help_result.stdout)
            assert_no_successful_capture_result(
                self, help_result.stdout, help_result.stderr
            )
            self.assertEqual(missing_result.returncode, 2, missing_result.stderr)
            self.assertIn("usage: chatmd", missing_result.stderr)
            self.assertIn("clipboard is not a URL", missing_result.stderr)
            assert_no_successful_capture_result(
                self, missing_result.stdout, missing_result.stderr
            )


if __name__ == "__main__":
    unittest.main()
