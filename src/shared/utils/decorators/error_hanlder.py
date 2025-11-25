from functools import wraps
import logging
import asyncio
from typing import Callable, Any, Type, Optional, Union

logger = logging.getLogger(__name__)

def error_handler(module: str, custom_exception: Optional[Type[Exception]] = None, **exception_kwargs) -> Callable:
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in {module}.{func.__name__}: {str(e)}")
                    
                    if custom_exception:
                        error_data = {
                            "message": str(e),
                            "module": module,
                            "function": func.__name__,
                            **exception_kwargs
                        }
                        raise custom_exception(**error_data) from e
                    else:
                        raise
            return async_wrapper
        else:
            @wraps(func) 
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in {module}.{func.__name__}: {str(e)}")
                    
                    if custom_exception:
                        error_data = {
                            "message": str(e),
                            "module": module,
                            "function": func.__name__,
                            **exception_kwargs
                        }
                        raise custom_exception(**error_data) from e
                    else:
                        raise
            return sync_wrapper
    return decorator