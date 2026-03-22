# Copyright 2024 HDAnzz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from functools import wraps
from typing import Any, Callable


def require_api_key(key: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    装饰器：检查 API key 是否存在。

    Args:
        key: API key 名称（如 "OPENCLAW_GATEWAY_TOKEN"）

    Returns:
        装饰器函数

    Raises:
        ValueError: 当 API key 未提供时抛出

    Example:
        @require_api_key("OPENCLAW_GATEWAY_TOKEN")
        def my_function(gateway_token: str):
            ...
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 检查 kwargs 中是否包含 API key
            api_key = kwargs.get(key.lower()) or kwargs.get(key)
            if not api_key:
                # 检查环境变量
                api_key = os.environ.get(key)
            if not api_key:
                raise ValueError(
                    f"API key '{key}' not provided in kwargs or environment variable '{key}'"
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator
