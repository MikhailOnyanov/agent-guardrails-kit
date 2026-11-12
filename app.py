from pathlib import Path
from typing import Any

from fastapi import FastAPI
from nemoguardrails import LLMRails, RailsConfig
from pydantic import BaseModel


CONFIG_DIR = Path(__file__).parent / "config"
rails = LLMRails(RailsConfig.from_path(str(CONFIG_DIR)))
app = FastAPI(title="NeMo Guardrails: dangerous SQL example")


class ChatRequest(BaseModel):
    messages: list[dict[str, Any]]


@app.post("/chat")
async def chat(request: ChatRequest) -> dict[str, str]:
    # Input rails run before generation, including block_dangerous_sql.
    response = await rails.generate_async(messages=request.messages)
    return {"reply": response.response[-1]["content"]}
