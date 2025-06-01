from dataclasses import dataclass
from typing import Any, Dict, List

from src.ragflow.prompts.base_parser import BaseContentParser
from src.ragflow.prompts.message_template import MessageTemplate


@dataclass
class CommunicationProtocol:
    template: MessageTemplate
    parser: BaseContentParser

    def template_partial(self, **kwargs) -> List[str]:
        self.template = self.template.partial(**kwargs)
        return self.template.input_variables
    
    def process_input(self, content: str, **kwargs) -> List[Dict[str, str]]:
        encoded_content, encoded_dict = self.parser.encode(content, **kwargs)
        return self.template.format(content = encoded_content, **kwargs, **encoded_dict)
    
    def parse_output(self, content: str, **kwargs) -> Any:
        return self.parser.decode(content, **kwargs)