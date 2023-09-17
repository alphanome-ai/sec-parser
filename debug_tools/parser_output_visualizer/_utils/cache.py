from __future__ import annotations

import hashlib
import json
import os
import pickle
import re
from functools import wraps
from typing import Any, Callable, Dict


def _generate_filename(selected_kwargs: Dict[str, Any], args_hash: str) -> str:
    str_elements = [
        v
        for key, value in selected_kwargs.items()
        if isinstance(value, str) and len(v := re.sub(r"[^a-zA-Z0-9]+", "", value)) < 10
    ] + [
        f"{key}={'-'.join(str(v) for v in value)}"
        for key, value in selected_kwargs.items()
        if isinstance(value, list) and value
    ]
    prefix = "_".join(str_elements)
    return f"{prefix}_{args_hash}.pkl" if prefix else f"{args_hash}.pkl"


def cache_to_file(cache_by_keys: set[str], cache_dir: str) -> Callable:
    def actual_decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create a hash of the selected arguments
            if cache_by_keys:
                selected_kwargs = {k: kwargs[k] for k in cache_by_keys if k in kwargs}
            else:
                selected_kwargs = kwargs
            selected_kwargs = {
                k: selected_kwargs[k]
                for k in sorted(selected_kwargs)
                if selected_kwargs[k]
            }
            args_hash = hashlib.md5(str(selected_kwargs).encode()).hexdigest()[:10]

            cache_dir_ = os.path.join(os.path.dirname(__file__), cache_dir)
            os.makedirs(cache_dir_, exist_ok=True)

            cache_file_name = _generate_filename(selected_kwargs, args_hash)
            cache_file_path = os.path.join(cache_dir_, cache_file_name)

            if os.path.exists(cache_file_path):
                with open(cache_file_path, "rb") as f:
                    result = pickle.load(f)
                    if isinstance(result, str) and not os.path.exists(
                        cache_file_path.replace(".pkl", ".txt")
                    ):
                        with open(cache_file_path.replace(".pkl", ".txt"), "w") as f:
                            f.write(func(*args, **kwargs))
                    if isinstance(result, dict) and not os.path.exists(
                        cache_file_path.replace(".pkl", ".json")
                    ):
                        with open(cache_file_path.replace(".pkl", ".json"), "w") as f:
                            json.dump(result, f, indent=4)
                    return result

            result = func(*args, **kwargs)
            if isinstance(result, str):
                with open(cache_file_path.replace(".pkl", ".txt"), "w") as f:
                    f.write(result)
            if isinstance(result, dict):
                with open(cache_file_path.replace(".pkl", ".json"), "w") as f:
                    json.dump(result, f, indent=4)
            with open(cache_file_path, "wb") as f:
                pickle.dump(result, f)

            return result

        return wrapper

    return actual_decorator
