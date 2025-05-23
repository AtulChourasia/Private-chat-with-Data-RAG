import os
import torch
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.llms import HuggingFaceHub
from dotenv import load_dotenv

load_dotenv()

# Check for GPU availability and set the appropriate device for computation.
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

# Global variables
conversation_retrieval_chain = None
chat_history = []
llm_hub = None
embeddings = None

# Function to initialize the language model and its embeddings
import os

def init_llm():
    global llm_hub, embeddings

    model_id = "tiiuae/falcon-7b-instruct"
    

    llm_hub = HuggingFaceHub(
        repo_id=model_id,
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
        model_kwargs={"temperature": 0.1, "max_new_tokens": 600, "max_length": 600}
    )

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": DEVICE}
    )



# Function to process a PDF document
def process_document(document_path):
    global conversation_retrieval_chain
    init_llm()

    # Load the document
    loader = PyPDFLoader(document_path)
    documents = loader.load()
    
    # Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
    texts = text_splitter.split_documents(documents)
    
    # Create an embeddings database using Chroma from the split text chunks.
    # Create an embeddings database using Chroma from the split text chunks.
    # db = Chroma.from_documents(texts, embedding_function=embeddings)
    db = Chroma.from_documents(texts, embeddings)




    # --> Build the QA chain, which utilizes the LLM and retriever for answering questions. 
    # By default, the vectorstore retriever uses similarity search. 
    # If the underlying vectorstore support maximum marginal relevance search, you can specify that as the search type (search_type="mmr").
    # You can also specify search kwargs like k to use when doing retrieval. k represent how many search results send to llm
    conversation_retrieval_chain = RetrievalQA.from_chain_type(
        llm=llm_hub,
        chain_type="stuff",
        retriever=db.as_retriever(search_type="mmr", search_kwargs={'k': 6, 'lambda_mult': 0.25}),
        return_source_documents=False,
        input_key = "question"
     #   chain_type_kwargs={"prompt": prompt} # if you are using prompt template, you need to uncomment this part
    )


# Function to process a user prompt
def process_prompt(prompt):
    global conversation_retrieval_chain
    global chat_history
    
    # Query the model
    output = conversation_retrieval_chain({"question": prompt, "chat_history": chat_history})
    answer = output["result"]
    
    # Update the chat history
    chat_history.append((prompt, answer))
    
# Return the model's response
    return answer
