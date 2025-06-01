from typing import Dict, Tuple

from src.ragflow.prompts import BaseContentParser, CommunicationProtocol, MessageTemplate
from src.ragflow.utils.json_parser import parse_json, parse_json_v2


filtering_template = MessageTemplate(
    template = [
    ("system", "You are a highly capable AI assistant skilled at analyzing, filtering, and structuring content."),
    ("user", """
**Input:**  
You will receive a string of raw parsed text content. This content may include title for the points, purposes, guidlines, and importance for that subsection.  
# Task
Your task is to extract key points, their purpose, importance, and guidelines from the given content.  

# Output format
Your output must strictly follow the format below. Ensure the output is JSON parsable in Python.  
{{
    "points": [
        {{
            "point": "<whatever is the title of that point>",
            "purpose": "<Purpose of this point if not mentioned then return empty string>",
            "guidelines": "<Get the guidlines that are there if not mentioned then return empty string>"
            "importance": "<if importance is there what is the importance for that section if not available then return empty string>",
        }},
        ...
    ]
}}

# Content
{content}
""".strip()),
    ],
    input_variables=["content"],
)

class FilteringParser(BaseContentParser):
    def encode(self, content: str, **kwargs) -> Tuple[str, dict]:
        return content, {}

    def decode(self, content: str, **kwargs) -> Dict[str, str]:
        try:
            output = parse_json(content)
        except Exception as e:
            print(f"[WebCopyParser] Content: {content}\nException: {e}")
            try:
                output = parse_json_v2(content)
            except Exception as e2:
                print(f"  [WebCopyParser] Exception: {e2}")
                return {
                    "header": "",
                    "purpose": "",
                    "guidlines": "",
                    "content": content,
                }
        for key, value in output.items():
            output[key] = str(value)
        return output

filtering_protocol = CommunicationProtocol(
    template=filtering_template,
    parser=FilteringParser(),
)