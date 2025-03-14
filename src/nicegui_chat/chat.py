"""AIチャット"""

from logging import INFO, basicConfig, getLogger
from math import acos, cos, radians, sin

import jageocoder
import urllib3
from nicegui import events, ui
from openai import APIConnectionError, BadRequestError, NotFoundError
from pydantic_ai import Agent, RunContext
from pydantic_ai.exceptions import AgentRunError
from pydantic_ai.models.openai import OpenAIModel

logger = getLogger(__name__)


def distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """2地点間の大圏距離(km)"""
    r = 6371
    ry1, rx1, ry2, rx2 = radians(lat1), radians(lon1), radians(lat2), radians(lon2)
    distance = r * acos(sin(ry1) * sin(ry2) + cos(ry1) * cos(ry2) * cos(rx1 - rx2))
    logger.info("\033[32mdistance\033[0m: %s %s %s %s %f", lat1, lon1, lat2, lon2, distance)
    return distance


def calc_distance(_ctx: RunContext[None], from_: str, to: str) -> float:
    """2つの住所間の距離"""
    logger.info("\033[32mcalc_distance\033[0m: %s %s", from_, to)
    if not from_ or not to:
        msg = "引数が空"
        raise AgentRunError(msg)
    results = jageocoder.search(from_)
    if not results["matched"]:
        msg = "from_の結果なし"
        raise AgentRunError(msg)
    location = results["candidates"][0]
    from_x, from_y = location["x"], location["y"]
    results = jageocoder.search(to)
    if not results["matched"]:
        msg = "toの結果なし"
        raise AgentRunError(msg)
    location = results["candidates"][0]
    to_x, to_y = location["x"], location["y"]
    return distance(from_y, from_x, to_y, to_x)


async def send(
    event: events.GenericEventArguments,
    agent: Agent,
    message_container: ui.column,
    text: ui.textarea,
) -> None:
    """質問に回答

    :param event: イベント
    :param agent: エージェント
    :param message_container: 親コンテナ(UI)
    :param text: 入力(UI)
    """
    # シフトキー、IME確定、または空文字列
    if event.args.get("shiftKey") or event.args.get("isComposing") or not (question := text.value):
        return
    text.value = ""
    with message_container:
        ui.chat_message(text=question, name="You", sent=True)
        response_message = ui.chat_message(name="Bot", sent=False)
        spinner = ui.spinner(type="dots")
    ui.run_javascript("window.scrollTo(0, document.body.scrollHeight)")
    try:
        # tool利用時は、結果が空になることがあるためrun_streamは使えない
        message = await agent.run(question)
        content = str(message.data)
    except (
        AgentRunError,
        APIConnectionError,
        BadRequestError,
        jageocoder.exceptions.RemoteTreeException,
        urllib3.exceptions.MaxRetryError,
        NotFoundError,
    ) as e:
        content = str(e)
    finally:
        with response_message:
            ui.html(content)
        ui.run_javascript("window.scrollTo(0, document.body.scrollHeight)")
        message_container.remove(spinner)


def chat(model: str = "llama3.2", *, port: int | None = None) -> None:
    """メイン"""
    basicConfig(level=INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    # jageocoderの設定
    jageocoder.init(url="http://localhost:5000/jsonrpc")
    # モデルとしてOllamaを利用
    agent = Agent(
        OpenAIModel(model, base_url="http://localhost:11434/v1", api_key="_"),
        system_prompt=(
            "Be concise, reply with one sentence.",
            "For the distance between two addresses in Japan, use calc_distance tool.",
            "For the argument address, use the input value as it is.",
        ),
        tools=[calc_distance],
        model_settings={"temperature": 0.8},
    )
    # UI
    message_container = ui.column().classes("w-full max-w-2xl mx-auto items-stretch")
    with ui.footer().classes("bg-white"), ui.column().classes("w-full max-w-3xl mx-auto my-6"):
        text = ui.textarea(placeholder="メッセージ").props("rounded outlined input-class=mx-3").classes("w-full")
        text.on("keydown.enter", lambda event: send(event, agent, message_container, text))
    # 入力欄にカーソルを表示
    ui.timer(0.2, lambda: ui.run_javascript('document.querySelector("textarea").focus()'), once=True)
    ui.run(title="Chat", reload=False, port=port)
