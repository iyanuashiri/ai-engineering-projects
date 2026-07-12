import os
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import chain
from langsmith import traceable

import pypdf
from decouple import config


os.environ["LANGSMITH_API_KEY"] = config("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = config("LANGSMITH_TRACING")
os.environ["LANGSMITH_PROJECT"] = config("LANGSMITH_PROJECT")
os.environ["LANGSMITH_ENDPOINT"] = config("LANGSMITH_ENDPOINT")


OPENROUTER_API_KEY = config("OPENROUTER_API_KEY")


# llm = ChatOpenRouter(model="openai/gpt-5.4-mini")

embeddings = OpenAIEmbeddings(
    base_url="https://openrouter.ai/api/v1",
    model="openai/text-embedding-3-large",
    # With the `text-embedding-3` class
    # of models, you can specify the size
    # of the embeddings you want returned.
    # dimensions=1024
    api_key=OPENROUTER_API_KEY
)

# embeddings = ChatOpenRouter(model="openai/text-embedding-3-large")
vector_store = InMemoryVectorStore(embeddings)


# Below is a minimal helper for demonstration purposes.
def load_pdf_pages(file_path: str) -> list[Document]:
    reader = pypdf.PdfReader(file_path)
    return [
        Document(
            page_content=page.extract_text() or "",
            metadata={"source": file_path, "page": i},
        )
        for i, page in enumerate(reader.pages)
    ]


file_path = "nke-10k-2023.pdf"
docs = load_pdf_pages(file_path)
print(len(docs))


def chunking(loaded_documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
        )

    chunks = text_splitter.split_documents(loaded_documents)
    return chunks

chunks = chunking(loaded_documents=docs)


def indexing(chunks):
    ids = vector_store.add_documents(documents=chunks)
    return ids


print(len(indexing(chunks=chunks)))    


@traceable(name="Ask Question")
def ask_question(question):
    result = vector_store.similarity_search(question)
    return result[0]    


result1 = ask_question(question="How many distribution centers does Nike have in the US?")
print(result1)

@traceable(name="Ask Question With Score")
def ask_question_with_score(question):
    results = vector_store.similarity_search_with_score(question)
    doc, score = results[0]
    return doc, score
    

result2 = ask_question_with_score("What was Nike's revenue in 2023?")
doc, score = result2[0], result2[1]
print(doc)
print(score)


# result1 = ask_question(question="How many distribution centers does Nike have in the US?")
# print(result1[0])



# results = await vector_store.asimilarity_search("When was Nike incorporated?")

# print(results[0])

############################################################
# Return scores:
# Note that providers implement different scores; the score here
# is a distance metric that varies inversely with similarity.


# print(f"Score: {score}\n")
# print(doc)
###########################################################

# Return documents based on similarity to an embedded query:

embedding = embeddings.embed_query("How were Nike's margins impacted in 2023?")

results = vector_store.similarity_search_by_vector(embedding)
print(results[0])

###############################################################


@chain
def retriever(query: str) -> List[Document]:
    return vector_store.similarity_search(query, k=1)


retriever.batch(
    [
        "How many distribution centers does Nike have in the US?",
        "When was Nike incorporated?",
    ],
)

