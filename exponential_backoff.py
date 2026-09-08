import random
import time
from openai import OpenAI
from openai import APIError, APITimeOutError, RateLimitError

client = OpenAI()


def call_openai_with_backoff(messages, model: str = "gpt-4-mini", max_retries: int = 4, base_delay:float = 1.0, max_delay:float = 60.0):

    attempt = 0
    while True:
        try:
            response = client.chat.completions.create(
                model = model,
                messages = messages,
                timeout = 30
            )
            return response
        except (RateLimitError, APITimeOutError) as e:
            attempt += 1
            if attempt > max_retries:
                raise RuntimeError(f"max retry {{max_retry}} exceeded")
            delay = min(max_delay, base_delay * 2 (2 ** (attempt - 1)))
            jitter = random.uniform(0, delay * 0.1)
            wait_time = delay + jitter
            print(f"rate limited retying {wait_time}")
            time.sleep(wait_time)
        except APIError:
         raise  


if __name__ == "_main_":
    messages = [{"role": "user", "content": "Explain RAG in one line."}]
    result = call_openai_with_backoff(messages)
    print(result.choices[0].message.content)    





