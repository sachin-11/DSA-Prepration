# two Sums

def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        value = target - num
        if value in seen:
            return [seen[value], i]
        seen[num] = i

    return []

result = two_sum([2, 7, 11, 15], 9)  
print(result)  


def max_profit(prices):
    min_price, best = float("inf"), 0
    for p in prices:
        min_price = min(min_price, p)
        best = max(best, p - min_price)
    return best

result = max_profit([7, 1, 5, 3, 6, 4])
print(result)

def contained_duplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

result = contained_duplicate([1,2,3,4])
print(result)

def is_palidrom(string):
    okay = lambda c : c.isalnum()
    left, right = 0, len(string) - 1
    while left < right:
        while left < right and not okay(string[left]): left += 1
        while left < right and not okay(string[right]): right -= 1
        if string[left].lower() != string[right].lower():
            return False
        left +=1
        right -= 1
    return True

result = is_palidrom("A man, a plan, a canal: Panama")
print(result)

def three_sum(nums):
    nums.sort()
    res = []
    n = len(nums)
    for i in range(n - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        left, right = i + 1, n - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                res.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1

    return res


print(three_sum([-1, 0, 1, 2, -1, -4]))


def max_sub_array(nums):
    curr = best = nums[0]
    for num in nums[1:]:
        curr = max(num, curr + num)
        best = max(best, curr)
    return best

result = max_sub_array([-2,1,-3,4,-1,2,1,-5,4])
print(result)\


def length_of_longest_substring(string):
    seen = set()
    left = best = 0
    for right in range(len(string)):
        while string[right] in seen:
            seen.remove(string[left])
            left += 1
        seen.add(string[right])
        best = max(best, right - left + 1)
    return best

result = length_of_longest_substring("abcabcbb")
print(result)


def longest_substring(string):
    seen = set()
    left_best = right





