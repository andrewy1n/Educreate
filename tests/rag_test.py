from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import WebBaseLoader
from langchain.chat_models import ChatOpenAI

loader = WebBaseLoader("https://nicegui.io/documentation")  # Change URL to actual docs
docs = loader.load()

# Step 2: Split text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
documents = text_splitter.split_documents(docs)

# Step 3: Store in Vector Database
vectorstore = FAISS.from_documents(documents, OpenAIEmbeddings())

# Step 4: Retrieve Relevant Docs & Generate Response
def get_latest_nicegui_info(query):
    docs = vectorstore.similarity_search(query, k=3)  # Retrieve top 3 relevant docs
    context = "\n\n".join([doc.page_content for doc in docs])
    
    llm = ChatOpenAI(model_name="gpt-4-turbo")  # Use an LLM with latest info
    response = llm.predict(f"Use the following documentation to answer the query:\n\n{context}\n\nQuery: {query}")
    
    return response

# Example Query
print(get_latest_nicegui_info("How do I create a button in NiceGUI?"))
