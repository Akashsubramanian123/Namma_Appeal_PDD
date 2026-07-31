import os
from supabase import create_client
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import pdfplumber
# 1. Configuration
SUPABASE_URL = "https://tstxwzcgtkdhbxeygtvw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRzdHh3emNndGtkaGJ4ZXlndHZ3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQyMDg1OCwiZXhwIjoyMDkxOTk2ODU4fQ.CYq8uvhdGy25pIu0Ma0xmNJWNLUBDCKy2h4uHAalwrw" # Double check this is the SERVICE_ROLE key, not the anon key
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Use the model
model = SentenceTransformer('all-mpnet-base-v2') 

# 2. Correct File Path
pdf_path = os.path.join("backend_tools", "rti_act_2005.pdf")

try:
    full_text = ""
    # Open the PDF with pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    if not full_text.strip():
        print("--- ERROR: No text could be extracted from the PDF. ---")
        exit()
    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(full_text)
    
    print(f"Total chunks created: {len(chunks)}")

    # 3. Embed and Upload with error tracking
    for i, chunk in enumerate(chunks):
        vector = model.encode(chunk).tolist()
        
        data = {
            "content": chunk,
            "embedding": vector,
            "metadata": {"source": "RTI Act 2005", "chunk_index": i}
        }
        
        # We use .execute() and capture the response
        response = supabase.table("rti_laws").insert(data).execute()
        
        if i % 10 == 0:
            print(f"Uploaded {i} chunks...")

    print("--- SUCCESS: Check Supabase again! ---")

except Exception as e:
    print(f"--- ERROR OCCURRED: {e} ---")