from copy import deepcopy
import importlib
import os
import pathlib
from typing import Any, Callable, Optional

from dotenv import load_dotenv

from src.ragflow.prompts.protocol import CommunicationProtocol
from langchain_core.embeddings import Embeddings


def laod_dot_env(env_path: Optional[str] = None) -> None:
    if env_path is None:
        repo_path: str = pathlib.Path(os.path.abspath(__file__)).parent.parent.parent.parent
        env_path = os.path.join(repo_path, "env_configs\\.env")
    
    load_success: bool = load_dotenv(env_path)
    assert load_success is True, f"Failed to load .env file from {env_path}!"
    return

def load_constant(module_path: str, variable_name: str) -> Any:
    target_module = importlib.import_module(module_path)
    target = getattr(target_module, variable_name)
    return target

def load_protocol(module_path: str, protocol_name: str, partial_values: dict={}) -> CommunicationProtocol:
    protocol_module = importlib.import_module(module_path)
    protocol: CommunicationProtocol = deepcopy(getattr(protocol_module, protocol_name))
    protocol.template_partial(**partial_values)
    return protocol

def load_callable(module_path: str, name: str) -> Callable:
    return load_constant(module_path, name)

def load_class(module_path: str, class_name: str, base_class=None) -> object:
    loaded_class = load_constant(module_path, class_name)
    if base_class is not None:
        assert issubclass(loaded_class, base_class), (
            f"Class expected to be sub-class of {base_class.name()} but {loaded_class.name()} loaded."
        )
    return loaded_class

def load_embedding_func(**kwargs) -> Embeddings:
    embedding_class = load_callable("src.ragflow.llm_client", "EmbeddingsClient")
    if "model_name" not in kwargs or kwargs["model_name"] is None:
        kwargs["model_name"] = "text-embedding-3-large"
    embedding = embedding_class(**kwargs)
    return embedding