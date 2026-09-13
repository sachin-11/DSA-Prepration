from __future__ import annotations

import random
import time
from string import Template

from openai import OpenAI

client = OpenAI()


class RateLimitedError(Exception):
    pass


# 1) Simple chat call

def chat(system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


# 2) Retry with exponential backoff

def call_with_backoff(func, max_retries: int = 5, base_delay: float = 1.0, max_delay: float = 30.0):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitedError:
            if attempt == max_retries - 1:
                raise
            delay = min(max_delay, base_delay * (2 ** attempt))
            jitter = random.uniform(0, delay * 0.5)
            wait_time = delay + jitter
            print(f"rate limited, retrying in {wait_time:.2f}s (attempt {attempt + 1})")
            time.sleep(wait_time)
    raise RuntimeError("max retries exceeded")


# 3) Streaming chat

def stream_chat(user_prompt: str, system_prompt: str, model: str = "gpt-4o-mini") -> str:
    full_text = ""
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
            full_text += delta
    print()
    return full_text


# 4) Safe chat with retryable and non-retryable exceptions

try:
    from openai import APITimeoutError, APIConnectionError, RateLimitError, BadRequestError, AuthenticationError
except ImportError:
    class APITimeoutError(Exception):
        pass

    class APIConnectionError(Exception):
        pass

    class RateLimitError(Exception):
        pass

    class BadRequestError(Exception):
        pass

    class AuthenticationError(Exception):
        pass


RETRYABLE_ERRORS = (APITimeoutError, APIConnectionError, RateLimitedError, RateLimitError)
NON_RETRYABLE_ERRORS = (BadRequestError, AuthenticationError)


def safe_chat(messages, model: str = "gpt-4o-mini", max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model=model,
                messages=messages,
                timeout=30,
            )
        except RETRYABLE_ERRORS as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"retryable error: {e}. Retrying in {wait}s")
            time.sleep(wait)
        except NON_RETRYABLE_ERRORS as e:
            print(f"non retryable error: {e}")
            raise
    raise RuntimeError("safe_chat failed after retries")


# 5) Fallback logic

def call_openai(prompt: str) -> str:
    raise RuntimeError("open ai down (mock)")


def call_antropic(prompt: str) -> str:
    return f"[antropic] answer to the prompt: {prompt}"


def local_llm_call(prompt: str) -> str:
    return f"[local_llm] answer to the prompt: {prompt}"


providers = [call_antropic, call_openai, local_llm_call]


def chat_with_fallback(prompt: str) -> str:
    for provider in providers:
        try:
            return provider(prompt)
        except Exception as e:
            print(f"{provider.__name__} failed: {e}")
    raise RuntimeError("all providers failed")


# 6) Prompt templating

class PromptTemplate:
    def __init__(self, template: str):
        self.template = Template(template)

    def render(self, **kwargs) -> str:
        return self.template.safe_substitute(**kwargs)


# 7) Fixed-size chunking with overlap

def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> list[str]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)

    return chunks


if __name__ == "__main__":
    print(chat("you are a helpful assistant", "explain RAG in 2 lines"))
    print(call_with_backoff(lambda: 42))
    print(chat_with_fallback("2+2 kitna hota he?"))
    template = PromptTemplate("hello ${name}, this is a few-shot example")
    print(template.render(name="Alice"))
    print(chunk_text("abcdefghijklmnopqrstuvwxyz", 10, 3))


### 13. Documents ko embed karke ek in-memory vector store banao (numpy/list based cosine similarity).

import numpy as np

def mock_embeded(text:str) -> np.ndarray:
    # real project mein openAI
    rng = np.random.default_rng(abs(hash(text)) % (2 ** 32))
    vec = rng.random(384)
    return vec / np.linage.norm(vec)