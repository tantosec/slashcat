from functools import wraps
import time


def time_based_cache(lifetime):
    def decorator(func):
        cache = {"result": None, "last_updated": 0}

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if time.time() - cache["last_updated"] < lifetime:
                return cache["result"]

            new_res = await func(*args, **kwargs)
            cache["result"] = new_res
            cache["last_updated"] = time.time()
            return new_res

        return wrapper

    return decorator
