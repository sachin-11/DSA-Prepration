# two sums code

def twSum(num, target):
    seen = {}
    for i, num in enumerate(num):
        need = target - num
        if need in seen:
            return [seen[need], i]
        seen[num] = i

    return []

result = twSum([2, 7, 11, 15], 9)
print(result)


def maxProfit(prices):
    min_price, best = float("inf"), 0
    for price in prices:
        min_price = min(min_price, price)
        best = max(best, price - min_price)
    return best  

result = maxProfit([7, 1, 5, 3, 6, 4])
print(result)


def contained_duplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

result = contained_duplicate([1, 2, 3, 3, 8])
print(result)


def is_pallidrom(num):
    ok = lambda c: c.isalnum()
    left, right = 0, len(num) - 1
    while left < right:
        while left < right and not ok(num[left]): left += 1
        while left < right and not ok(num[right]): right -= 1
        if num[left].lower() != num[right].lower():
            return False
        left += 1; right -= 1
    return True

result = is_pallidrom("A man, a plan, a canal: Panama")
print(result)


def threeSum(nums):
    nums.sort()
    res = []
    n = len(nums)
    for i in range(n - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        left, right = i + 1, n - 1
        while left < right:
            sum = nums[left] + nums[right] + nums[i]
            if sum == 0:
                res.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]: left += 1
                while left < right and nums[right] == nums[right - 1]: right -= 1
                left += 1; right -= 1

            elif sum < 0:
                left += 1
            else:
                right -= 1
    return res;

result = threeSum([-1, 0, 1, 2, -1, -4])
print(result)            


def maxsubArraySum(nums):
    curr = best = nums[0]
    for num in nums[1:]:
        curr = max(num, curr + num)
        best = max (best, curr)

    return best;

result = maxsubArraySum([-2,1,-3,4,-1,2,1,-5,4])
print(result)  

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

result = length_of_longest_substring("aaabyhdhdj")
print(result)






        
    

     
