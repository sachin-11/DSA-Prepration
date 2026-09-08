# 1. OpenAI/Anthropic API ko call karke ek simple chat function likho (system + user message ke saath).

from openai import OpenAI

client = OpenAI()


def chat(system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    answer = chat(
        system_prompt="You are a helpful assistant that explains concepts simply.",
        user_prompt="Explain RAG in 2 lines.",
    )
    print(answer)
