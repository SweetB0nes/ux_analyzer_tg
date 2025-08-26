from __future__ import annotations
from typing import Any, Callable
import time

def invoke_with_retry(fn: Callable[[dict], Any], inputs: dict, attempts: int = 3, base_delay: float = 0.8) -> Any:
    last_err = None
    for i in range(1, attempts + 1):
        try:
            return fn(inputs)
        except Exception as e:
            last_err = e
            if i == attempts:
                raise
            time.sleep(base_delay * (2 ** (i - 1)))
    if last_err:
        raise last_err
