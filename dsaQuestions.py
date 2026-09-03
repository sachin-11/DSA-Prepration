# twosums
def two_sums(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        contained = target - num
        if contained in seen:
            return [seen[contained], i]

        seen[num] = i

    return []


print(two_sums([2, 7, 11, 15], 9))



def max_profit(prices):
    best = float('inf')
    max_value = 0
    for price in prices:
        best = min(best, price)
        max_value = max(max_value, price - best)
    return max_value    


print(max_profit([7, 1, 5, 3, 6, 4]))


def contained_duplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False 



print(contained_duplicate([1, 2, 3, 3]))


def is_valid(string):
    def ok(c):
        return c.isalnum()

    left, right = 0, len(string) - 1
    while left < right:
        while left < right and not ok(string[left]):
            left += 1
        while left < right and not ok(string[right]):
            right -= 1
        if string[left].lower() != string[right].lower():
            return False
        left += 1
        right -= 1

    return True


print(is_valid("A man, a plan, a canal: Panama"))

def isValid(string):
    def ok(c):
        return c.isalnum()
    
    left, right = 0, len(string) - 1
    while left < right :
        while left < right and not ok(string[left]):
            left += 1
        while left < right and not ok(string[right]):
            right -= 1
        if string[left].lower() != string[right].lower():
            return  False
        left += 1
        right -= 1

    return True   