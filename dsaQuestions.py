# two sums
def twoSums(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        need = target - num
        if need in seen:
            return [seen[need], i]
        seen[num] = i
    return []

result = twoSums([2, 7, 11, 15], 9)
print(result)


# maxprofit 
def maxProfit(prices):
    min_price, best = float("inf"), 0
    for p in prices:
        min_price = min(min_price, p)
        best = max(best, p - min_price)
    return best

result = maxProfit([7, 1, 5, 3, 6, 4])   
print(result) 

# contained Duplicate
def containedDuplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

result = containedDuplicate([1,2,3,4])   
print(result) 

# is valid pallidrom 
def is_pallidrom(string):
    okay = lambda c: c.isalnum()
    left, right = 0,  len(string) - 1
    while left < right:
        while left < right and not okay(string[left]): left += 1
        while left < right and not okay(string[right]): right -= 1
        if string[left].lower() != string[right].lower():
            return False
        left += 1
        right -= 1
    return True

result = is_pallidrom("race a car")


def threeSum(nums):
    nums.sort()
    res = []
    n = len(nums)
    for i in range( n - 2):
        if(i > 0 and nums[i] == nums[i - 1]):
            continue
        left, right = i + 1, n - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                res.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]: left += 1
                while left < right and nums[right] == nums[right - 1]: right -= 1
                left += 1
                right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1
    return res;   


result = threeSum([-1, 0, 1, 2, -1, -4])
print(result)


# maxSubArraySum 

def max_sub_array_sum(nums):
    curr = best = nums[0]
    for num in nums[1:]:
        curr = max(num, curr + num)
        best = max(best, curr)
    return best

result = max_sub_array_sum([-2,1,-3,4,-1,2,1,-5,4]) 
print(result)

# logest substring bethought repeating charector
def logest_substring_count(strings):
     seen = set()
     left = 0
     best_start, best_len = 0, 0
     for right in range(len(strings)):
        while strings[right] in seen:
            seen.remove(strings[left])
            left += 1
        seen.add(strings[right])
        if right - left + 1 > best_len:
            best_len = right - left + 1
            best_start = left
     return strings[best_start:best_start + best_len]


result = logest_substring_count("sdjshjjdshhd")
print(result)


def longest_substring_count(strings):
    seen = set()
    left = 0
    best_start, best_length = 0, 0
    for right in range(len(strings)):
        while strings[right] in seen:
            seen.remove(strings[left])
            left += 1
        seen.add(strings[right])
        if right - left + 1 > best_length:
            best_length = right - left + 1
            best_start = left
    return strings[best_start: best_start + best_length]    


# 3. Count character values in list and print in tuple format
# Counter usage + tuples: Counter.items() (element, count) pairs deta hai,
# yeh already tuples hote hain.
from collections import Counter


def count_characters(chars):
    counts = Counter(chars)
    return list(counts.items())


result = count_characters(["a", "b", "a", "c", "b", "a"])
print(result)

from collections import Counter

def count_charectors(chars):
    counts = Counter(chars)
    return list(counts.items())


# 4. Conditional Graph in Python (LangGraph)
# Conditional graph: directed graph jisme next node dynamically decide hota
# hai current state / previous node ke output ke basis par.
# - StateGraph: LangGraph ki main class. Nodes = functions, Edges = transitions,
#   State = shared TypedDict.
# - add_conditional_edges: ek function leta hai jo state dekh kar next node
#   ka naam return karta hai.
# - TypedDict: Python ka typed dictionary — LangGraph state structure
#   type hints ke saath define karne ke liye use hota hai.
# Yeh hi agentic AI workflows ki foundation hai — agent ka "what to do next"
# decision literally ek conditional edge hai.
from typing import TypedDict
from langgraph.graph import StateGraph, END


class GraphState(TypedDict):
    number: int
    result: str


def start_node(state: GraphState) -> GraphState:
    print(f"start_node: number={state['number']}")
    return state


def even_node(state: GraphState) -> GraphState:
    state["result"] = f"{state['number']} is even"
    return state


def odd_node(state: GraphState) -> GraphState:
    state["result"] = f"{state['number']} is odd"
    return state


def router(state: GraphState) -> str:
    return "even_node" if state["number"] % 2 == 0 else "odd_node"


builder = StateGraph(GraphState)
builder.add_node("start", start_node)
builder.add_node("even_node", even_node)
builder.add_node("odd_node", odd_node)

builder.set_entry_point("start")
builder.add_conditional_edges("start", router, {"even_node": "even_node", "odd_node": "odd_node"})
builder.add_edge("even_node", END)
builder.add_edge("odd_node", END)

graph = builder.compile()

print(graph.invoke({"number": 4, "result": ""}))
print(graph.invoke({"number": 7, "result": ""}))


# 5. Function: a=1, b=1, c=2, d=4 — Can a rectangle be formed?
# Rectangle ke liye exactly do pairs of equal sides chahiye. 4 values ko
# sort karo, pehle do equal AND aakhri do equal hone chahiye.
# Edge case: square bhi ek rectangle hai (chaaron sides equal = do pairs of 2).
def can_form_rectangle(a, b, c, d):
    sides = sorted([a, b, c, d])
    return sides[0] == sides[1] and sides[2] == sides[3]


print(can_form_rectangle(1, 1, 2, 4))  # False
print(can_form_rectangle(2, 2, 4, 4))  # True
print(can_form_rectangle(3, 3, 3, 3))  # True (square)


# 6. DSA — Merge Overlapping Intervals
# Pehle start time ke hisaab se sort karo — isse overlapping intervals
# adjacent aa jaate hain. Fir har interval ke liye check karo:
# current_start <= last_merged_end -> overlap hai, end ko extend karo
# (max lo, taaki ek interval dusre ke andar fully ho to bhi sahi rahe).
# Time: O(n log n) sorting ke wajah se. Space: O(n) result ke liye.
def merge_intervals(intervals):
    if not intervals:
        return []

    sorted_intervals = sorted(intervals, key=lambda interval: interval[0])
    merged = [sorted_intervals[0]]

    for start, end in sorted_intervals[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = [last_start, max(last_end, end)]
        else:
            merged.append([start, end])

    return merged


print(merge_intervals([[1, 3], [2, 5], [7, 9], [8, 10]]))  # [[1, 5], [7, 10]]


# 7. RAG (Retrieval Augmented Generation) — mini end-to-end pipeline
# Interview mein bohot common hai: documents -> chunk -> embed -> store ->
# retrieve (query se cosine similarity) -> LLM ko context ke saath bhej kar
# answer generate karo. Yahan embedding/LLM dono mock hain (bina API key ke
# test karne ke liye) — real project mein embed_text() OpenAI/SentenceTransformers
# embedding call banega aur generate_answer() actual LLM call.
import numpy as np


def chunk_text(text: str, chunk_size: int = 100, overlap: int = 20) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def embed_text(text: str) -> np.ndarray:
    rng = np.random.default_rng(abs(hash(text)) % (2**32))
    vec = rng.random(64)
    return vec / np.linalg.norm(vec)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


class VectorStore:
    def __init__(self):
        self.texts: list[str] = []
        self.vectors: list[np.ndarray] = []

    def add(self, text: str):
        self.texts.append(text)
        self.vectors.append(embed_text(text))

    def retrieve_top_k(self, query: str, k: int = 2) -> list[str]:
        query_vec = embed_text(query)
        scored = [
            (text, cosine_similarity(query_vec, vec))
            for text, vec in zip(self.texts, self.vectors)
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [text for text, _ in scored[:k]]


def generate_answer(query: str, context_chunks: list[str]) -> str:
    context = "\n".join(context_chunks)
    return f"[mock LLM answer]\nQuery: {query}\nUsing context:\n{context}"


def run_rag_pipeline(documents: list[str], query: str, k: int = 2) -> str:
    store = VectorStore()
    for doc in documents:
        for chunk in chunk_text(doc):
            store.add(chunk)

    top_chunks = store.retrieve_top_k(query, k=k)
    return generate_answer(query, top_chunks)


documents = [
    "Company policy: annual leave is 24 days per year, accrued monthly.",
    "Sick leave requires a medical certificate after 2 consecutive days.",
]
print(run_rag_pipeline(documents, "annual leave kitne din milti hai?"))


# 7b. Same RAG pipeline — LangChain version
# Real project mein embeddings = OpenAIEmbeddings(), llm = ChatOpenAI() hoga
# (API key chahiye). Yahan bina API key ke test karne ke liye
# DeterministicFakeEmbedding aur FakeListChatModel use kiya hai — pipeline
# ka structure/logic same rehta hai, sirf real classes plug karni hain.
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.prompts import ChatPromptTemplate


def run_langchain_rag_pipeline(raw_documents: list[str], query: str, k: int = 2) -> str:
    # 1. chunk
    splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    docs = splitter.create_documents(raw_documents)

    # 2. embed + store
    embeddings = DeterministicFakeEmbedding(size=64)  # real: OpenAIEmbeddings()
    vectorstore = InMemoryVectorStore(embeddings)
    vectorstore.add_documents(docs)

    # 3. retrieve
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    retrieved_docs = retriever.invoke(query)
    context = "\n".join(doc.page_content for doc in retrieved_docs)

    # 4. generate answer
    llm = FakeListChatModel(responses=["Mocked answer based on retrieved context."])  # real: ChatOpenAI()
    prompt = ChatPromptTemplate.from_template(
        "Answer the question using only the context below.\n\nContext:\n{context}\n\nQuestion: {question}"
    )
    chain = prompt | llm
    response = chain.invoke({"context": context, "question": query})
    return response.content


print(run_langchain_rag_pipeline(documents, "annual leave kitne din milti hai?"))
