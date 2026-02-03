import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


FAISS_PATH = os.path.join(BASE_DIR, "data", "faiss_index")
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FAISS_PATH, exist_ok=True)

CHUNK_SIZE = 25000
CHUNK_OVERLAP = 200
TOP_K = 15
TEMPERATURE = 0.25
MAX_PAGES = 500        
MAX_FILE_SIZE_MB = 50 
SIMILARITY_THRESHOLD = 0.6
