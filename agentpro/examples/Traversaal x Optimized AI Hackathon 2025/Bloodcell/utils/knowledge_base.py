import requests
from bs4 import BeautifulSoup
import pickle
import time
import streamlit as st
from config import DATA_FILE_PATH, EMBEDDING_DIMENSION
from models.gemini_client import generate_gemini_embedding
import os 

def scrape_website_content(url: str) -> str:
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        headers = soup.find_all(['h1', 'h2', 'h3'])
        content_parts = [h.get_text(strip=True) for h in headers if h.get_text(strip=True)]
        content_parts.extend([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        content = '\n\n'.join(content_parts)
        if not content:
            return "Could not find significant text content using p/h1/h2/h3 tags."
        return content
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL {url}: {str(e)}"
    except Exception as e:
        return f"Error processing {url}: {str(e)}"

def save_to_knowledge_base(url: str, content: str) -> tuple:
    if content.startswith("Error") or content.startswith("Could not find"):
        return False, content
    
    try:
        with open(DATA_FILE_PATH, 'a', encoding='utf-8') as file:
            file.write(f"\n\n--- CONTENT FROM: {url} ---\n")
            file.write(content)
            file.write("\n--- END CONTENT ---\n")
    except Exception as e:
        return False, f"Error saving to data.txt: {e}"
    
    try:
        chunks = []
        current_chunk = ""
        for paragraph in content.split('\n\n'):
            if len(current_chunk) + len(paragraph) < 1000:
                if current_chunk:
                    current_chunk += "\n\n"
                current_chunk += paragraph
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = paragraph
        if current_chunk:
            chunks.append(current_chunk)
        
        embeddings = []
        embedding_success_count = 0
        for chunk in chunks:
            embedding = generate_gemini_embedding(chunk, dimension=EMBEDDING_DIMENSION)
            if embedding is not None:
                embeddings.append({
                    'text': chunk,
                    'embedding': embedding,
                    'url': url,
                    'timestamp': time.time()
                })
                embedding_success_count += 1
        
        # Save embeddings to a pickle file
        embedding_file = 'embeddings.pkl'
        existing_embeddings = []
        if os.path.exists(embedding_file):
            with open(embedding_file, 'rb') as f:
                existing_embeddings = pickle.load(f)
        existing_embeddings.extend(embeddings)
        with open(embedding_file, 'wb') as f:
            pickle.dump(existing_embeddings, f)
            
        return True, f"Successfully added {embedding_success_count} chunks to knowledge base with Gemini embeddings."
    except Exception as e:
        return False, f"Error creating embeddings: {e}"

def load_knowledge_base():
    try:
        with open(DATA_FILE_PATH, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "No additional context data found."

def load_embeddings():
    embedding_file = 'embeddings.pkl'
    if os.path.exists(embedding_file):
        try:
            with open(embedding_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            st.warning(f"Failed to load embeddings: {e}")
            return []
    return []