from typing import Any, Callable

import functools
import time

from loguru import logger


def log_function_enter_exit(
    *, entry=True, exit=True, level="DEBUG"
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for logging function calls.

    Args:
        entry: Log the function call.
        exit: Log the function return.
        level: Log level.

    Returns:
        The decorated function.
    """

    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(level, "Entering '{}' (args={}, kwargs={})", name, args, kwargs)
            result = func(*args, **kwargs)
            if exit:
                logger_.log(level, "Exiting '{}' (result={})", name, result)
            return result

        return wrapped

    return wrapper


def timeit(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for logging the execution time of a function.

    Args:
        func: The function to be decorated.

    Returns:
        The decorated function.
    """

    @functools.wraps(func)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug("Function '{}' executed in {:f} s", func.__name__, end - start)
        return result

    return wrapped
