from abc import abstractmethod
from datetime import datetime
import time
from typing import Any, List


class BaseLLMClient(object):
    NAME = "BaseLLMClient"
    
    def __init__(self, **kwargs) -> None:
        pass
    
    def generate_content_with_messages(self, messages: List[dict]) -> str:
        start_time = time.time()

        response = self._get_response_with_messages(messages)

        time_used = time.time() - start_time

        return response

    @abstractmethod
    def _get_response_with_messages(self, messages: List[dict]) -> Any:
        raise NotImplementedError
