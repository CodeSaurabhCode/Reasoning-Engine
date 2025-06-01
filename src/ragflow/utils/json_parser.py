import json
from typing import Any


def parse_json(content: str) -> Any:
    if type(content)== dict: 
        return content
    content = content.replace("\n", " ")
    start_idx = content.find("{")
    end_idx = content.rfind("}") + 1
    content = content[start_idx:end_idx]
    parsed_content = json.loads(content)
    return recursive_parse(parsed_content)

def parse_json_v2(content: str) -> Any:
    content = content.replace("\n", " ")

    start_idx = content.rfind(': "')
    end_idx = content.rfind('"}')
    if start_idx >= 0 and end_idx >= 0:
        content = content[:start_idx] + ': "' + content[start_idx + len(': "') : end_idx].replace('"', "") + '"}'

    start_idx = content.find("{")
    end_idx = content.find("}")
    content = content[start_idx : end_idx + 1]
    return json.loads(content, strict=False)

def recursive_parse(data: Any) -> Any:
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = recursive_parse(value)
    elif isinstance(data, list):
        for i in range(len(data)):
            data[i] = recursive_parse(data[i])
    elif isinstance(data, str):
        try:
            potential_dict = json.loads(data)
            if isinstance(potential_dict, (dict, list)):
                return recursive_parse(potential_dict)  
        except json.JSONDecodeError:
            pass  
    return data