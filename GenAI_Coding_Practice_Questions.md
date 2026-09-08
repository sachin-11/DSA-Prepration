# GenAI Coding Interview Questions — Practice List

Topics ke hisaab se grouped hai. Har question ko `AICodingQuestions.py` (ya alag file) mein khud implement karo.

## 1. LLM API Basics & Reliability
1. OpenAI/Anthropic API ko call karke ek simple chat function likho (system + user message ke saath).
2. Exponential backoff with jitter implement karo API rate-limit errors ke liye (retry logic).
3. Streaming response handle karo — tokens as they arrive print karo (SSE/streaming API).
4. Timeout aur connection error ke liye robust error handling likho (retryable vs non-retryable errors alag karo).
5. Multiple API keys/providers ke beech fallback logic likho (agar ek provider fail ho to dusre pe switch ho jaye).

## 2. Prompt Engineering / Templating
6. Ek reusable prompt template class/function banao jisme variables inject ho sakein (jinja2 ya f-string based).
7. Few-shot prompt banane wala function likho jo examples list se dynamically prompt construct kare.
8. System prompt + conversation history ko ek single messages array mein assemble karne wala function likho.

## 3. Token Counting & Cost
9. `tiktoken` (ya similar) use karke ek function likho jo given text ka token count return kare.
10. Ek function likho jo conversation history ko max token limit ke andar truncate kare (oldest messages drop karke ya summarize karke).
11. Cost calculator likho — input/output tokens aur model pricing ke basis par total cost estimate kare.

## 4. RAG (Retrieval Augmented Generation)
12. Text ko chunks mein split karne wala function likho (fixed size + overlap ke saath).
13. Documents ko embed karke ek in-memory vector store banao (numpy/list based cosine similarity).
14. Query ke liye top-k similar chunks retrieve karne wala function likho (cosine similarity search).
15. End-to-end mini RAG pipeline banao: documents → chunk → embed → store → retrieve → LLM se answer generate karo.
16. Re-ranking step add karo (retrieved chunks ko dobara score karke best ones upar lao).
17. Hybrid search implement karo (keyword/BM25 + vector similarity combine karke).

## 5. Function Calling / Tool Use / Agents
18. Ek "tool" define karo (jaise `get_weather(city)`) aur LLM ko function-calling ke through use karwao.
19. Simple ReAct-style agent loop likho: LLM decide kare kaunsa tool call karna hai, result observe kare, phir final answer de.
20. Multiple tools ke beech LLM ko route karne wala dispatcher likho (tool name se actual Python function call karo).

## 6. Memory / Conversation Management
21. Chatbot ke liye conversation memory class banao jo history store kare aur token-limit ke andar rakhe.
22. Long conversation ko summarize karke context window save karne wala function likho (summary + recent messages).

## 7. Caching
23. Exact-match cache implement karo (same prompt → cached response, LLM call skip).
24. Semantic caching likho — embedding similarity check karke similar query ka cached response return karo.

## 8. Evaluation & Guardrails
25. "LLM-as-judge" function likho jo do responses compare kare aur better one select kare (with reasoning).
26. Simple content moderation/guardrail function likho jo harmful/off-topic queries ko LLM tak jaane se pehle filter kare.
27. RAG output ke liye faithfulness check likho (kya generated answer sirf retrieved context se hi aa raha hai, ya hallucinate ho raha hai).

## 9. Data & Fine-tuning Prep
28. Raw conversation logs ko fine-tuning ke liye JSONL format mein convert karne wala script likho.
29. Duplicate/near-duplicate training examples detect aur remove karne wala function likho (embedding similarity se).

## 10. Structured Output
30. LLM se JSON output nikalwane wala function likho aur output ko Pydantic model se validate karo.
31. Agar LLM invalid JSON return kare to ek retry-with-correction loop likho (error message wapas LLM ko bhejo, fix karwao).

---

### Practice tip
Har question ko pehle **bina AI API call kiye** (mock/dummy response se) implement karo — logic (chunking, retry, caching, token counting) test karna easy ho jayega. Phir real API se connect karo.
