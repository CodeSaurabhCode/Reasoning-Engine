from src.ragflow.prompts.web_copy.generation import (
    web_copy_protocol, web_copy_template, WebCopyParser
)
from src.ragflow.prompts.web_copy.filtering import (
    filtering_protocol, filtering_template, FilteringParser
)
from src.ragflow.prompts.web_copy.query import (
    generation_qa_with_reference_protocol, generation_qa_with_reference_template, GenerationQaParser
)

__all__ = [
    "web_copy_protocol", "web_copy_template", "WebCopyParser", "filtering_protocol", "filtering_template", "FilteringParser",
    "generation_qa_with_reference_protocol", "generation_qa_with_reference_template", "GenerationQaParser",
]