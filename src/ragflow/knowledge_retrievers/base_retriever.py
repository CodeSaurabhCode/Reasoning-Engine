from typing import List


class BaseRetriever:
    def __init__(self) -> None:
        pass
      
    def retrieve_contents_by_query(self, query: str, **kwargs) -> List[str]:
        return []

    def retrieve_contents(self, qa: str, **kwargs) -> List[str]:
        return self.retrieve_contents_by_query(qa, **kwargs)
