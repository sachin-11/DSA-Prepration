# GenAI Coding Interview Questions — Practice List

Topics ke hisaab se grouped hai. Har question ke neeche reference answer diya hai (mock/dummy data ke saath, bina real API call ke) — pehle answer dekhe bina khud try karo, phir compare karo.

## 1. LLM API Basics & Reliability

### 1. OpenAI/Anthropic API ko call karke ek simple chat function likho (system + user message ke saath).

**Answer:**
```python
from openai import OpenAI

client = OpenAI()  # OPENAI_API_KEY env var se uthega


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
    print(chat("You are a helpful assistant.", "Explain RAG in 2 lines."))
```
Anthropic ke liye same idea hai, bas `system` alag param hota hai:
```python
import anthropic

client = anthropic.Anthropic()


def chat_claude(system_prompt: str, user_prompt: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text
```
_System message model ka behaviour/persona set karta hai, user message actual query hoti hai._

---

### 2. Exponential backoff with jitter implement karo API rate-limit errors ke liye (retry logic).

**Answer:**
```python
import random
import time


class RateLimitError(Exception):
    pass


def call_with_backoff(func, max_retries: int = 5, base_delay: float = 1.0, max_delay: float = 30.0):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            delay = min(max_delay, base_delay * (2 ** attempt))
            jitter = random.uniform(0, delay * 0.5)
            wait_time = delay + jitter
            print(f"rate limited, retrying in {wait_time:.2f}s (attempt {attempt + 1})")
            time.sleep(wait_time)


# --- test with a mock flaky function ---
_calls = {"n": 0}


def flaky_call():
    _calls["n"] += 1
    if _calls["n"] < 3:
        raise RateLimitError("429")
    return "success"


if __name__ == "__main__":
    print(call_with_backoff(flaky_call))
```
_Delay har retry pe double hota hai (`base_delay * 2^attempt`), jitter isliye add karte hain taaki multiple clients ek saath retry na karein (thundering herd avoid ho)._

---

### 3. Streaming response handle karo — tokens as they arrive print karo (SSE/streaming API).

**Answer:**
```python
from openai import OpenAI

client = OpenAI()


def stream_chat(user_prompt: str, model: str = "gpt-4o-mini") -> str:
    full_text = ""
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": user_prompt}],
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
            full_text += delta
    print()
    return full_text


# --- mock version bina API ke test karne ke liye ---
def mock_stream(tokens):
    full_text = ""
    for token in tokens:
        print(token, end="", flush=True)
        full_text += token
    print()
    return full_text


if __name__ == "__main__":
    mock_stream(["Hello", " ", "world", "!"])
```
_`stream=True` pass karne se response chunks (delta) mein aati hai; har chunk ko turant print karo taaki user ko real-time feel aaye._

---

### 4. Timeout aur connection error ke liye robust error handling likho (retryable vs non-retryable errors alag karo).

**Answer:**
```python
import time
from openai import OpenAI, APITimeoutError, APIConnectionError, RateLimitError, BadRequestError, AuthenticationError

client = OpenAI()

RETRYABLE_ERRORS = (APITimeoutError, APIConnectionError, RateLimitError)
NON_RETRYABLE_ERRORS = (BadRequestError, AuthenticationError)


def safe_chat(messages, model: str = "gpt-4o-mini", max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(model=model, messages=messages, timeout=30)
        except RETRYABLE_ERRORS as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"retryable error {type(e).__name__}, retrying in {wait}s")
            time.sleep(wait)
        except NON_RETRYABLE_ERRORS as e:
            print(f"non-retryable error {type(e).__name__}: {e}")
            raise
```
_Retryable = temporary/network-level issues (timeout, connection drop, rate limit). Non-retryable = client ki galti (bad request, invalid auth) — inhe retry karna waste hai, seedha fail-fast karo._

---

### 5. Multiple API keys/providers ke beech fallback logic likho (agar ek provider fail ho to dusre pe switch ho jaye).

**Answer:**
```python
def call_openai(prompt: str) -> str:
    raise RuntimeError("OpenAI down (mock)")


def call_anthropic(prompt: str) -> str:
    return f"[anthropic] answer to: {prompt}"


def call_local_llm(prompt: str) -> str:
    return f"[local-llm] answer to: {prompt}"


PROVIDERS = [call_openai, call_anthropic, call_local_llm]


def chat_with_fallback(prompt: str) -> str:
    last_error = None
    for provider in PROVIDERS:
        try:
            return provider(prompt)
        except Exception as e:
            print(f"{provider.__name__} failed: {e}")
            last_error = e
            continue
    raise RuntimeError(f"all providers failed: {last_error}")


if __name__ == "__main__":
    print(chat_with_fallback("2+2 kitna hota hai?"))
```
_Providers ko priority order mein list rakho, har ek fail hone par next try karo. Production mein circuit-breaker bhi add karte hain taaki baar-baar dead provider try na ho._

## 2. Prompt Engineering / Templating

### 6. Ek reusable prompt template class/function banao jisme variables inject ho sakein (jinja2 ya f-string based).

**Answer:**
```python
from string import Template


class PromptTemplate:
    def __init__(self, template: str):
        self.template = Template(template)

    def render(self, **kwargs) -> str:
        return self.template.safe_substitute(**kwargs)


if __name__ == "__main__":
    tmpl = PromptTemplate("Summarize the following $doc_type in $n_words words:\n\n$content")
    prompt = tmpl.render(doc_type="article", n_words=50, content="LLMs are transforming software...")
    print(prompt)
```
Jinja2 version (agar loops/conditionals bhi chahiye):
```python
from jinja2 import Template as JinjaTemplate

tmpl = JinjaTemplate("You are a {{ role }}.\n{% for ex in examples %}Q: {{ ex }}\n{% endfor %}")
print(tmpl.render(role="math tutor", examples=["2+2", "3*3"]))
```
_f-string/Template simple substitution ke liye kaafi hai; jinja2 tab use karo jab conditionals ya loops chahiye templates ke andar._

---

### 7. Few-shot prompt banane wala function likho jo examples list se dynamically prompt construct kare.

**Answer:**
```python
def build_few_shot_prompt(instruction: str, examples: list[dict], query: str) -> str:
    parts = [instruction, ""]
    for ex in examples:
        parts.append(f"Input: {ex['input']}")
        parts.append(f"Output: {ex['output']}")
        parts.append("")
    parts.append(f"Input: {query}")
    parts.append("Output:")
    return "\n".join(parts)


if __name__ == "__main__":
    examples = [
        {"input": "I love this!", "output": "positive"},
        {"input": "This is terrible.", "output": "negative"},
    ]
    prompt = build_few_shot_prompt(
        "Classify the sentiment as positive or negative.",
        examples,
        "The movie was okay, nothing special.",
    )
    print(prompt)
```
_Har example ko consistent Input/Output format mein rakho — model pattern ko follow karke last query ka answer generate karta hai._

---

### 8. System prompt + conversation history ko ek single messages array mein assemble karne wala function likho.

**Answer:**
```python
def assemble_messages(system_prompt: str, history: list[tuple[str, str]], user_message: str) -> list[dict]:
    messages = [{"role": "system", "content": system_prompt}]
    for role, content in history:
        messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})
    return messages


if __name__ == "__main__":
    history = [
        ("user", "Mera naam Sachin hai."),
        ("assistant", "Nice to meet you, Sachin!"),
    ]
    messages = assemble_messages("You are a friendly assistant.", history, "Mera naam kya hai?")
    for m in messages:
        print(m)
```
_History ko `(role, content)` tuples ki list mein store karo, phir system + history + naya message ek hi array mein order se jodo — yahi format LLM APIs expect karti hain._

## 3. Token Counting & Cost

### 9. `tiktoken` (ya similar) use karke ek function likho jo given text ka token count return kare.

**Answer:**
```python
import tiktoken


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


if __name__ == "__main__":
    print(count_tokens("Hello, how are you doing today?"))
```
_Model-specific encoding na mile to fallback encoding (`cl100k_base`) use karo, warna `KeyError` aayega naye/unknown model names ke liye._

---

### 10. Ek function likho jo conversation history ko max token limit ke andar truncate kare (oldest messages drop karke ya summarize karke).

**Answer:**
```python
def truncate_history(messages: list[dict], max_tokens: int, count_tokens_fn) -> list[dict]:
    system_msgs = [m for m in messages if m["role"] == "system"]
    other_msgs = [m for m in messages if m["role"] != "system"]

    total = sum(count_tokens_fn(m["content"]) for m in system_msgs)
    kept_reversed = []
    for msg in reversed(other_msgs):  # sabse latest message se peeche jao
        msg_tokens = count_tokens_fn(msg["content"])
        if total + msg_tokens > max_tokens:
            break
        total += msg_tokens
        kept_reversed.append(msg)

    return system_msgs + list(reversed(kept_reversed))


if __name__ == "__main__":
    def fake_count(text):
        return len(text.split())

    messages = [
        {"role": "system", "content": "You are helpful"},
        {"role": "user", "content": "message one two three"},
        {"role": "assistant", "content": "reply one two"},
        {"role": "user", "content": "latest question here"},
    ]
    print(truncate_history(messages, max_tokens=8, count_tokens_fn=fake_count))
```
_System message hamesha rakho, phir latest messages se reverse order mein pichhe jao jab tak token budget na khatam ho jaaye — purani (oldest) messages sabse pehle drop hoti hain._

---

### 11. Cost calculator likho — input/output tokens aur model pricing ke basis par total cost estimate kare.

**Answer:**
```python
PRICING_PER_1M_TOKENS = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    if model not in PRICING_PER_1M_TOKENS:
        raise ValueError(f"unknown model: {model}")
    rates = PRICING_PER_1M_TOKENS[model]
    input_cost = (input_tokens / 1_000_000) * rates["input"]
    output_cost = (output_tokens / 1_000_000) * rates["output"]
    return round(input_cost + output_cost, 6)


if __name__ == "__main__":
    print(estimate_cost("gpt-4o-mini", input_tokens=1500, output_tokens=300))
```
_Pricing per-million-token rates ke hisaab se store karo (jaisa providers publish karte hain), phir input aur output tokens ki cost alag-alag calculate karke add karo._

## 4. RAG (Retrieval Augmented Generation)

### 12. Text ko chunks mein split karne wala function likho (fixed size + overlap ke saath).

**Answer:**
```python
def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> list[str]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks


if __name__ == "__main__":
    text = "A" * 500
    chunks = chunk_text(text, chunk_size=200, overlap=50)
    print(len(chunks), [len(c) for c in chunks])
```
_Har next chunk `overlap` characters pichhe se shuru hota hai taaki chunk boundary pe context na toote (sentence beech mein cut na ho)._

---

### 13. Documents ko embed karke ek in-memory vector store banao (numpy/list based cosine similarity).

**Answer:**
```python
import numpy as np


def mock_embed(text: str) -> np.ndarray:
    # real project mein OpenAI/SentenceTransformers embedding call hoga
    rng = np.random.default_rng(abs(hash(text)) % (2**32))
    vec = rng.random(384)
    return vec / np.linalg.norm(vec)


class InMemoryVectorStore:
    def __init__(self):
        self.vectors: list[np.ndarray] = []
        self.texts: list[str] = []

    def add(self, text: str, embed_fn=mock_embed):
        self.vectors.append(embed_fn(text))
        self.texts.append(text)

    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


if __name__ == "__main__":
    store = InMemoryVectorStore()
    for doc in ["cats are great pets", "dogs are loyal animals", "python is a programming language"]:
        store.add(doc)
    print(store.cosine_similarity(store.vectors[0], store.vectors[1]))
```
_Har document ko fixed-dimension vector mein convert karke list mein store karte hain; similarity nikalne ke liye cosine similarity (dot product / magnitudes) use hoti hai._

---

### 14. Query ke liye top-k similar chunks retrieve karne wala function likho (cosine similarity search).

**Answer:**
```python
def retrieve_top_k(store: "InMemoryVectorStore", query: str, k: int = 3, embed_fn=mock_embed) -> list[tuple[str, float]]:
    query_vec = embed_fn(query)
    scored = [
        (text, store.cosine_similarity(query_vec, vec))
        for text, vec in zip(store.texts, store.vectors)
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]


if __name__ == "__main__":
    store = InMemoryVectorStore()
    for doc in ["cats are great pets", "dogs are loyal animals", "python is a programming language"]:
        store.add(doc)
    results = retrieve_top_k(store, "tell me about pets", k=2)
    for text, score in results:
        print(f"{score:.3f} -> {text}")
```
_Query ko bhi embed karke store ke sabhi vectors se compare karo, similarity score ke hisaab se descending sort karo, top-k return karo._

---

### 15. End-to-end mini RAG pipeline banao: documents → chunk → embed → store → retrieve → LLM se answer generate karo.

**Answer:**
```python
def mock_llm_answer(query: str, context_chunks: list[str]) -> str:
    context = "\n---\n".join(context_chunks)
    return f"[mock answer based on context]\nQuery: {query}\nUsed context:\n{context}"


def run_rag_pipeline(documents: list[str], query: str, chunk_size=100, overlap=20, k=2) -> str:
    store = InMemoryVectorStore()
    for doc in documents:
        for chunk in chunk_text(doc, chunk_size=chunk_size, overlap=overlap):
            store.add(chunk)

    top_chunks = [text for text, _ in retrieve_top_k(store, query, k=k)]
    return mock_llm_answer(query, top_chunks)


if __name__ == "__main__":
    docs = [
        "Company policy: annual leave is 24 days per year, accrued monthly.",
        "Sick leave requires a medical certificate after 2 consecutive days.",
    ]
    print(run_rag_pipeline(docs, "Annual leave kitne din milti hai?"))
```
_Pura flow: documents ko chunk karo → har chunk embed karke store mein daalo → query ke liye relevant chunks retrieve karo → un chunks ko context bana kar LLM ko final prompt do._

---

### 16. Re-ranking step add karo (retrieved chunks ko dobara score karke best ones upar lao).

**Answer:**
```python
def keyword_overlap_score(query: str, text: str) -> float:
    query_words = set(query.lower().split())
    text_words = set(text.lower().split())
    if not query_words:
        return 0.0
    return len(query_words & text_words) / len(query_words)


def rerank(query: str, candidates: list[tuple[str, float]], alpha: float = 0.5) -> list[tuple[str, float]]:
    reranked = []
    for text, vector_score in candidates:
        keyword_score = keyword_overlap_score(query, text)
        final_score = alpha * vector_score + (1 - alpha) * keyword_score
        reranked.append((text, final_score))
    reranked.sort(key=lambda x: x[1], reverse=True)
    return reranked


if __name__ == "__main__":
    candidates = [
        ("annual leave policy is 24 days", 0.62),
        ("sick leave needs medical certificate", 0.58),
    ]
    print(rerank("annual leave days", candidates))
```
_Vector similarity ke saath ek dusra signal (keyword overlap, cross-encoder score, recency etc.) combine karke chunks ko dobara sort karte hain — retrieval recall high rakhte hue precision improve hoti hai._

---

### 17. Hybrid search implement karo (keyword/BM25 + vector similarity combine karke).

**Answer:**
```python
from rank_bm25 import BM25Okapi


def hybrid_search(query: str, documents: list[str], store: "InMemoryVectorStore", k: int = 3, alpha: float = 0.5):
    tokenized_docs = [doc.lower().split() for doc in documents]
    bm25 = BM25Okapi(tokenized_docs)
    bm25_scores = bm25.get_scores(query.lower().split())
    max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1.0
    bm25_scores_norm = [s / max_bm25 for s in bm25_scores]

    vector_results = dict(retrieve_top_k(store, query, k=len(documents)))

    combined = []
    for i, doc in enumerate(documents):
        vec_score = vector_results.get(doc, 0.0)
        final_score = alpha * vec_score + (1 - alpha) * bm25_scores_norm[i]
        combined.append((doc, final_score))

    combined.sort(key=lambda x: x[1], reverse=True)
    return combined[:k]


if __name__ == "__main__":
    docs = ["annual leave policy is 24 days", "sick leave needs medical certificate", "python programming basics"]
    store = InMemoryVectorStore()
    for d in docs:
        store.add(d)
    print(hybrid_search("leave policy", docs, store))
```
_BM25 exact keyword matches ke liye strong hota hai, vector search semantic/paraphrased matches pakadta hai — dono ke normalized scores ko weighted-average karke combine karte hain._

## 5. Function Calling / Tool Use / Agents

### 18. Ek "tool" define karo (jaise `get_weather(city)`) aur LLM ko function-calling ke through use karwao.

**Answer:**
```python
import json
from openai import OpenAI

client = OpenAI()


def get_weather(city: str) -> dict:
    # mock — real mein weather API call hoga
    return {"city": city, "temp_c": 28, "condition": "sunny"}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    }
]


def chat_with_tool(user_prompt: str):
    messages = [{"role": "user", "content": user_prompt}]
    response = client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=TOOLS)
    message = response.choices[0].message

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        result = get_weather(**args)
        messages.append(message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result),
        })
        final = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
        return final.choices[0].message.content
    return message.content
```
_Tool ko JSON schema (name, description, parameters) mein define karte hain; model decide karta hai kab call karna hai, hum uske arguments extract karke actual Python function run karte hain, result wapas model ko bhejte hain._

---

### 19. Simple ReAct-style agent loop likho: LLM decide kare kaunsa tool call karna hai, result observe kare, phir final answer de.

**Answer:**
```python
def mock_llm_decide(query: str, observations: list[str]) -> dict:
    if not observations:
        return {"action": "search", "input": query}
    return {"action": "final_answer", "input": f"Based on search: {observations[-1]}"}


def mock_search_tool(query: str) -> str:
    return f"search result for '{query}': answer is 42"


def react_loop(query: str, max_steps: int = 5) -> str:
    observations = []
    for step in range(max_steps):
        decision = mock_llm_decide(query, observations)
        print(f"step {step}: action={decision['action']}, input={decision['input']}")

        if decision["action"] == "final_answer":
            return decision["input"]

        if decision["action"] == "search":
            observation = mock_search_tool(decision["input"])
            observations.append(observation)

    return "could not find an answer in max steps"


if __name__ == "__main__":
    print(react_loop("what is the answer to life?"))
```
_Loop: Thought (LLM decide karta hai) → Action (tool call) → Observation (result) → repeat, jab tak LLM "final_answer" na de ya max_steps khatam na ho jaaye._

---

### 20. Multiple tools ke beech LLM ko route karne wala dispatcher likho (tool name se actual Python function call karo).

**Answer:**
```python
def get_weather(city: str) -> str:
    return f"Weather in {city}: 28C, sunny"


def get_stock_price(symbol: str) -> str:
    return f"{symbol} price: $150"


TOOL_REGISTRY = {
    "get_weather": get_weather,
    "get_stock_price": get_stock_price,
}


def dispatch_tool_call(tool_name: str, arguments: dict):
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(f"unknown tool: {tool_name}")
    return TOOL_REGISTRY[tool_name](**arguments)


if __name__ == "__main__":
    print(dispatch_tool_call("get_weather", {"city": "Mumbai"}))
    print(dispatch_tool_call("get_stock_price", {"symbol": "AAPL"}))
```
_Tool name → function mapping ek dict (registry) mein rakho, LLM se aaya `tool_name` aur `arguments` (JSON) use karke seedha `**kwargs` se call kar do._

## 6. Memory / Conversation Management

### 21. Chatbot ke liye conversation memory class banao jo history store kare aur token-limit ke andar rakhe.

**Answer:**
```python
class ConversationMemory:
    def __init__(self, max_tokens: int = 2000, count_tokens_fn=lambda t: len(t.split())):
        self.max_tokens = max_tokens
        self.count_tokens_fn = count_tokens_fn
        self.messages: list[dict] = []

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        self._trim()

    def _trim(self):
        total = sum(self.count_tokens_fn(m["content"]) for m in self.messages)
        while total > self.max_tokens and len(self.messages) > 1:
            removed = self.messages.pop(0)
            total -= self.count_tokens_fn(removed["content"])

    def get_history(self) -> list[dict]:
        return self.messages


if __name__ == "__main__":
    memory = ConversationMemory(max_tokens=10)
    memory.add("user", "hello there how are you")
    memory.add("assistant", "I am fine thank you")
    memory.add("user", "what is python")
    print(memory.get_history())
```
_Har `add` ke baad total token count check karo, limit cross ho to sabse purani message (index 0) drop karte jao jab tak budget ke andar na aa jaye._

---

### 22. Long conversation ko summarize karke context window save karne wala function likho (summary + recent messages).

**Answer:**
```python
def mock_summarize(messages: list[dict]) -> str:
    topics = [m["content"][:30] for m in messages]
    return "Summary of earlier conversation: " + "; ".join(topics)


def compress_conversation(messages: list[dict], keep_recent: int = 4) -> list[dict]:
    if len(messages) <= keep_recent:
        return messages

    old_messages = messages[:-keep_recent]
    recent_messages = messages[-keep_recent:]

    summary = mock_summarize(old_messages)
    return [{"role": "system", "content": summary}] + recent_messages


if __name__ == "__main__":
    messages = [{"role": "user", "content": f"message {i}"} for i in range(10)]
    compressed = compress_conversation(messages, keep_recent=3)
    for m in compressed:
        print(m)
```
_Purani messages ko ek summary message mein compress karo (system role se prepend), recent N messages ko as-is rakho — isse context window mein jagah bachti hai lekin history ka essence bana rehta hai._

## 7. Caching

### 23. Exact-match cache implement karo (same prompt → cached response, LLM call skip).

**Answer:**
```python
import hashlib


class ExactMatchCache:
    def __init__(self):
        self._cache: dict[str, str] = {}

    def _key(self, prompt: str) -> str:
        return hashlib.sha256(prompt.encode()).hexdigest()

    def get(self, prompt: str) -> str | None:
        return self._cache.get(self._key(prompt))

    def set(self, prompt: str, response: str):
        self._cache[self._key(prompt)] = response


def cached_chat(prompt: str, cache: ExactMatchCache, llm_call_fn) -> str:
    cached = cache.get(prompt)
    if cached is not None:
        print("cache hit")
        return cached

    print("cache miss, calling LLM")
    response = llm_call_fn(prompt)
    cache.set(prompt, response)
    return response


if __name__ == "__main__":
    cache = ExactMatchCache()
    fake_llm = lambda p: f"answer to: {p}"
    print(cached_chat("what is 2+2", cache, fake_llm))
    print(cached_chat("what is 2+2", cache, fake_llm))  # cache hit
```
_Prompt ka hash key bana kar dict mein response store karo; same prompt dobara aaye to LLM call skip karke seedha cached response return karo._

---

### 24. Semantic caching likho — embedding similarity check karke similar query ka cached response return karo.

**Answer:**
```python
class SemanticCache:
    def __init__(self, similarity_threshold: float = 0.9, embed_fn=mock_embed):
        self.threshold = similarity_threshold
        self.embed_fn = embed_fn
        self.entries: list[tuple[str, "np.ndarray", str]] = []  # (query, vector, response)

    def _cosine(self, a, b) -> float:
        import numpy as np
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def get(self, query: str) -> str | None:
        query_vec = self.embed_fn(query)
        best_score, best_response = 0.0, None
        for _, vec, response in self.entries:
            score = self._cosine(query_vec, vec)
            if score > best_score:
                best_score, best_response = score, response
        if best_score >= self.threshold:
            return best_response
        return None

    def set(self, query: str, response: str):
        self.entries.append((query, self.embed_fn(query), response))


if __name__ == "__main__":
    cache = SemanticCache(similarity_threshold=0.0)  # mock embeddings random hain, isliye threshold 0 rakha demo ke liye
    cache.set("what is the capital of France", "Paris")
    print(cache.get("capital of France?"))
```
_Query ko embed karke cache mein stored query-vectors se cosine similarity nikalo; threshold se upar match mile to uska response return karo — paraphrased queries bhi cache hit hoti hain._

## 8. Evaluation & Guardrails

### 25. "LLM-as-judge" function likho jo do responses compare kare aur better one select kare (with reasoning).

**Answer:**
```python
def llm_as_judge(query: str, response_a: str, response_b: str, llm_call_fn) -> dict:
    judge_prompt = f"""You are an impartial judge. Compare the two responses to the query and decide which is better.

Query: {query}

Response A: {response_a}

Response B: {response_b}

Reply in the format:
Winner: A or B
Reasoning: <one sentence>"""

    result = llm_call_fn(judge_prompt)
    winner = "A" if "Winner: A" in result else "B"
    return {"winner": winner, "raw": result}


def mock_judge_llm(prompt: str) -> str:
    return "Winner: A\nReasoning: Response A is more concise and directly answers the question."


if __name__ == "__main__":
    result = llm_as_judge(
        "What is RAG?",
        "RAG combines retrieval with generation to ground LLM answers in real data.",
        "RAG is a thing in AI.",
        mock_judge_llm,
    )
    print(result)
```
_Judge ko dono responses + query ek structured prompt mein do, usse fixed format (Winner + Reasoning) mein reply mangwao, phir output parse karo._

---

### 26. Simple content moderation/guardrail function likho jo harmful/off-topic queries ko LLM tak jaane se pehle filter kare.

**Answer:**
```python
import re

BLOCKED_PATTERNS = [
    r"\bhow to (make|build) a bomb\b",
    r"\bhack (into|a) .* account\b",
    r"\bself[\s-]?harm\b",
]

OFF_TOPIC_KEYWORDS = ["politics", "religion"]


def moderate_query(query: str, allowed_topics_only: bool = False) -> dict:
    lowered = query.lower()

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, lowered):
            return {"allowed": False, "reason": "harmful_content"}

    if allowed_topics_only:
        for keyword in OFF_TOPIC_KEYWORDS:
            if keyword in lowered:
                return {"allowed": False, "reason": "off_topic"}

    return {"allowed": True, "reason": None}


if __name__ == "__main__":
    print(moderate_query("how to make a bomb"))
    print(moderate_query("what is the weather today"))
```
_Real production mein regex ke bajaye moderation API (OpenAI Moderation, Llama Guard) use hoti hai — yeh simple rule-based version hai jo interview mein logic dikhane ke liye kaafi hai._

---

### 27. RAG output ke liye faithfulness check likho (kya generated answer sirf retrieved context se hi aa raha hai, ya hallucinate ho raha hai).

**Answer:**
```python
def faithfulness_check(answer: str, context_chunks: list[str], llm_call_fn) -> dict:
    context = "\n---\n".join(context_chunks)
    prompt = f"""Given the CONTEXT below, check if the ANSWER is fully supported by it.
Reply "FAITHFUL" if every claim in the answer is backed by the context, otherwise "HALLUCINATED" and list unsupported claims.

CONTEXT:
{context}

ANSWER:
{answer}
"""
    verdict = llm_call_fn(prompt)
    return {"faithful": verdict.strip().startswith("FAITHFUL"), "raw": verdict}


def mock_faithfulness_llm(prompt: str) -> str:
    return "HALLUCINATED\nUnsupported claim: 'leave carries over indefinitely' is not in context."


if __name__ == "__main__":
    result = faithfulness_check(
        "Annual leave is 24 days and carries over indefinitely.",
        ["Company policy: annual leave is 24 days per year, accrued monthly."],
        mock_faithfulness_llm,
    )
    print(result)
```
_Ek dusre LLM call (ya same model, alag prompt) se pucho ki answer ke claims context mein exist karte hain ya nahi — yeh basically "LLM-as-judge" ka RAG-specific version hai._

## 9. Data & Fine-tuning Prep

### 28. Raw conversation logs ko fine-tuning ke liye JSONL format mein convert karne wala script likho.

**Answer:**
```python
import json


def convert_to_jsonl(conversations: list[list[dict]], output_path: str, system_prompt: str = "You are a helpful assistant."):
    with open(output_path, "w", encoding="utf-8") as f:
        for conversation in conversations:
            record = {"messages": [{"role": "system", "content": system_prompt}] + conversation}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    conversations = [
        [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello!"}],
        [{"role": "user", "content": "2+2?"}, {"role": "assistant", "content": "4"}],
    ]
    convert_to_jsonl(conversations, "training_data.jsonl")
```
_OpenAI fine-tuning format mein har line ek JSON object hoti hai jisme `messages` key ke andar system+user+assistant turns hote hain — file line-by-line (JSONL) likhi jaati hai, ek pura JSON array nahi._

---

### 29. Duplicate/near-duplicate training examples detect aur remove karne wala function likho (embedding similarity se).

**Answer:**
```python
def dedupe_examples(examples: list[str], similarity_threshold: float = 0.95, embed_fn=mock_embed) -> list[str]:
    import numpy as np

    kept: list[str] = []
    kept_vecs: list[np.ndarray] = []

    for example in examples:
        vec = embed_fn(example)
        is_duplicate = False
        for kept_vec in kept_vecs:
            score = float(np.dot(vec, kept_vec) / (np.linalg.norm(vec) * np.linalg.norm(kept_vec)))
            if score >= similarity_threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            kept.append(example)
            kept_vecs.append(vec)

    return kept


if __name__ == "__main__":
    examples = ["how to reset my password", "how do I reset my password?", "what is the weather today"]
    print(dedupe_examples(examples, similarity_threshold=0.99))
```
_Har naye example ko ab tak kept examples ke embeddings se compare karo; threshold se zyada similarity ho to usse duplicate maan kar skip karo, warna list mein add karo._

## 10. Structured Output

### 30. LLM se JSON output nikalwane wala function likho aur output ko Pydantic model se validate karo.

**Answer:**
```python
import json
from pydantic import BaseModel, ValidationError


class Person(BaseModel):
    name: str
    age: int
    email: str


def get_structured_output(llm_response_text: str) -> Person:
    data = json.loads(llm_response_text)
    return Person(**data)


if __name__ == "__main__":
    mock_llm_response = '{"name": "Sachin", "age": 28, "email": "sachin@example.com"}'
    person = get_structured_output(mock_llm_response)
    print(person)

    try:
        get_structured_output('{"name": "Sachin", "age": "not-a-number"}')
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"validation failed: {e}")
```
_LLM se JSON string mangwao (system prompt mein schema/format specify karo), `json.loads` se parse karo, phir Pydantic model se validate karo — dono jagah exception handle karo (malformed JSON aur schema mismatch)._

---

### 31. Agar LLM invalid JSON return kare to ek retry-with-correction loop likho (error message wapas LLM ko bhejo, fix karwao).

**Answer:**
```python
import json
from pydantic import BaseModel, ValidationError


class Person(BaseModel):
    name: str
    age: int
    email: str


def get_structured_output_with_retry(initial_prompt: str, llm_call_fn, max_retries: int = 3) -> Person:
    prompt = initial_prompt

    for attempt in range(max_retries):
        response_text = llm_call_fn(prompt)
        try:
            data = json.loads(response_text)
            return Person(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"attempt {attempt + 1} failed: {e}")
            prompt = (
                f"{initial_prompt}\n\n"
                f"Your previous response was invalid: {response_text}\n"
                f"Error: {e}\n"
                f"Please return ONLY valid JSON matching the schema: "
                f"{{\"name\": str, \"age\": int, \"email\": str}}"
            )

    raise RuntimeError("failed to get valid structured output after retries")


# --- mock LLM: pehli baar galat, doosri baar sahi JSON deta hai ---
_attempt_counter = {"n": 0}


def mock_llm_call(prompt: str) -> str:
    _attempt_counter["n"] += 1
    if _attempt_counter["n"] == 1:
        return '{"name": "Sachin", "age": "twenty eight"}'  # invalid: age string hai
    return '{"name": "Sachin", "age": 28, "email": "sachin@example.com"}'


if __name__ == "__main__":
    person = get_structured_output_with_retry("Give me a person's details as JSON.", mock_llm_call)
    print(person)
```
_Jab parsing/validation fail ho, error message aur previous (invalid) response ko next prompt mein include karke LLM ko wapas bhejo — model apni galti dekh kar corrected JSON return karta hai._

---

### Practice tip
Har question ko pehle **bina AI API call kiye** (mock/dummy response se) implement karo — logic (chunking, retry, caching, token counting) test karna easy ho jayega. Phir real API se connect karo.

Answers already ऊपर mock-based hain — pehle khud se try karo, phir compare karo, phir chaho to real OpenAI/Anthropic API laga kar end-to-end test karo.
