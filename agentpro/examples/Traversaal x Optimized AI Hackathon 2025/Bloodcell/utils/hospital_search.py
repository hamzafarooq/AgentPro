import time
from config import HOSPITAL_CACHE_DURATION
from utils.logging_setup import logger

# In-memory cache
HOSPITAL_CACHE = {}

def search_hospitals(agent, disease: str, location: str, force_refresh: bool = False) -> str:
    cache_key = (disease, location)
    if not force_refresh and cache_key in HOSPITAL_CACHE:
        timestamp, results = HOSPITAL_CACHE[cache_key]
        if time.time() - timestamp < HOSPITAL_CACHE_DURATION:
            logger.info(f"Using cached results for {disease} in {location}")
            return results
    
    try:
        query = (
            f"Find hospitals or medical centers in {location}, Pakistan that specialize in "
            f"{'hematology and can treat patients with ' + disease + ' genetic marker in blood disorders' if disease in ['NPM1', 'PML_RARA', 'RUNX1_RUNX1T1'] else 'treating ' + disease}. "
            f"List the top 3 with their name, contact details, address, expertise, and available treatments. "
            f"Format the response with markdown headings and bullet points."
        )
        
        logger.info(f"Searching for hospitals treating {disease} in {location}")
        response = agent(query)
        formatted_response = _format_hospital_response(response, disease, location)
        
        HOSPITAL_CACHE[cache_key] = (time.time(), formatted_response)
        return formatted_response
        
    except Exception as e:
        error_msg = f"Error searching for hospitals: {str(e)}"
        logger.error(error_msg)
        return f"⚠️ {error_msg}\n\nPlease try again later or contact support."

def _format_hospital_response(response: str, disease: str, location: str) -> str:
    if not response or len(response.strip()) < 10:
        return f"No specialized hospitals found for {disease} in {location}. Please consult with a general hematologist or oncologist for referrals."
    
    return f"""
## Hospitals Specializing in {disease} Treatment in {location}

{response}

---

**Disclaimer:** This information is provided for reference only. Please verify details directly with the hospitals 
before making any decisions. Always consult with a qualified healthcare provider for medical advice.
"""

def get_disease_description(disease: str) -> str:
    descriptions = {
        "NPM1": "NPM1 is a genetic mutation commonly found in acute myeloid leukemia (AML). "
                "It affects the nucleophosmin protein and is generally associated with a more "
                "favorable prognosis compared to some other genetic markers in AML.",
        "PML_RARA": "PML-RARA is a fusion gene associated with acute promyelocytic leukemia (APL), "
                   "a subtype of acute myeloid leukemia. This genetic abnormality is caused by a "
                   "translocation between chromosomes 15 and 17, and is responsive to targeted therapies.",
        "RUNX1_RUNX1T1": "RUNX1-RUNX1T1 (previously known as AML1-ETO) is a fusion gene resulting "
                        "from a translocation between chromosomes 8 and 21. It is associated with a "
                        "specific subtype of acute myeloid leukemia (AML) that generally has a favorable prognosis.",
        "control": "This indicates a normal or control sample without detected genetic abnormalities "
                 "associated with leukemia or other blood disorders."
    }
    return descriptions.get(disease, f"Information about {disease} is not available in the database.")