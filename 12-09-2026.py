# sub array sum equal to k
# brut force approch 

def sum_array_sum_equals_k(nums, target):
    count = 0
    for i in range(len(nums)):
        curr_sum = 0
        for j in range(i, len(nums)):
            curr_sum += nums[j]
            if curr_sum == target:
                count += 1
    return count

result = sum_array_sum_equals_k([1, 1, 1], 2)
print(result) 


# optimal approach for this
from collections import defaultdict


def sub_array_sum_equals_k_optimal(nums, target):
    seen = defaultdict(int)
    seen[0] = 1
    total, count = 0,0
    for num in nums:
        total += num
        count += seen[total - target]
        seen[total] += 1
    return count

result = sub_array_sum_equals_k_optimal([1, 1, 1], 2)
print(result) 


def product_array_except_itself(nums):
    res = []
    for i in range(len(nums)):
        product = 1
        for j in range(len(nums)):
            if i == j:
                continue
            product *= nums[j]
            print(product)
        res.append(product)
    return res

result = product_array_except_itself([1, 2, 3, 4])
print(result)


def product_array_except_itself_optimal(nums):
    n = len(nums)
    res = [1] * n
    left = 1
    for i in range(n):
        res[i] = left
        left *= nums[i]

    right = 1
    for i in range(n-1, -1, -1):
        res[i] *= right
        right *= nums[i]
    return res

result = product_array_except_itself_optimal([1, 2, 3, 4])
print(result)


def container_with_most_water(heights):
    left, right, best = 0, len(heights) - 1, 0
    while left < right:
        area = min(heights[left], heights[right]) * ( right -left)
        best = max(best, area)

        if heights[left] < heights[right]:
            left += 1
        else:
            right -= 1
    return best   

result  = container_with_most_water([1,8,6,2,5,4,8,3,7])
print(result)


def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        need = target - num
        if need in seen:
            return [seen[need], i]
        seen[num] = i
    return []

result = twoSum([2, 7, 11, 15], 9)
print(result)   


def max_profit(prices):
    min_price, best =float("inf"), 0
    for price in range(len(prices)):
        min_price = min(min_price, price)
        best = max(best, price - min_price)
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

result = contained_duplicate([1,2,3,1])  
print(result)  

def is_pallidrom(string):
    ok = lambda c: c.isalnum()
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

result = is_pallidrom("A man, a plan, a canal: Panama")
print(result)    

def three_sum(nums):
    nums.sort()
    res = []
    n = len(nums)
    for i in range(n -2):
        if i > 0 and nums[i] == nums[i - 1]:
           continue
        left, right = i + 1, n -1
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
            elif(total < 0):
                left += 1
            else:
                right -= 1
    return res; 


result = three_sum([-1, 0, 1, 2, -1, -4])
print(result)


def length_of_longest_subString(strings):
    seen = set()
    left = best = 0
    start = 0
    for right in range(len(strings)):
        while strings[right] in seen:
            seen.remove(strings[left])
            left +=1
        seen.add(strings[right])
        if right - left + 1 > best:
            best = right - left + 1
            start = left
    return strings[start: start + best]
    #     best = max(best, right - left + 1)

    # return best

result = length_of_longest_subString("dhsjhdh")
print(result)


def max_sub_array(nums):
    curr = best = nums[0]
    for num in nums[1:]:
        curr = max(num, curr + num)
        best = max(best, curr)
    return best    

result = max_sub_array([-2,1,-3,4,-1,2,1,-5,4])
print(result)










    
