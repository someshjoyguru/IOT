import os
import warnings
import requests
import json
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Suppress warnings from langchain and other libraries
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Path for storing the FAISS index
FAISS_INDEX_PATH = "vectorstore.faiss"
FAISS_CONFIG_PATH = "vectorstore.pkl"

# Load or initialize the FAISS vector store
def load_vectorstore():
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(FAISS_CONFIG_PATH):
        return FAISS.load_local(FAISS_INDEX_PATH, embeddings)
    else:
        # Create a new vector store if no saved store exists
        dummy_text = "This is a dummy text to initialize the vector store."
        return FAISS.from_texts([dummy_text], embeddings)

# Save the vector store to disk
def save_vectorstore(vectorstore):
    vectorstore.save_local(FAISS_INDEX_PATH)

# Initialize the vectorstore
vectorstore = load_vectorstore()

# Function to interact with the LLM server
def get_response(prompt):
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {"model": "tinydolphin", "prompt": prompt}

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code != 200:
        print("Error:", response.text)
        return "Failed to generate response."

    try:
        lines = response.text.splitlines()
        results = [json.loads(line) for line in lines if line.strip()]
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}, Response: {response.text}")
        return "Failed to parse server response."

    return ''.join(result["response"] for result in results if "response" in result)

# Determine if the input is informative or a question
def is_informative(text):
    return not text.strip().endswith('?')

# Process user input
def process_input(text):
    global vectorstore  # Access global vectorstore
    if text.strip().lower() == "dolphin forget everything":
        # Clear the vector store
        vectorstore = FAISS.from_texts(["This is a dummy text to initialize the vector store."], embeddings)
        save_vectorstore(vectorstore)
        return "Memory cleared. I have forgotten everything."
    elif is_informative(text):
        # Store data in memory
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_text(text)
        docs = [Document(page_content=doc) for doc in docs]
        vectorstore.add_texts(
            [doc.page_content for doc in docs], 
            embeddings=[embeddings.embed_query(doc.page_content) for doc in docs]
        )
        save_vectorstore(vectorstore)  # Save updated vector store
        return "Got it! Storing it in my memory."
    else:
        # Retrieve relevant data and generate response
        docs = vectorstore.similarity_search(text, k=3)
        context = "\n".join(doc.page_content for doc in docs)

        prompt = f"""
        You are an AI language model. Provide a response strictly based on the given context.

        Context:
        {context}

        Question:
        {text}

        Answer:
        """
        # print(prompt)
        return get_response(prompt)

# Main loop
if __name__ == "__main__":
    print("Assistant: Hello! How can I help you? (Type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Assistant: Goodbye!")
            break
        response = process_input(user_input)
        print(f"Assistant: {response}")
