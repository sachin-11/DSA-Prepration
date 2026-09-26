def two_sum(nums, target):
    seen = {}
    for i , num in enumerate(nums):
        need = target - num
        if need in seen:
            return [ seen[need], i]
        seen[num] = i
    return []

result = two_sum([2, 7, 11, 15], 9)
print(result)    


def max_profit(prices):
    min_price,  best = float("inf"), 0
    for p in prices:
        min_price = min(min_price, p)
        best = max(best, p - min_price)
    return best

result = max_profit([7, 1, 5, 3, 6, 4]) 
print(result)   

def containedDuplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

result = containedDuplicate([1, 2, 3, 4, 5])
print(result) 


def is_pallidrom(strings):
    okay = lambda c: c.isalnum()
    left, right= 0, len(strings) -1
    while left < right:
        while left < right and not okay(strings[left]): left += 1
        while left < right and not okay(strings[right]): right -= 1
        if(strings[left].lower() != strings[right].lower()):
               return False
        left += 1
        right -= 1
    return True

result = is_pallidrom("A man, a plan, a canal: Panama")
print(result)


def three_sum(nums):
    nums.sort()
    res = []
    n = len(nums)
    for i in  range(n - 2):
        if i > 0 and nums[i] == nums[i -1]:
            continue
        left, right = i + 1, n - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                res.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]: left += 1
                while left < right and nums[right] == nums[right - 1]: right -= 1
                left += 1
                right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1
    return res

result = three_sum([-1, 0, 1, 2, -1, -4])
print(result)


def max_sub_array_sum(nums):
    curr = best= nums[0]
    for num in nums[1:]:
        curr = max(num, curr + num)
        best = max(best, curr)
    return best

result = max_sub_array_sum([-2,1,-3,4,-1,2,1,-5,4])
print(result)


def length_of_longest_substring(strings):
    seen = set()
    left = best_len = best_left = 0
    for right in range(len(strings)):
        while strings[right] in seen:
            seen.remove(strings[left])
            left += 1
        seen.add(strings[right])
        if right - left + 1 > best_len:
            best_len = right - left + 1
            best_left = left
    return strings[best_left:best_left + best_len]

result = length_of_longest_substring("abcabcbb")
print(result)




                


