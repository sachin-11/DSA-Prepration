# Mutable vs Immutable types kya hote hain?

# Immutable: object create hone ke baad uska value/content change nahi ho sakta.
# Koi bhi "change" karoge to naya object ban jayega (memory address badal jayega).
# Examples: int, float, bool, str, tuple, frozenset

x = "hello"
print(id(x))
x += " world"       # naya string object banta hai
print(id(x))         # id change ho gayi

t = (1, 2, 3)
# t[0] = 10          # TypeError: tuple item assignment not supported


# Mutable: object create hone ke baad uska content in-place change ho sakta hai.
# Memory address (id) same rehta hai, sirf value andar se badalti hai.
# Examples: list, dict, set, bytearray, custom classes (by default)

lst = [1, 2, 3]
print(id(lst))
lst.append(4)         # same object modify ho raha hai
print(id(lst))         # id same rahegi


# Isliye function argument pass karte waqt farak padta hai:
def add_item(l):
    l.append("new")   # original list bhi change ho jayegi (mutable, reference pass hua)

def add_text(s):
    s += " new"        # original string change NAHI hogi (immutable, naya object banta hai andar)
    return s

my_list = [1, 2]
my_list = [1, 2]
add_item
add_item(my_list)
print(my_list)          # [1, 2, 'new']

my_str = "hi"
add_text(my_str)
print(my_str)            # "hi"  (unchanged)


# Interview tip: mutable types ko dict key ya set element nahi bana sakte,
# kyunki unka hash value change ho sakta hai. Immutable types hashable hote hain.
# d = {[1,2]: "x"}   # TypeError: unhashable type: 'list'
d = {(1, 2): "x"}    # tuple (immutable) chalega
print(d)


def add_message(msg, history = []):
    history.append(msg)
    return history

add_message("hello")
add_message("worlld")
result = add_message(add_message("hello", "worls"))
print(result)

# closure is pythin 

def make_llm_call(model_name):
    async def call(prompt):
        return await api_call(model = model_name, prompt = prompt)
    return call


# @lru_cache kab use karni chahiye aur iska kya use he?
#
# Use karo jab function:
#   1. "pure" ho -> same input pe hamesha same output de (no side effects, no randomness)
#   2. expensive ho (recursion, heavy computation, I/O jaise DB/API call jiska result badalta nahi)
#   3. baar baar same arguments ke saath call hota ho (recursion me overlapping subproblems, ya repeated lookups)
#   4. arguments hashable hon (int, str, tuple, frozenset) - list/dict args nahi chalenge
#
# Kya karta he: pehli baar function ek particular input ke liye run hota he,
# result ko internally dict me {args: result} store kar leta he.
# Agla call same args ke saath aaya to seedha cache se result return, function dobara run nahi hota.

from functools import lru_cache

# Without cache: exponential time O(2^n)
def fib_slow(n):
    if n < 2:
        return n
    return fib_slow(n - 1) + fib_slow(n - 2)

# With cache: linear time O(n), kyunki har unique n sirf ek baar compute hota he
@lru_cache(maxsize=None)   # maxsize=None -> unlimited cache; warna LRU eviction hogi
def fib_fast(n):
    if n < 2:
        return n
    return fib_fast(n - 1) + fib_fast(n - 2)

print(fib_fast(35))
print(fib_fast.cache_info())   # hits, misses, maxsize, currsize
fib_fast.cache_clear()          # cache reset karni ho to

# Gotcha: mutable/unhashable arg pass kiya to TypeError aayega
# fib_fast([1, 2])   # TypeError: unhashable type: 'list'

# Gotcha: long-running process (jaise server) me maxsize=None se memory grow karti rahegi
# agar inputs unbounded hain -> tab maxsize ek reasonable number rakho (LRU purane entries evict karega)
