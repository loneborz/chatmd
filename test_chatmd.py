from email.message import Message as Headers
import json
import unittest

import chatmd


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
            chatmd.Conversation((
                chatmd.Message("user", "multimodal_text", (
                    chatmd.TextPart("  exact **source**\n\n"),
                    chatmd.ImagePart("sediment://asset/example"),
                )),
                chatmd.Message("assistant", "text", (chatmd.TextPart("answer"),)),
            )),
        )

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


if __name__ == "__main__":
    unittest.main()
