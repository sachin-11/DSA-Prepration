# from langchain_openai import ChatOpenAI
# from langchain_core.tools import tool
# from langchain.agent import create_react_agent, AgentExcutor
# from langchain import hub


# # tool define karo

# @tool
# def get_weather(city: str) -> str:
#     """get the current weather of current city when user asked about city"""
#     return f"{city}: 32°C, Humid"

# @tool
# def calculater(expression:str) -> str:
#     """ calculte the expression like 2 + 2"""
#     try:
#         return str(eval(expression))
#     except:
#         return "Invalid expression"

# @tool
# def search_web(query:str) -> str:
#     """get query of serach web reasult"""
#     return f"search for result of the {query}"

# tools = [get_weather, calculater, search_web]


# # LLM calling 
# llm  = ChatOpenAI(model = "gpt-4o-min", tempreture = 0)
# prompt = hub.pull("hwchase17/react")

# agent = create_react_agent(llm = llm, tools = tools, prompt = prompt)

# # agent actually run karta he tool me 

# agent_exicutor = AgentExcutor(
#     agent = agent,
#     tools = tools,
#     verbose = True,
#     max_itration = 5
# )


# result = agent_exicutor.invoke({
#     "input": "delhi ka weather kya he kal kitna change honga"
# }) 

# print(result["output"])


def contained_duplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False


result = contained_duplicate([1, 2, 3, 4, 5])
# result = contained_duplicate([1, 2, 3, 4, 4])
print(result)



def two_sums(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        need = target - num
        if need in seen:
            return [seen[need], i]
        seen[num] = i
    return []

result = two_sums([2, 7, 11, 15], 9)
print(result) 


def max_profit(prices):
     min_price, best = float("inf"), 0
     for price in prices:
         min_price = min(min_price, price)
         best = max(best, price - min_price)
     return best

result = max_profit([7, 1, 5, 3, 6, 4])   
print(result)  


def is_pallidrom(string):
    okay = lambda c : c.isalnum()
    left, right = 0, len(string) - 1
    while left < right:
        while left < right and not okay(string[left]): left += 1
        while left < right and not okay(string[right]): right -= 1
        if string[left].lower() != string[right].lower():
            return False
        left += 1
        right -= 1
    return True    


result = is_pallidrom("race a car")
print(result)


def three_sum(nums):
    nums.sort()
    res = []
    n = len(nums)
    for i in range(n - 2):
        if (i > 0 and nums[i] == nums[i - 1]):
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


def max_subArray(nums):
    curr = best = nums[0]
    for num in nums:
        curr = max(num, curr + num)
        best = max(best, curr)
    return best

result = max_subArray([-2,1,-3,4,-1,2,1,-5,4])
print(result) 


def longest_substring_count(strigs):
    seen = set()
    left = 0
    best_start, best_length = 0, 0
    for right in range(len(strigs)):
        while(strigs[right] in seen):
            seen.remove(strigs[left])
            left += 1
        seen.add(strigs[right])
        if right - left + 1 > best_length:
            best_length = right - left + 1
            best_start = left
    return strigs[best_start: best_start + best_length]
    # return best_start 
         
result = longest_substring_count("sdjshjjdshhd")
print(result)

