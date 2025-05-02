import streamlit as st
import os
from config import DATA_FILE_PATH
from utils.knowledge_base import scrape_website_content, save_to_knowledge_base, load_embeddings

def render_knowledge_base_ui():
    st.header("🌐 Web Content Extractor with Gemini Embedding")
    st.caption("Enter a URL to extract its main text content and save it to your knowledge base.")
    
    user_url = st.text_input("Enter URL:", key="url_input", placeholder="e.g., https://www.example-health-info.com")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Extract & Save to Knowledge Base", key="scrape_save_button"):
            if user_url:
                with st.spinner(f"Extracting content from {user_url}..."):
                    scraped_content = scrape_website_content(user_url)
                    st.text_area("Extracted Content:", scraped_content, height=200)
                    if not scraped_content.startswith("Error") and not scraped_content.startswith("Could not find"):
                        with st.spinner("Saving to knowledge base and creating embeddings with Gemini..."):
                            success, message = save_to_knowledge_base(user_url, scraped_content)
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
            else:
                st.warning("Please enter a URL first.")
    
    with col2:
        if st.button("View Current Knowledge Base Stats", key="view_kb_stats"):
            with st.spinner("Analyzing knowledge base..."):
                if os.path.exists(DATA_FILE_PATH):
                    with open(DATA_FILE_PATH, 'r', encoding='utf-8') as file:
                        content = file.read()
                        total_chars = len(content)
                        total_lines = content.count('\n') + 1
                        urls_count = content.count('--- CONTENT FROM:')
                        st.info(f"""
                        📚 **Knowledge Base Stats**
                        - Total characters: {total_chars:,}
                        - Total lines: {total_lines:,}
                        - Sources: {urls_count} URLs
                        """)
                else:
                    st.info("No knowledge base file found.")
                
                embeddings = load_embeddings()
                if embeddings:
                    unique_urls = len(set(e['url'] for e in embeddings))
                    total_chunks = len(embeddings)
                    st.info(f"""
                    🔍 **Embedding Stats**
                    - Total embedded chunks: {total_chunks:,}
                    - Unique sources: {unique_urls:,}
                    - Embedding model: models/text-embedding-004
                    """)
                else:
                    st.info("No embeddings found.")
    
    st.caption("Note: Extraction success depends on website structure and permissions. Respect website terms.")