import requests
import langchain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain.schema import Document
import json
import time


embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
dummy_text = "This is a dummy text to initialize the vector store."
vectorstore = FAISS.from_texts([dummy_text], embeddings)

def get_response(prompt):
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {"model": "tinydolphin", "prompt": prompt}

    # Initial POST request to start the generation process
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code != 200:
        print("Error:", response.text)
        return "Failed to generate response."

    # Parse the concatenated JSON objects in the response
    try:
        lines = response.text.splitlines()  # Split response into individual JSON lines
        results = [json.loads(line) for line in lines]
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        return "Failed to parse server response."

    # Combine responses
    final_response = ''.join(result["response"] for result in results if "response" in result)

    return final_response

def process_input(text):
  if is_informative(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_text(text)
    docs = [Document(page_content=doc) for doc in docs]
    vectorstore.add_texts([doc.page_content for doc in docs], embeddings=[embeddings.embed_query(doc.page_content) for doc in docs])
    return "Got it! Storing it in my memory."
  else:
    docs = vectorstore.similarity_search(text, k=3)
    context = [doc.page_content for doc in docs]
    
    prompt = f"""You are an AI language model. Provide a response strictly based on the given context. If the question cannot be answered using the context, respond only with "I don't know."

    Context:
    {context}

    Question:
    {text}

    Answer:
    """
    
    response = get_response(prompt)
    return f"Assistant: {response}"

def is_informative(text):
  return text[-1]!='?'

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Assistant: Goodbye!")
        break
    response = process_input(user_input)
    print(f"Assistant: {response}")
