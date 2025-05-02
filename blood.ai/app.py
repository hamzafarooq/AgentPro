# import streamlit as st
# from PIL import Image
# import tensorflow as tf
# import google.generativeai as genai
# import numpy as np
# import os
# import time
# import requests
# from bs4 import BeautifulSoup
# import faiss  
# import pickle  
# import json  
# import logging
# from typing import Dict, Any, Tuple
# import sys
# import dotenv

# # Set up logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger('bloodcell_app')

# # Load environment variables
# dotenv.load_dotenv()

# # --- Page Configuration (MUST BE THE FIRST STREAMLIT COMMAND) ---
# st.set_page_config(
#     page_title="AI Chat & Blood Classifier",
#     layout="wide",
#     initial_sidebar_state="auto"
# )

# # --- AgentPro Import Attempt ---
# try:
#     # Try to import AgentPro
#     from AgentPro.agentpro import AgentPro
#     from AgentPro.agentpro.tools import AresInternetTool
    
#     # Initialize AgentPro for hospital search
#     tools = [AresInternetTool()]
#     agent = AgentPro(tools=tools)
#     logger.info("AgentPro initialized successfully with AresInternetTool")
#     hospital_search_available = True
# except ImportError:
#     try:
#         sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "AgentPro"))
#         from agentpro import AgentPro
#         from agentpro.tools import AresInternetTool
        
#         # Initialize AgentPro for hospital search
#         tools = [AresInternetTool()]
#         agent = AgentPro(tools=tools)
#         logger.info("AgentPro initialized successfully with AresInternetTool")
#         hospital_search_available = True
#     except ImportError:
#         logger.warning("Unable to import AgentPro. Hospital search functionality will be disabled.")
#         # Create placeholder empty classes so the rest of the code can run
#         class AgentProPlaceholder:
#             def __init__(self, *args, **kwargs):
#                 pass
#             def __call__(self, *args, **kwargs):
#                 return "AgentPro is not available. Please check your installation."
        
#         class AresInternetToolPlaceholder:
#             def __init__(self):
#                 self.name = "AresInternetTool"
#                 self.description = "A tool for searching the internet (currently unavailable)"
        
#         AgentPro = AgentProPlaceholder
#         AresInternetTool = AresInternetToolPlaceholder
#         agent = None
#         hospital_search_available = False
# except Exception as e:
#     logger.error(f"Error initializing AgentPro: {e}")
#     agent = None
#     hospital_search_available = False

# # --- Hospital Search Functionality ---
# # Constants for hospital search
# HOSPITAL_CACHE_DURATION = 86400  # 24 hours in seconds
# HOSPITAL_CACHE = {}  # In-memory cache: {(disease, location): (timestamp, results)}

# def search_hospitals(agent, disease: str, location: str, force_refresh: bool = False) -> str:
#     """
#     Search for hospitals that specialize in treating a specific blood disease in a given location.
    
#     Args:
#         agent: The AgentPro instance to use for search
#         disease: The blood disease or indicator (e.g., "NPM1", "PML_RARA")
#         location: The city/location to search in (e.g., "Lahore")
#         force_refresh: Whether to force a fresh search, ignoring cache
        
#     Returns:
#         str: A formatted response with hospital information
#     """
#     # Check cache first (if not forcing refresh)
#     cache_key = (disease, location)
#     if not force_refresh and cache_key in HOSPITAL_CACHE:
#         timestamp, results = HOSPITAL_CACHE[cache_key]
#         # If cache is still valid (less than CACHE_DURATION old)
#         if time.time() - timestamp < HOSPITAL_CACHE_DURATION:
#             logger.info(f"Using cached results for {disease} in {location}")
#             return results
    
#     try:
#         # Format the query for better results
#         if disease in ["NPM1", "PML_RARA", "RUNX1_RUNX1T1"]:
#             # For genetic markers, add context
#             query = (
#                 f"Find hospitals or medical centers in {location}, Pakistan that specialize in "
#                 f"hematology and can treat patients with {disease} genetic marker in blood disorders. "
#                 f"List the top 3 with their name, contact details, address, expertise, and available treatments. "
#                 f"Format the response with markdown headings and bullet points."
#             )
#         else:
#             # General query for other conditions
#             query = (
#                 f"Find hospitals or medical centers in {location}, Pakistan that specialize in "
#                 f"treating {disease}. List the top 3 with their name, contact details, address, "
#                 f"expertise, and available treatments. Format the response with markdown headings and bullet points."
#             )
        
#         logger.info(f"Searching for hospitals treating {disease} in {location}")
        
#         # Execute the search using AgentPro
#         response = agent(query)
        
#         # Process and format the response
#         formatted_response = _format_hospital_response(response, disease, location)
        
#         # Cache the result
#         HOSPITAL_CACHE[cache_key] = (time.time(), formatted_response)
        
#         return formatted_response
        
#     except Exception as e:
#         error_msg = f"Error searching for hospitals: {str(e)}"
#         logger.error(error_msg)
#         return f"⚠️ {error_msg}\n\nPlease try again later or contact support."

# def _format_hospital_response(response: str, disease: str, location: str) -> str:
#     """Format the hospital search response for better readability."""
#     # If response is empty or invalid
#     if not response or len(response.strip()) < 10:
#         return f"No specialized hospitals found for {disease} in {location}. Please consult with a general hematologist or oncologist for referrals."
    
#     # Add a header and disclaimer
#     formatted_response = f"""
# ## Hospitals Specializing in {disease} Treatment in {location}

# {response}

# ---

# **Disclaimer:** This information is provided for reference only. Please verify details directly with the hospitals 
# before making any decisions. Always consult with a qualified healthcare provider for medical advice.
# """
    
#     return formatted_response

# def get_disease_description(disease: str) -> str:
#     """Get a general description of the blood disease or genetic marker."""
#     descriptions = {
#         "NPM1": "NPM1 is a genetic mutation commonly found in acute myeloid leukemia (AML). "
#                 "It affects the nucleophosmin protein and is generally associated with a more "
#                 "favorable prognosis compared to some other genetic markers in AML.",
        
#         "PML_RARA": "PML-RARA is a fusion gene associated with acute promyelocytic leukemia (APL), "
#                    "a subtype of acute myeloid leukemia. This genetic abnormality is caused by a "
#                    "translocation between chromosomes 15 and 17, and is responsive to targeted therapies.",
        
#         "RUNX1_RUNX1T1": "RUNX1-RUNX1T1 (previously known as AML1-ETO) is a fusion gene resulting "
#                         "from a translocation between chromosomes 8 and 21. It is associated with a "
#                         "specific subtype of acute myeloid leukemia (AML) that generally has a favorable prognosis.",
        
#         "control": "This indicates a normal or control sample without detected genetic abnormalities "
#                  "associated with leukemia or other blood disorders."
#     }
    
#     return descriptions.get(disease, f"Information about {disease} is not available in the database.")

# # --- Configuration ---

# # Load Google API Key securely from Streamlit Secrets
# try:
#     api_key = st.secrets["GOOGLE_API_KEY"]
#     genai.configure(api_key=api_key)
#     GEMINI_MODEL_NAME = "gemini-1.5-flash"  # Or "gemini-pro", etc.
#     EMBEDDING_MODEL_NAME = "models/text-embedding-004"  # Google's text embedding model

# except KeyError:
#     st.error("❌ Google API Key not found. Please ensure it's in `.streamlit/secrets.toml` as GOOGLE_API_KEY='YourKey'.")
#     st.stop()
# except Exception as e:
#     st.error(f"❌ Error configuring Google AI SDK: {e}")
#     st.stop()

# # --- TensorFlow Model Loading ---

# @st.cache_resource  # Caching is crucial for performance
# def load_tf_model(model_path):
#     """Loads a TensorFlow/Keras model, handling potential errors."""
#     if not os.path.exists(model_path):
#         st.error(f"Model file not found at path: {model_path}")
#         return None
#     try:
#         return tf.keras.models.load_model(model_path)
#     except Exception as e:
#         st.error(f"Error loading TensorFlow model from {model_path}: {e}")
#         return None

# # Define model paths
# BLOOD_DISEASE_MODEL_PATH = 'blood_cells_model.h5'
# CELL_TYPE_MODEL_PATH = 'image_classification_model.h5'

# # Load the models
# blood_disease_model = load_tf_model(BLOOD_DISEASE_MODEL_PATH)
# cell_type_model = load_tf_model(CELL_TYPE_MODEL_PATH)

# # Define class names for prediction mapping
# # Class names for the "Blood Disease" model (Check this list carefully)
# disease_indicator_class_names = ["RUNX1_RUNX1T1", "control", "NPM1", "PML_RARA", "RUNX1_RUNX1T1"]
# # Class names for the "Blood Cell Type" model
# cell_type_class_names = ["ig", "lymphocyte", "monocyte", "neutrophil", "platelet"]

# # --- Gemini Embeddings and FAISS Setup ---

# # Paths for saving data
# DATA_FILE_PATH = 'data.txt'
# FAISS_INDEX_PATH = 'faiss_index.bin'
# FAISS_METADATA_PATH = 'faiss_metadata.pkl'
# EMBEDDING_DIMENSION = 768  # Default dimension for text-embedding-004, can be reduced

# # Initialize embedding model - no need to cache as we'll use the client directly
# embedding_model = None  # We'll use the genai module directly instead

# # Function to generate embeddings using Gemini
# def generate_gemini_embedding(text, dimension=None):
#     """Generate an embedding for a text using Google's Gemini embedding model."""
#     try:
#         # Configure embedding parameters
#         embed_config = {}
#         if dimension is not None and dimension > 0:
#             embed_config["output_dimensionality"] = dimension
            
#         # Generate embedding using the embedding model
#         result = genai.embed_content(
#             model=EMBEDDING_MODEL_NAME,
#             content=text,
#             task_type="RETRIEVAL_QUERY",  # For query embedding
#             **embed_config
#         )
        
#         # Return the embedding values as a numpy array
#         return np.array(result["embedding"], dtype=np.float32)
#     except Exception as e:
#         st.error(f"Error generating embedding: {e}")
#         return None

# # Function to load existing FAISS index if available
# def load_faiss_index():
#     """Load the FAISS index and metadata if they exist."""
#     if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(FAISS_METADATA_PATH):
#         try:
#             # Load the index
#             index = faiss.read_index(FAISS_INDEX_PATH)
            
#             # Load the metadata
#             with open(FAISS_METADATA_PATH, 'rb') as f:
#                 metadata = pickle.load(f)
                
#             return index, metadata
#         except Exception as e:
#             st.warning(f"Failed to load existing FAISS index: {e}. Will create a new one.")
#             return None, None
#     return None, None

# # Try to load existing index
# faiss_index, metadata = load_faiss_index()

# # Initialize if doesn't exist
# if faiss_index is None:
#     # Create a new index - configure with the correct dimension
#     faiss_index = faiss.IndexFlatL2(EMBEDDING_DIMENSION)
#     metadata = {
#         'texts': [],     # Original texts
#         'urls': [],      # Source URLs
#         'timestamps': [] # When added
#     }

# # --- Chatbot Context Data ---

# def load_knowledge_base():
#     """Load the knowledge base from the data.txt file."""
#     try:
#         with open(DATA_FILE_PATH, 'r', encoding='utf-8') as file:
#             return file.read()
#     except FileNotFoundError:
#         return "No additional context data found."

# data_details = load_knowledge_base()

# # System prompt for the chatbot
# SYSTEM_PROMPT = f"""You are an AI assistant specialized in providing information about blood cell types and blood diseases. Your purpose is to offer general knowledge and explanations based on established medical information.

# You can discuss:
# * Different types of blood cells (e.g., lymphocytes, monocytes, neutrophils, platelets, red blood cells) and their functions.
# * General information about common blood disorders, conditions, or indicators (e.g., anemia, leukemia, sickle cell disease, or specific genetic markers like NPM1 or PML-RARA mentioned in context).
# * Basic concepts related to blood types (e.g., ABO system, Rh factor - but not determine a user's type).
# * Definitions of related medical terms.

# Use the following specific details if relevant to the user's question and within your scope:
# ---
# {data_details}
# ---

# **IMPORTANT LIMITATIONS: You MUST strictly adhere to the following:**
# * **DO NOT provide medical diagnoses.** You cannot tell a user if they have a specific disease.
# * **DO NOT interpret personal medical data,** such as lab results or medical images.
# * **DO NOT offer medical advice,** treatment recommendations, or suggestions on managing health conditions.
# * **DO NOT act as a substitute for a qualified healthcare professional.** Your information is for general knowledge only.

# **If a user asks for a diagnosis, medical advice, interpretation of their personal results/images, or asks 'what disease do I have?', you MUST politely refuse.** State clearly that you are an informational AI assistant and cannot provide medical services. **Strongly advise the user to consult with a doctor or qualified healthcare provider** for any personal health concerns, diagnosis, or treatment.

# Keep your responses informative, factual, objective, and strictly within the boundaries of providing general educational information. Avoid speculation.
# """

# # --- Streamlit App Title ---
# st.title("🩸 AI Chatbot & Blood Classifier")

# # --- Chatbot Section ---
# st.header("💬 AI Chat Assistant")
# st.caption("Ask questions about blood cells and related diseases (general information only).")

# # Initialize chat history in session state
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display past chat messages
# chat_container = st.container()
# with chat_container:
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

# # Get user input using st.chat_input
# if prompt := st.chat_input("Your question..."):
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with chat_container:
#         with st.chat_message("user"):
#             st.markdown(prompt)

#     # Search FAISS index for relevant content if it contains data
#     if faiss_index.ntotal > 0:
#         try:
#             # Generate embedding for the user query using Gemini
#             query_embedding = generate_gemini_embedding(prompt, dimension=EMBEDDING_DIMENSION)
            
#             if query_embedding is not None:
#                 # Reshape to 2D array for faiss search
#                 query_embedding = query_embedding.reshape(1, -1)
                
#                 # Search the index (get top 3 most similar chunks)
#                 k = min(3, faiss_index.ntotal)
#                 distances, indices = faiss_index.search(query_embedding, k)
                
#                 # Get the relevant texts
#                 relevant_texts = [metadata['texts'][idx] for idx in indices[0]]
                
#                 # Add to context (only if there are relevant matches)
#                 if len(relevant_texts) > 0 and distances[0][0] < 20:  # Only include if distance is reasonable
#                     context_from_faiss = "\n\nRelevant information from knowledge base:\n" + "\n---\n".join(relevant_texts)
#                     full_prompt = SYSTEM_PROMPT + context_from_faiss + "\n\nUser: " + prompt + "\n\nAssistant:"
#                 else:
#                     full_prompt = SYSTEM_PROMPT + "\n\nUser: " + prompt + "\n\nAssistant:"
#             else:
#                 full_prompt = SYSTEM_PROMPT + "\n\nUser: " + prompt + "\n\nAssistant:"
                
#         except Exception as e:
#             st.warning(f"Error searching knowledge base: {e}")
#             full_prompt = SYSTEM_PROMPT + "\n\nUser: " + prompt + "\n\nAssistant:"
#     else:
#         full_prompt = SYSTEM_PROMPT + "\n\nUser: " + prompt + "\n\nAssistant:"

#     try:
#         with st.spinner("Thinking..."):
#             model = genai.GenerativeModel(GEMINI_MODEL_NAME)
#             response = model.generate_content(contents=[full_prompt])

#             if response.parts:
#                  assistant_response = response.text
#             elif not response.candidates:
#                  assistant_response = "Response may have been blocked due to safety settings or contains no content."
#                  try:
#                      with chat_container: st.warning(f"Feedback: {response.prompt_feedback}")
#                  except Exception: pass
#             else:
#                  assistant_response = "Received an unexpected response structure."
#                  with chat_container: st.warning(f"Unexpected response: {response}")
#     except Exception as e:
#         st.error(f"❌ Error generating content: {e}")
#         assistant_response = f"Sorry, an error occurred: {e}"

#     st.session_state.messages.append({"role": "assistant", "content": assistant_response})
#     st.rerun()

# # --- Image Classification Section ---
# st.divider()
# st.header("🔬 Blood Image Classifier")

# if blood_disease_model is None or cell_type_model is None:
#     st.error("One or more classification models failed to load. Cannot proceed.")
# else:
#     col1, col2 = st.columns([1, 2])
#     with col1:
#         option = st.selectbox(
#             "Choose classification mode:",
#             ("Blood Disease", "Blood Cell Type Classification"),
#             key="classification_type",
#             help="Blood Disease: Predicts disease indicators (e.g., NPM1). Cell Type: Predicts cell types (e.g., lymphocyte)."
#         )

#         # Add location selector for hospital search if Blood Disease is selected
#         if option == "Blood Disease":
#             location = st.selectbox(
#                 "Select location for hospital search:",
#                 ["Lahore", "Karachi", "Islamabad", "Multan", "Faisalabad", "Peshawar"],
#                 key="location_selector",
#                 help="Select your location to find nearby hospitals that specialize in the detected disease."
#             )
        
#         uploaded_file = st.file_uploader(
#             "Upload a blood cell image",
#             type=['png', 'jpg', 'jpeg', 'tiff'],
#             key="file_uploader"
#         )

#     def preprocess_and_predict(image, model, class_names, target_size=(64, 64)):
#         """Preprocess image and predict class."""
#         try:
#             img_resized = image.resize(target_size)
#             if img_resized.mode != 'RGB': img_resized = img_resized.convert('RGB')
#             img_array = np.array(img_resized) / 255.0
#             img_array = np.expand_dims(img_array, axis=0)
#             predictions = model.predict(img_array)
#             pred_index = np.argmax(predictions, axis=1)[0]
#             if pred_index < len(class_names):
#                 predicted_class = class_names[pred_index]
#             else:
#                 st.error(f"Pred index {pred_index} out of bounds (len {len(class_names)}).")
#                 return None, None
#             confidence = np.max(predictions) * 100
#             return predicted_class, confidence
#         except Exception as e:
#             st.error(f"Image processing/prediction error: {e}")
#             return None, None

#     with col2:
#         if uploaded_file is not None:
#             try:
#                 image = Image.open(uploaded_file)
#                 st.image(image, caption="Uploaded Image", use_column_width=True)
#                 predicted_class = None
#                 confidence = None
#                 with st.spinner("Analyzing image..."):
#                     if option == "Blood Disease":
#                         predicted_class, confidence = preprocess_and_predict(
#                             image, blood_disease_model, disease_indicator_class_names, target_size=(224, 224)
#                         )
#                     elif option == "Blood Cell Type Classification":
#                         predicted_class, confidence = preprocess_and_predict(
#                             image, cell_type_model, cell_type_class_names, target_size=(64, 64)
#                         )
#                 if predicted_class is not None and confidence is not None:
#                     if option == "Blood Disease":
#                         st.success(f"Predicted Disease Indicator: **{predicted_class}**")
                        
#                         # Display disease information
#                         disease_description = get_disease_description(predicted_class)
#                         st.info(f"**About this marker:** {disease_description}")
                        
#                         # Show hospital search section if Blood Disease was detected
#                         location = st.session_state.get("location_selector", "Lahore")
#                         with st.expander(f"Find hospitals for {predicted_class} in {location}", expanded=True):
#                             if st.button("Search for Specialized Hospitals"):
#                                 with st.spinner(f"Searching for hospitals that specialize in {predicted_class} in {location}..."):
#                                     if hospital_search_available and agent:
#                                         try:
#                                             response = search_hospitals(agent, predicted_class, location)
#                                             st.markdown("### Hospital Recommendations")
#                                             st.markdown(response)
#                                         except Exception as e:
#                                             st.error(f"Error searching for hospitals: {e}")
#                                     else:
#                                         st.warning("Hospital search is not available because AgentPro could not be initialized.")
#                     else:
#                         st.success(f"Predicted Cell Type: **{predicted_class}**")
                    
#                     st.metric(label="Confidence", value=f"{confidence:.2f}%")
#                 else:
#                     st.warning("Could not make a prediction.")
#             except Exception as e:
#                 st.error(f"Error handling uploaded image: {e}")
#         elif option:
#             placeholder = st.empty()
#             placeholder.info("Upload an image using the panel on the left.")

# # --- Web Scraping and Embedding Section ---
# st.divider()
# st.header("🌐 Web Content Extractor with FAISS Embedding")
# st.caption("Enter a URL to extract its main text content and save it to your knowledge base.")

# # Function to scrape data from a single URL
# def scrape_website_content(url):
#     """Attempts to scrape paragraphs and headings from a given URL."""
#     try:
#         # Add scheme if missing
#         if not url.startswith(('http://', 'https://')):
#             url = 'https://' + url
#         # Basic headers
#         headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
#         response = requests.get(url, headers=headers, timeout=10)
#         response.raise_for_status() # Check for HTTP errors
#         soup = BeautifulSoup(response.text, 'html.parser')
#         # Extract common text elements
#         paragraphs = soup.find_all('p')
#         headers = soup.find_all(['h1', 'h2', 'h3'])
#         # Combine and clean
#         content_parts = [h.get_text(strip=True) for h in headers if h.get_text(strip=True)]
#         content_parts.extend([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
#         content = '\n\n'.join(content_parts)
#         if not content: return "Could not find significant text content using p/h1/h2/h3 tags."
#         return content
#     except requests.exceptions.RequestException as e: return f"Error fetching URL {url}: {str(e)}"
#     except Exception as e: return f"Error processing {url}: {str(e)}"

# # Function to add scraped content to data.txt and create FAISS embeddings
# def save_to_knowledge_base(url, content):
#     """Save the content to data.txt and update FAISS embeddings using Gemini."""
#     # Don't process if content indicates an error
#     if content.startswith("Error") or content.startswith("Could not find"):
#         return False, content
    
#     # Save to data.txt (append mode)
#     try:
#         with open(DATA_FILE_PATH, 'a', encoding='utf-8') as file:
#             file.write(f"\n\n--- CONTENT FROM: {url} ---\n")
#             file.write(content)
#             file.write("\n--- END CONTENT ---\n")
#     except Exception as e:
#         return False, f"Error saving to data.txt: {e}"
    
#     # Create embeddings and add to FAISS index
#     try:
#         # Split content into manageable chunks (max ~500-1000 characters per chunk)
#         chunks = []
#         current_chunk = ""
#         for paragraph in content.split('\n\n'):
#             if len(current_chunk) + len(paragraph) < 1000:  # Rough character limit
#                 if current_chunk: current_chunk += "\n\n"
#                 current_chunk += paragraph
#             else:
#                 if current_chunk: 
#                     chunks.append(current_chunk)
#                 current_chunk = paragraph
#         if current_chunk:  # Add the last chunk
#             chunks.append(current_chunk)
        
#         # Create embeddings for each chunk
#         embedding_success_count = 0
#         for chunk in chunks:
#             # Generate embedding using Gemini
#             embedding = generate_gemini_embedding(chunk, dimension=EMBEDDING_DIMENSION)
            
#             if embedding is not None:
#                 # Add to FAISS index (reshape to 2D array)
#                 embedding = embedding.reshape(1, -1)
#                 faiss_index.add(embedding)
                
#                 # Add metadata
#                 metadata['texts'].append(chunk)
#                 metadata['urls'].append(url)
#                 metadata['timestamps'].append(time.time())
                
#                 embedding_success_count += 1
        
#         # Save the updated index and metadata
#         faiss.write_index(faiss_index, FAISS_INDEX_PATH)
#         with open(FAISS_METADATA_PATH, 'wb') as f:
#             pickle.dump(metadata, f)
            
#         return True, f"Successfully added {embedding_success_count} chunks to knowledge base with Gemini embeddings."
#     except Exception as e:
#         return False, f"Error creating embeddings: {e}"

# # UI for scraping
# user_url = st.text_input("Enter URL:", key="url_input", placeholder="e.g., https://www.example-health-info.com")
# col1, col2 = st.columns([1, 1])

# with col1:
#     if st.button("Extract & Save to Knowledge Base", key="scrape_save_button"):
#         if user_url:
#             with st.spinner(f"Extracting content from {user_url}..."):
#                 # 1. Scrape content
#                 scraped_content = scrape_website_content(user_url)
#                 st.text_area("Extracted Content:", scraped_content, height=200)
                
#                 # 2. Save to knowledge base and create embeddings
#                 if not scraped_content.startswith("Error") and not scraped_content.startswith("Could not find"):
#                     with st.spinner("Saving to knowledge base and creating embeddings with Gemini..."):
#                         success, message = save_to_knowledge_base(user_url, scraped_content)
#                         if success:
#                             st.success(message)
#                         else:
#                             st.error(message)
#         else:
#             st.warning("Please enter a URL first.")

# with col2:
#     if st.button("View Current Knowledge Base Stats", key="view_kb_stats"):
#         with st.spinner("Analyzing knowledge base..."):
#             # Show stats about the knowledge base
#             if os.path.exists(DATA_FILE_PATH):
#                 with open(DATA_FILE_PATH, 'r', encoding='utf-8') as file:
#                     content = file.read()
#                     total_chars = len(content)
#                     total_lines = content.count('\n') + 1
#                     urls_count = content.count('--- CONTENT FROM:')
                    
#                     st.info(f"""
#                     📚 **Knowledge Base Stats**
#                     - Total characters: {total_chars:,}
#                     - Total lines: {total_lines:,}
#                     - Sources: {urls_count} URLs
#                     """)
#             else:
#                 st.info("No knowledge base file found.")
            
#             # Show stats about FAISS index
#             if faiss_index.ntotal > 0:
#                 st.info(f"""
#                 🔍 **FAISS Index Stats**
#                 - Total embeddings: {faiss_index.ntotal:,}
#                 - Unique sources: {len(set(metadata['urls'])):,}
#                 - Embedding dimension: {faiss_index.d}
#                 - Embedding model: {EMBEDDING_MODEL_NAME}
#                 """)
#             else:
#                 st.info("FAISS index is empty.")

# st.caption("Note: Extraction success depends on website structure and permissions. Respect website terms.")

# # --- Display Model Summary Section ---
# st.divider()
# st.header("⚙️ TensorFlow Model Details")

# selected_option_for_summary = st.session_state.get("classification_type", "Blood Disease")
# with st.expander(f"Show TF Model Summary for '{selected_option_for_summary}'"):
#     model_to_show = None
#     if selected_option_for_summary == "Blood Disease": model_to_show = blood_disease_model
#     elif selected_option_for_summary == "Blood Cell Type Classification": model_to_show = cell_type_model
#     if model_to_show:
#          summary_lines = []
#          model_to_show.summary(print_fn=lambda x: summary_lines.append(x))
#          st.text('\n'.join(summary_lines))
#     else: st.warning("Selected classification model could not be loaded/found.")
import streamlit as st
from components.chatbot import render_chatbot
from components.classifier import render_classifier
from components.knowledge_base_ui import render_knowledge_base_ui
from components.model_summary import render_model_summary
from config import set_page_config

def main():
    # Set page configuration
    set_page_config()

    # App title
    st.title("🩸 AI Chatbot & Blood Classifier")

    # Render components
    render_chatbot()
    st.divider()
    render_classifier()
    st.divider()
    render_knowledge_base_ui()
    st.divider()
    render_model_summary()

if __name__ == "__main__":
    main()
    