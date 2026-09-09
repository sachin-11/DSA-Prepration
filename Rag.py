from langchain.documents_loader import pypdfloader
from langchain.text_splitter import RecursiveCharectorTextSplitter
from langchain.embedding import openAIEmbedding
from langchain.vector_stores import pinecone
from langchain.chat_model import OpenAI
from langchain.chain import RetriveQa

# load the documnts
loader = pypdfloader("company policy.docs")
documents = loader.load()
print(f"loader {documents} for the page")


# splitter the charector using recursive text splitter
splitter = RecursiveCharectorTextSplitter(
    chunk = 500,
    chunkOverLap = 50,
    seprerator = ["\n\n", "\n", ".", " "]
)

chunk = splitter.split_documents(documents)
print(f"chunk documents {chunk}")


# make embedding
embedding = openAIEmbedding(
    model = "text-embedding-3-small"
)

# store in database
pinecone.init(
api_key="your-pinecone-key",
  environment="ap-southeast-1"
)

# make Rag chain

qachain = RetriveQa.from_chain_type(
    llm = llm,
    retrival = vectorstore.as_retrival(
        search_kwarg = {"k": 3}
    ),
    return_source_documents = True
)


# make Query 

result = qa_chain({
    "query":  "Anual leave kitne din me milti he"
})

print(f"anwer {result}")
print(f"source: {result['source_documents']}")
