import json
import logging

from typing import Optional
from fastapi import WebSocket
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionSystemMessageParam
)

from diagram_tools import build_diagram
from prompt import SYSTEM_PROMPT
from settings import MODEL_NAME, TOOLS, TEMPERATURE

logger = logging.getLogger(__name__)

class DiagramAgent:
    def __init__(self, client: OpenAI):
        self.client = client
        self.chat_history: list[
            ChatCompletionSystemMessageParam |
            ChatCompletionUserMessageParam |
            ChatCompletionToolMessageParam
        ] = [SYSTEM_PROMPT]
        self.waiting_for_user: bool = True
        self.model_name = MODEL_NAME
        self.temperature = TEMPERATURE
        self.tools = TOOLS

    async def process_tool_calls(self, tool_calls, websocket: WebSocket) -> None:
        """
        Process function calls returned by the LLM.
        """
        for tool_call in tool_calls:
            fn_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            call_id = tool_call.id

            if fn_name == "ask_for_clarification":
                await websocket.send_json({"type": "question", "text": args["question"]})

                self.chat_history.append(ChatCompletionToolMessageParam(
                    role="tool", tool_call_id=call_id, content="Clarification sent to user"
                ))
                self.waiting_for_user = True # waiting for user input
                return None

            elif fn_name == "generate_aws_diagram":
                logger.info("Generating diagram...")
                try:
                    path = build_diagram(args["description"])
                    await websocket.send_json({"type": "diagram", "path": path})
                except Exception as e:
                    await websocket.send_json({"type": "error", "message": str(e)})
                self.chat_history.append(ChatCompletionToolMessageParam(
                    role="tool", tool_call_id=call_id, content="Diagram generated"
                ))

        self.waiting_for_user = False # continue the loop
        return None

    async def run(self, websocket: WebSocket, user_input: Optional[str] = None):
        """
        Main entrypoint for user messages or continuation after tool call.
        """
        if user_input:
            self.chat_history.append(ChatCompletionUserMessageParam(
                role="user", content=user_input
            ))
            self.waiting_for_user = False

        while not self.waiting_for_user:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.chat_history,
                temperature=self.temperature,
                tools=self.tools,
                tool_choice="auto"
            )
            msg = response.choices[0].message
            self.chat_history.append(msg)

            tool_calls = getattr(msg, "tool_calls", None)

            if tool_calls:
                await self.process_tool_calls(tool_calls, websocket)

                if not self.waiting_for_user:
                    continue
                else:
                    break

            elif msg.content:
                await websocket.send_json({"type": "message", "text": msg.content})
                self.waiting_for_user = False
