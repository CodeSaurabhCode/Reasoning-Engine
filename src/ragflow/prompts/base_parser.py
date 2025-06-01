from typing import Any, Tuple

class BaseContentParser:
    def __init__(self) -> None:
        pass

    def encode(self, content: str, **kwargs) -> Tuple[str, dict]:
        return content, {}

    def decode(self, content: str, **kwargs) -> Any:
        return content
