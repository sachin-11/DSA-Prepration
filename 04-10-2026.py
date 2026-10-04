# decorator function 

def greet():
    return "hello"

another_name = greet

print(another_name)


# basic decorator 

def logger(fun):
    def wrapper():
        print("function start")
        result = fun()
        print("function end")
        return result
    return wrapper


@logger
def greet():
    return "hello sachin"

print(greet())


# retry machanism 

import time
from functiontools import wraps


def retry(time = 3, delay = 1, exception = (Exception,)):
    def decorator(fun):
        @wraps(fun)
        def wrapper(*arags, **kwargs):
            for attempt in range(1, time = 1):
                try:
                    return fun(*arags, **kwargs)
                except exception as e:
                    print(f"attempt {attempt} failed: {e}")
                    if attempt == time:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator


def required_role(role):
    def decorators(fun):
        @wraps(fun)
        def wrapper(user, *args, **kwargs):
            if user.get("role") != role:
                raise PermissionError(f"{user['name']} is not in {role}")
            return fun(user, *args, **kwargs)
        return wrapper
    return decorators


@required_role("admin")
def delete_user(user, user_id):
    return f"user {user_id} deleted by {user['name']}"

print(delete_user({"name" : "sachin", "role": "admin"}, 101))


def logging(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        print(f"calling {fun._name_} with {args} {kwargs}")
        result = fun(*args, **kwargs)
        print(f"{fun._name} returned {result}")
        return result
    return wrapper




def retry(times = 3, delay = 1):
   def decorator(fun):
       @wraps(fun)
       def wrapper(*args, **kwargs):
           for attempt in range(1, time + 1):
               try:
                   return fun(*args, **kwargs)
               except Exception as e:
                   print(f"attempt {attempt} failed as {e}")
                   if attempt == times:
                       raise
                   time.sleep(delay)
       return wrapper
   return decorator


def rate_limit(max_call, period):
    def decorator(fun):
        calls = []
        @wraps(fun)
        def wrapper(*args, **kwargs):
            now = time.time()
            while calls and now - calls[0] > period:
                calls.pop(0)
            if len(calls) >= max_call:
                raise RuntimeError("too many connection try again")
            calls.append(now)
            return fun(*args, **kwargs)
        return wrapper
    return decorator


@rate_limit(max_call= 3, period= 5)
def api_call():
    return "okay"

for i in range(5):
    try:
        print(i + 1, api_call())
    except RuntimeError as e:
        print(i+ 1, "error:", e)



                      



                    


