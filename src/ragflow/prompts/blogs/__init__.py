from src.ragflow.prompts.blogs.blog_generation import (blog_generation_protocol, blog_generation_template, BlogGenerationParser)


from src.ragflow.prompts.web_copy.query import (
    generation_qa_with_reference_protocol, generation_qa_with_reference_template, GenerationQaParser
)
__all__ = [
        "blog_generation_protocol", "blog_generation_template", "BlogGenerationParser", "generation_qa_with_reference_protocol", "generation_qa_with_reference_template", "GenerationQaParser"
]