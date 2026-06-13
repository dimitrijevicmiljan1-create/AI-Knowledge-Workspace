from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(examples=["system"])
    content: str = Field(examples=["You are a helpful assistant."])


class ChatCompletionResult(BaseModel):
    content: str
    model: str
