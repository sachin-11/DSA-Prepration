# valid parebtisis

def is_valid(string: str):
    stack = []
    pairs = {
        '(': ')',
        '{': '}',
        '[': ']',
    }

    for ch in string:
        if ch in (
            '(',
            '{',
            '['
        ):
            stack.append(ch)
        else:
            if not stack or stack.pop != pairs[ch]:
                return False
        return len(stack) == 0



# min stack

class minStack:
    def __init__(self):
        self.stack = []
        self.minStack = []

    def push(self, value: int) -> None:
        self.stack.append(value)
        curr_min = min(value, self.minStack[-1]) if self.minStack else value
        self.minStack.append(curr_min)
    def pop(self) -> None:
        self.stack.pop()
        self.minStack.pop()
    def top(self) -> int:
        return self.stack[-1]
    def get_min(self) -> int:
        return self.minStack[-1]    



            
