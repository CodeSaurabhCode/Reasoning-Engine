from typing import Dict, Tuple
from src.ragflow.prompts import CommunicationProtocol, BaseContentParser, MessageTemplate
from src.ragflow.utils.json_parser import parse_json_v2, parse_json

blog_generation_template = MessageTemplate(
        template = [
    (
        "system", 
        "You are an expert blog writer with a strong command over crafting SEO-optimized, engaging, and contextually rich long-form content. Generate blog which is having word count more than 1000 words"
    ),
    (
        "user", 
        '''Your task is to generate a comprehensive blog post based strictly on the provided query and raw context. The blog should be highly engaging, focused, and must contain **at least 1000 words** (more is acceptable, but never less).

        ## Objective:
        Create a detailed and captivating blog that adheres strictly to the provided context and user query. The content should:
        - Be engaging and maintain the reader's attention throughout.
        - Stay entirely within the scope of the input context, with **no unrelated or hallucinated information**.
        - Be SEO-friendly and valuable for readers.
        - Be structured clearly for readability and flow.

        ## Input:
        - **Content topic**: '{content}'
        - **User query/context**: 
        {query}
        ## Output format:

        The blog should be printed as one continuous output, *without* explicitly labeling sections like "title", "introduction", "main body", or "conclusion" should contain data related to query and content passed.

        The structure should still be followed, but it should flow like a natural blog post.

        Use **bold** formatting for:
        - Headlines
        - Subheadings
        - Any keywords or phrases that should stand out

        Do not use any of the following words in the output:
        - "Title"
        - "Introductory paragraph"
        - "Main body"
        - "Conclusion"
        - Any structural labeling

        Please ensure the generated blog exceeds **1000 words** in total length, and follows the structure outlined above — just without labeling it.

        Let's craft a high-impact blog post based on this!
        '''.strip()),
        ],
input_variables=["content","query"],
)

class BlogGenerationParser(BaseContentParser):
        def encode(self, content:str, references: Dict[str,str]={}, **Kwargs)-> Tuple[str,dict]:
                
                return content,{
                        "query": references
                }
        def decode(self, content: str, **Kwargs) -> Dict[str,str]:
                try:
                        output = parse_json(content)
                except Exception as e:
                        print(f"content: {content}, \n Exception as {e}")
                        try:
                                output = parse_json_v2(content)
                        except Exception as e2:
                                print(f"Exception arises as {e2}")
                                return {
                                        "title": "parsing error",
                                        "headlines" :"parsing error",
                                        "subheadlines": "parsing error",
                                        "conclusion": "parsing error"
                                }
                for key, value in output.items():
                        output[key] = str(value)
                return output
        
blog_generation_protocol = CommunicationProtocol(
        template = blog_generation_template,
        parser = BlogGenerationParser()
)