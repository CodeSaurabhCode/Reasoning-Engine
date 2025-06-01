import os
from typing import List

import requests
from src.ragflow.utils.constants import EMBEDDINGS_URL, ZOOKEEPER_API_KEY


class EmbeddingsClient:
    def __init__(self, model_name: str) -> None:
        self.model_name: str = model_name
        self.url = EMBEDDINGS_URL
        return
    def embed_documents(self, messages: List[str]) -> List[List[float]]:
        payload = {
            "model": self.model_name,
            "input": messages,
        }
        api_key = os.getenv(ZOOKEEPER_API_KEY)

        headers = {
            "Content-Type": "application/json",
            "api-key": api_key
        }
        try:
            response = requests.post(self.url, json=payload, headers=headers, timeout=90)
            response.raise_for_status()  # Raise an exception for HTTP error responses (4xx, 5xx)
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
        if response.status_code == 200:
            response_dict = response.json()
            embeddings = [item["embedding"] for item in response_dict["data"]]
        else:
            print("Failed:", response.status_code, response.text)
        return embeddings
    
    def embed_query(self, message: str) -> List[float]:
        return self.embed_documents([message])[0]