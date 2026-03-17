import os
from functools import wraps
from typing import Any, Callable


def require_api_key(key: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            api_key = kwargs.get(key.lower())
            if not api_key:
                api_key = os.environ.get(key.upper())
            if not api_key:
                raise ValueError(
                    f"API key '{key}' not provided in kwargs or environment variable '{key.upper()}'"
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator
