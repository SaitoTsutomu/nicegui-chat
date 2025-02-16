"""テスト"""
# flake8: noqa: S101

import asyncio
from textwrap import dedent
from unittest.mock import patch

from nicegui import ui
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from nicegui_chat import send


def test_send() -> None:
    """send()のテスト"""
    # arrange
    question = "hello!"  # 質問
    answer = "world!"  # 回答

    # sendの引数
    agent = Agent(TestModel(custom_result_text=answer))
    message_container = ui.column()
    input_ = ui.input(value=question)

    # act
    with patch("nicegui.ui.run_javascript"):  # run_javascriptの無効化
        asyncio.run(send(agent, message_container, input_))

    # assert
    expected = dedent(f"""\
        Column
         ChatMessage [name=You, sent=True]
          Html [content={question}]
         ChatMessage [name=Bot]
          Html [content={answer}]""")
    assert str(message_container) == expected
