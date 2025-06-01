from src.ragflow.prompts.glossary.glossary_generation import (glossary_genParser, glossary_generation_protocol, glossary_template, glossary_chat_parser, glossary_chat_protocol, glossary_chat_template)
from src.ragflow.prompts.glossary.glossary_tagger import (glossaryContentParser, glossary_tagging_template, glossary_tagging_protocol)
from src.ragflow.prompts.web_copy.query import (
        generation_qa_with_reference_protocol, generation_qa_with_reference_template, GenerationQaParser
)

__all__ = [
        "glossary_genParser","glossary_generation_protocol","glossary_template","generation_qa_with_reference_protocol","generation_qa_with_reference_template","GenerationQaParser","glossaryContentParser","glossary_tagging_template","glossary_tagging_protocol","glossary_chat_template","glossary_chat_protocol","glossary_chat_parser"
]