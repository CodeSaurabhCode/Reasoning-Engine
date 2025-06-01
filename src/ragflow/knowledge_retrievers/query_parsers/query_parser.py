from typing import List



def question_as_query(qa) -> List[str]:
    return [qa]


def meta_as_query(qa, meta_name: str) -> List[str]:
    meta_value = qa.metadata[meta_name]
    if isinstance(meta_value, list):
        return meta_value
    else:
        return [meta_value]


