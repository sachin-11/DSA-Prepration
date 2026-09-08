# GenAI Scenario-Based Interview Questions (Experienced Candidate)

## Question 1: RAG Pipeline Giving Wrong/Outdated Answers

**Scenario:**
Aapki company ne ek internal chatbot banaya hai jo company ke policy documents (HR policies, leave rules, etc.) par RAG (Retrieval Augmented Generation) use karke employees ke sawalon ka jawab deta hai. Recently employees complain kar rahe hain ki chatbot purani (outdated) policy ka jawab de raha hai, jabki documents update ho chuke hain. Kabhi kabhi wo completely galat/hallucinated answer bhi de deta hai. Aap iss problem ko kaise debug aur fix karenge?

**Answer:**

Iss problem ko systematically approach karna chahiye — retrieval side aur generation side dono ko alag-alag check karke:

1. **Root cause identify karo (Retrieval vs Generation issue):**
   - Pehle check karo ki retrieved chunks hi purane hain, ya retrieval sahi hai lekin LLM generation mein galti ho rahi hai.
   - Retrieved context ko log/print karke dekho ki actual mein kya chunks LLM ko pass ho rahe hain.

2. **Outdated answers ka fix — Ingestion pipeline issue:**
   - Vector DB mein document re-indexing properly ho raha hai ya nahi check karo. Agar documents update hote hain to purane embeddings delete/overwrite hone chahiye (versioning ya document ID based upsert use karo).
   - Ek automated pipeline (CI/CD jaisa) banao jo document change hone par turant re-embed aur re-index kare (event-driven ingestion), instead of manual/batch update jo delay create karta hai.
   - Metadata mein `last_updated` timestamp store karo aur retrieval ke time recency ko bhi factor mein lo (hybrid ranking: similarity + recency).

3. **Hallucination ka fix:**
   - Prompt mein strict instruction do: "Answer only from the provided context. If the answer is not present, say 'I don't have this information.'"
   - Retrieval quality improve karo — chunk size, overlap, aur embedding model tune karo. Agar chunks bahut chhote/bade hain to relevant context miss ho sakta hai.
   - Re-ranking step add karo (e.g., cross-encoder re-ranker) taaki top-k retrieved chunks sabse relevant ho.
   - Grounding/citation add karo — jawab ke saath source document reference do, taaki verify karna easy ho aur hallucination visible ho jaye.

4. **Evaluation & Monitoring:**
   - Ek eval set banao (golden Q&A pairs) aur regularly test karo (RAGAS jaise framework se faithfulness, answer relevancy, context precision/recall measure karo).
   - Production mein user feedback loop (thumbs up/down) add karo taaki bad answers track ho sakein.

**Key takeaway:** Outdated answers zyadatar ek ingestion/indexing pipeline problem hoti hai, jabki hallucination ek prompt engineering + retrieval quality problem hoti hai. Dono ko alag treat karna zaroori hai.

---

## Question 2: LLM API Costs and Latency Spiking in Production

**Scenario:**
Aapka production application ek LLM API (jaise GPT/Claude) use karta hai customer support summarization ke liye. Traffic badhne ke saath saath API costs bahut zyada ho gaye hain aur response latency bhi increase ho gayi hai, jisse user experience kharab ho raha hai. Product team ne aapko task diya hai ki cost aur latency dono ko optimize karo, without significantly compromising output quality. Aap kya approach lenge?

**Answer:**

Ye ek classic cost-latency-quality tradeoff problem hai. Multiple layers par optimization karna hoga:

1. **Caching:**
   - Semantic caching implement karo — agar similar/same query pehle aa chuki hai, to LLM call kiye bina cached response return karo (embedding similarity based cache lookup).
   - Exact match caching bhi lagao common/repeated summarization requests ke liye.

2. **Model selection & routing:**
   - Har request ke liye sabse bada/expensive model use karna zaroori nahi hota. Ek model routing layer banao — simple/short queries ke liye smaller, cheaper, faster model (e.g., Haiku-tier) use karo, aur complex queries ke liye bada model (e.g., Sonnet/Opus-tier).
   - Task-specific fine-tuned smaller model bhi consider karo agar summarization ek narrow, repetitive task hai — ye latency aur cost dono kam karta hai.

3. **Prompt & token optimization:**
   - Prompt ko concise karo, unnecessary context/instructions hatao. Har extra token cost aur latency badhata hai.
   - Input truncation/summarization karo — agar conversation history bahut lambi hai, to sirf relevant/recent part hi context mein bhejo (sliding window ya prior summary use karo).
   - Output token limit (`max_tokens`) sensibly set karo taaki model zaroorat se zyada verbose na ho.

4. **Batching & async processing:**
   - Agar summarization real-time critical nahi hai (e.g., end-of-day reports), to requests batch karke process karo instead of one-by-one synchronous calls.
   - Streaming responses use karo real-time use cases ke liye taaki perceived latency kam lage (user ko partial output turant dikhna start ho jaye).

5. **Infrastructure-level:**
   - Connection pooling, retries with exponential backoff, aur timeout tuning karo taaki transient failures se latency spike na ho.
   - Rate limiting aur concurrency control add karo taaki traffic spikes API provider ke limits se na takrayein.

6. **Monitoring:**
   - Cost aur latency ko per-request track karo (token usage, model used, response time), dashboard banao, aur alerts set karo threshold cross hone par.
   - A/B testing karo optimization changes ke baad — quality metrics (accuracy, user satisfaction) drop na ho ye verify karne ke liye.

**Key takeaway:** Cost/latency optimization ek single fix nahi hota — caching, right-sized model selection, prompt efficiency, aur infra tuning — inn sab ka combination use karna padta hai, aur har change ke baad output quality ko measure karna zaroori hai.
