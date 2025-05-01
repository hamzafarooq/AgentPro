import os
import requests

class MistralClient:
    API_KEY = os.getenv("MISTRAL_API_KEY")
    API_URL = "https://api.mistral.ai/v1/chat/completions"
    
    @classmethod
    def query(cls, prompt: str, temperature: float = 0.6, model: str = "codestral-latest") -> str:
        """
        Send a query to Mistral API and return the response
        
        Args:
            prompt: The prompt to send to Mistral
            temperature: The temperature parameter for response generation
            model: The model to use for generation
            
        Returns:
            str: The generated response or error message
        """
        headers = {
            "Authorization": f"Bearer {cls.API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }

        try:
            response = requests.post(cls.API_URL, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            return f"Mistral API Error: {response.status_code}"
        except Exception as e:
            return f"Error querying Mistral: {str(e)}"
