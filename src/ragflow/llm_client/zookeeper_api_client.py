import os
from typing import List

import requests
from src.ragflow.llm_client.base import BaseLLMClient
from src.ragflow.utils.constants import ZOOKEEPER_API_KEY, EMBEDDINGS_URL, GENERATE_URL, EMBEDDINGS_MODEL, GENERATIVE_MODEL

class ZooKeeperAIClient(BaseLLMClient):
    NAME = "ZooKeeperAIClient"

    def __init__(self,**kwargs) -> None:
        super().__init__(**kwargs)
        self._model_id: str = GENERATIVE_MODEL
        self._generate_url = GENERATE_URL
        self._embeddings_url = EMBEDDINGS_URL

    def _get_response_with_messages(self, messages: List[dict]) -> str:
        payload = {
            "model": self._model_id,
            "messages": messages,
            "stream": False,
            "temperature": 0
        }

        api_key = os.getenv(ZOOKEEPER_API_KEY)
        headers = {
            "api-key": api_key, 
            "Content-Type": "application/json"
        }

        response = requests.post(self._generate_url, json=payload, headers=headers, timeout=180)
        message_content = ""
        if response.status_code == 200:
            response_dict = response.json()
            print("Response:", response_dict)
            message_content = response_dict['choices'][0]['message']['content']
        else:
            print("Failed:", response.status_code, response.text)
            print('api_key:', api_key)
        return message_content