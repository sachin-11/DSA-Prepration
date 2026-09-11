# two sums
def twoSums(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        need = target - num
        if need in seen:
            return [seen[need], i]
        seen[num] = i
    return []

result = twoSums([2, 7, 11, 15], 9)
print(result)


# maxprofit 
def maxProfit(prices):
    min_price, best = float("inf"), 0
    for p in prices:
        min_price = min(min_price, p)
        best = max(best, p - min_price)
    return best

result = maxProfit([7, 1, 5, 3, 6, 4])   
print(result) 

# contained Duplicate
def containedDuplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

result = containedDuplicate([1,2,3,4])   
print(result) 

# is valid pallidrom 
def is_pallidrom(string):
    okay = lambda c: c.isalnum()
    left, right = 0,  len(string) - 1
    while left < right:
        while left < right and not okay(string[left]): left += 1
        while left < right and not okay(string[right]): right -= 1
        if string[left].lower() != string[right].lower():
            return False
        left += 1
        right -= 1
    return True

result = is_pallidrom("race a car")


def threeSum(nums):
    nums.sort()
    res = []
    n = len(nums)
    for i in range( n - 2):
        if(i > 0 and nums[i] == nums[i - 1]):
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
    return res;   


result = threeSum([-1, 0, 1, 2, -1, -4])
print(result)


# maxSubArraySum 

def max_sub_array_sum(nums):
    curr = best = nums[0]
    for num in nums[1:]:
        curr = max(num, curr + num)
        best = max(best, curr)
    return best

result = max_sub_array_sum([-2,1,-3,4,-1,2,1,-5,4]) 
print(result)

# logest substring bethought repeating charector
def logest_substring_count(strings):
     seen = set()
     left = 0
     best_start, best_len = 0, 0
     for right in range(len(strings)):
        while strings[right] in seen:
            seen.remove(strings[left])
            left += 1
        seen.add(strings[right])
        if right - left + 1 > best_len:
            best_len = right - left + 1
            best_start = left
     return strings[best_start:best_start + best_len]


result = logest_substring_count("sdjshjjdshhd")
print(result)



            
              