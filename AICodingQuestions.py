from openai import OpenAI

client = OpenAI();


def chat(system_prompt: str, user_prompt: str, model: str = "gpt-4-min") -> str:
    response = client.chat.completions.create(
        model = model,
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "contnet": user_prompt},
        ],
    )
    return response.chat[0].message.content


if _name_ == "_main_":
    print("you are helpfull AI assistance", "explain rag in 2 lines")


# Rate limiter with exponentional backoff
import random
import time

class RateLimitError(Exception):
    pass


def call_with_backoff(fun, max_retriers: int = 5, base_delay: float = 0.1, max_delay: float = 30.0):
    for attempt in range(max_retriers):
        try:
            return fun()
        except RateLimitError:
            if attempt == max_retriers - 1:
                raise
            delay = min(max_delay, base_delay * (2 ** attempt))
            jitter = random.uniform(0, delay * 0.5)
            wait_time = delay + jitter
            print(f"rate limited, retrting in {wait_time} and {attempt + 1}")
            time.sleep(wait_time)


            # time out connection ke liye robust error handling
            import time
            from openai import OpenAI, APITimeOutError, APIConnectionError, RateLimitError, BadRequestError, AuthenticationError

            client  = OpenAI()

            RETRYBABLE_ERRORS = (APITimeOutError, APIConnectionError, RateLimitError)
            NON_RETRYABLE_ERRORS = (BadRequestError, AuthenticationError)


            def safe_chat(messages, model:str = "gpt-4o-mini", max_reties: int = 3):
                for attempt in range(max_retriers):
                    try:
                        return client.chat.completions.create(model= model, messages= messages, timeout = 30)
                    except RETRYBABLE_ERRORS as e:
                        if attempt ==- max_retriers -1:
                            raise
                        wait = 2 ** attempt
                        print(f"retryable error retying in {wait}")
                        time.sleep
                    except NON_RETRYABLE_ERRORS as e:
                        print(f"no retryble error : {e}")


# ---------------------------------------------------------------
# 1. What are Decorators in Python? How do they work?
# ---------------------------------------------------------------
# A: A decorator is a function that takes another function as input
# and extends or modifies its behavior without changing the original
# function's code. In Python, decorators use the @ syntax.
#
# - Decorators are higher-order functions — they wrap another function.
# - Common use cases: logging, authentication, caching, timing, retry logic.
# - Python has built-in decorators like @staticmethod, @classmethod, @property.

# Code Example:
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before function call")
        result = func(*args, **kwargs)
        print("After function call")
        return result
    return wrapper


@my_decorator
def greet(name):
    print(f"Hello, {name}")


def my_decorators(func):
    def wrapper(*arags, **kwargs):
        print("before function call")
        result = func(*arags, **kwargs)
        print("after function call")
        return result
    return wrapper


if __name__ == "__main__":
    greet("Sachin")
    # Output:
    # Before function call
    # Hello, Sachin
    # After function call

    # @my_decorator likhna, is line ke barabar hai:
    # greet = my_decorator(greet)
    # yani decorator ek function leta hai aur naya (wrapped) function return karta hai.


# ---------------------------------------------------------------
# Real-world example: timing decorator
# ---------------------------------------------------------------
# Use case: kisi bhi function ko bina uske andar code chede, uska
# execution time measure karna (interview mein sabse common example).
import time
from functools import wraps


def timer(func):
    @wraps(func)  # func ka __name__/__doc__ preserve karta hai (debugging ke liye)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.4f}s")
        return result
    return wrapper


@timer
def slow_square(n):
    time.sleep(0.2)
    return n * n


if __name__ == "__main__":
    print(slow_square(5))
    # Output (approx):
    # slow_square took 0.2001s
    # 25


# ---------------------------------------------------------------
# Real-world example: decorator jo arguments leta hai (parameterized)
# ---------------------------------------------------------------
# Use case: retry logic — function fail ho to N baar retry kare.
def retry(max_attempts: int = 3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"attempt {attempt} failed: {e}")
                    if attempt == max_attempts:
                        raise
        return wrapper
    return decorator


_calls = {"n": 0}


@retry(max_attempts=3)
def flaky():
    _calls["n"] += 1
    if _calls["n"] < 3:
        raise ValueError("temporary failure")
    return "success"


if __name__ == "__main__":
    print(flaky())
    # Output:
    # attempt 1 failed: temporary failure
    # attempt 2 failed: temporary failure
    # success


# ---------------------------------------------------------------
# Real-world example: auth decorator
# ---------------------------------------------------------------
# Use case: function ko chalane se pehle check karo ki user
# authenticated hai ya nahi.
def require_auth(func):
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        if not user.get("is_authenticated"):
            raise PermissionError("Not authenticated")
        return func(user, *args, **kwargs)
    return wrapper


@require_auth
def view_profile(user):
    return f"Profile of {user['name']}"

def require_auth(func):
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        if not user.get("is authenticated"):
            raise PermissionError("Not authenticated")
        return func(user, *args, **kwargs)
    return wrapper


if __name__ == "__main__":
    print(view_profile({"name": "Sachin", "is_authenticated": True}))
    try:
        view_profile({"name": "Guest", "is_authenticated": False})
    except PermissionError as e:
        print(f"blocked: {e}")
    # Output:
    # Profile of Sachin
    # blocked: Not authenticated


