"""シンプルAIチャット"""

from nicegui import ui
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel


async def send(agent: Agent, message_container: ui.column, text: ui.input) -> None:
    """質問に回答

    :param agent: エージェント
    :param message_container: 親コンテナ(UI)
    :param text: 入力(UI)
    """
    if not (question := text.value):
        return
    text.value = ""
    with message_container:
        ui.chat_message(text=question, name="You", sent=True)
        response_message = ui.chat_message(name="Bot", sent=False)
        spinner = ui.spinner(type="dots")
    async with agent.run_stream(question) as result:
        async for message in result.stream():
            response_message.clear()
            with response_message:
                ui.html(message)
    ui.run_javascript("window.scrollTo(0, document.body.scrollHeight)")
    message_container.remove(spinner)


def main(*, reload: bool = False, port: int = 8106) -> None:
    """メイン"""
    # Ollamaを利用
    agent = Agent(
        OpenAIModel("llama3.2", base_url="http://localhost:11434/v1", api_key="_"),
        system_prompt="Be concise, reply with one sentence.",
    )
    message_container = ui.column().classes("w-full max-w-2xl mx-auto items-stretch")
    with ui.footer().classes("bg-white"), ui.column().classes("w-full max-w-3xl mx-auto my-6"):
        text = ui.input(placeholder="メッセージ").props("rounded outlined input-class=mx-3").classes("w-full")
        text.on("keydown.enter", lambda: send(agent, message_container, text))
    ui.run(title="Chat", reload=reload, port=port)
