import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from email.message import Message as Headers
from pathlib import Path
from unittest.mock import patch

import chatmd

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

    def test_writer_uses_desktop_and_exclusive_creation(self) -> None:
        conversation = chatmd.Conversation("Desktop export", ())
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            desktop = home / "Desktop"
            desktop.mkdir()
            with patch("chatmd.Path.home", return_value=home):
                output = chatmd.write_markdown(
                    conversation,
                    "https://chatgpt.com/share/example",
                )

            self.assertEqual(output, desktop / "Desktop export.md")
            self.assertEqual(output.read_text(encoding="utf-8"), (
                "# Desktop export\n\n"
                "> Source: https://chatgpt.com/share/example\n"
            ))

            output.write_text("keep this exact file", encoding="utf-8")
            with self.assertRaisesRegex(FileExistsError, "already exists"):
                chatmd.write_markdown(conversation, "https://chatgpt.com/share/example", desktop)
            self.assertEqual(output.read_text(encoding="utf-8"), "keep this exact file")
            self.assertEqual(list(desktop.iterdir()), [output])

    def test_writer_publishes_no_partial_file_on_failure(self) -> None:
        conversation = chatmd.Conversation(
            "failed export",
            (chatmd.Message("system", "text", (chatmd.TextPart("not visible"),)),),
        )
        with tempfile.TemporaryDirectory() as temporary:
            desktop = Path(temporary)
            with self.assertRaises(chatmd.ParseError):
                chatmd.write_markdown(conversation, "https://chatgpt.com/share/example", desktop)
            self.assertEqual(list(desktop.iterdir()), [])

            valid = chatmd.Conversation("write failure", ())
            with patch("chatmd.os.link", side_effect=OSError("link failed")), self.assertRaisesRegex(
                OSError, "link failed"
            ):
                chatmd.write_markdown(valid, "https://chatgpt.com/share/example", desktop)
            self.assertEqual(list(desktop.iterdir()), [])

    def test_main_accepts_one_url_without_stdout_serialization(self) -> None:
        source_url = "https://chatgpt.com/share/example?b=2&a=1#fragment"
        conversation = chatmd.Conversation("Title", ())
        stdout = io.StringIO()
        with patch("chatmd.parse_share", return_value=conversation) as parse_share, patch(
            "chatmd.write_markdown"
        ) as write_markdown, redirect_stdout(stdout):
            self.assertEqual(chatmd.main([source_url]), 0)

        parse_share.assert_called_once_with(source_url)
        write_markdown.assert_called_once_with(conversation, source_url)
        self.assertEqual(stdout.getvalue(), "")

    def test_main_rejects_missing_extra_and_invalid_input(self) -> None:
        for arguments in ([], ["https://example.com/one", "https://example.com/two"], ["not-a-url"]):
            with (
                self.subTest(arguments=arguments),
                redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit) as error,
            ):
                chatmd.main(arguments)
            self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
