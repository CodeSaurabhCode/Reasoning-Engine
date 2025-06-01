import os
from pathlib import Path
from typing import List, Tuple

def list_files_recursively(directory: str, extensions: List[str]=None) -> List[Tuple[str, str]]:
    name_path_list: List[Tuple[str, str]] = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if extensions is None or Path(filename).suffix[1:] in extensions:
                name_path_list.append((filename, os.path.join(root, filename)))
    return name_path_list
