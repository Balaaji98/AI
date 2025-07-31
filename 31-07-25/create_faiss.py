from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

# Folder where your WMS .txt files are stored
knowledge_base_folder = "kb"  # Change if different

# Load documents
docs = []
for filename in os.listdir(knowledge_base_folder):
    if filename.endswith(".txt"):
        loader = TextLoader(os.path.join(knowledge_base_folder, filename))
        docs.extend(loader.load())

# Split text
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
split_docs = splitter.split_documents(docs)

# Embed and store
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(split_docs, embedding_model)

# Save vector index
vectorstore.save_local("faiss_index")
print("✅ FAISS index saved successfully.")
