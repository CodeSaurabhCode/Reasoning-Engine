from __future__ import annotations
from string import Formatter
from typing import Dict, List, Tuple, Union, Callable
from pydantic import BaseModel, model_validator

formatter = Formatter()

class MessageTemplate(BaseModel):

    template: List[Tuple[str, str]]

    input_variables: List[str] = None

    partial_variables: Dict[str, Union[str, Callable[[], str]]] = {}

    @model_validator(mode="after")
    def validate_input_variables(self) -> MessageTemplate:
        input_variables_in_template = sorted(
            {
                field_name
                for _, content_template in self.template
                for _, field_name, _, _ in formatter.parse(content_template)
                if field_name is not None
            }
        )

        if self.input_variables is None:
            self.input_variables = list(input_variables_in_template)

        else:
            input_variable_set = set(self.input_variables)
            partial_variable_set = set(self.partial_variables.keys())
            parsed_variable_set = set(input_variables_in_template)
            for variable in parsed_variable_set:
                assert variable in input_variable_set or variable in partial_variable_set, (
                    f"{variable} in template but not shown in input variables list!"
                )
            for variable in input_variable_set:
                assert variable in parsed_variable_set, (
                    f"{variable} in input variable list but cannot found in template!"
                )

        return self

    def partial(self, **kwargs: Union[str, Callable[[], str]]) -> MessageTemplate:
        prompt_dict = self.__dict__.copy()
        prompt_dict["input_variables"] = list(set(self.input_variables).difference(kwargs))
        prompt_dict["partial_variables"] = {**self.partial_variables, **kwargs}
        return type(self)(**prompt_dict)

    def _merge_partial_and_user_variables(self, **kwargs: Union[str, Callable[[], str]]) -> Dict[str, str]:
        partial_kwargs = {
            k: v if isinstance(v, str) else v()
            for k, v in self.partial_variables.items()
        }
        return {**partial_kwargs, **kwargs}

    def format(self, **kwargs) -> List[Dict[str, str]]:
        kwargs = self._merge_partial_and_user_variables(**kwargs)
        result: List[Dict[str, str]] = [
            {
                "role": role,
                "content": formatter.format(content, **kwargs),
            }
            for role, content in self.template
        ]
        return result
