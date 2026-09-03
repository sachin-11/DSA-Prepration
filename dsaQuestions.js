//twosums
const twoSums = (nums, target) => {
  const seen = new Map();
  for(let i = 0; i < nums.length; i++) {
      let contained = target - nums[i]
      if(seen.has(contained)) {
         return [seen.get(contained), i]
      }

      seen.set(nums[i], i)
  }

  return []
}

console.log(twoSums([2, 7, 11, 15], 9))


const maxProfit = (prices) => {
  let best = Infinity, max = 0
  for(let i = 0; i < prices.length; i++) {
    best = Math.min(best, prices[i])
    max = Math.max(max, prices[i] - best)
  }
  return max;
}

console.log(maxProfit([7, 1, 5, 3, 6, 4]))



const containedDuplicate = (nums) => {
  const seen = new Set();
  for(let i = 0; i < nums.length; i++) {
     if(seen.has(nums[i])) return true
     seen.add(nums[i])
  }
  return false
}


console.log(containedDuplicate([1,2,3,3]))


const isValid = (string) => {
   const ok = c => /[a-z0-9]/i.test(c); 
   let left = 0, right  = string.length -1
   while(left < right) {
       while(left < right && !ok(string[left])) left++
       while(left < right && !ok(string[right])) right--
       if(string[left].toLowerCase() !== string[right].toLowerCase()) return false
       left++
       right--
   }

   return true
}

console.log(isValid("A man, a plan, a canal: Panama"))



const threeSums = (nums) => {
  //sort 
  nums.sort((a, b) => a - b)
  let res = [];
  for(let i = 0; i < nums.length - 2; i++) {
    if(i > 0 && nums[i] === nums[i + 1]) continue
    let left =  i+ 1, right = nums.length -1;
    while(left < right) {
        let sum = nums[i] + nums[left] + nums[right]
        if(sum === 0) {
            res.push([nums[i], nums[left], nums[right]])
            while(left < right && nums[left] === nums[left+ 1]) left++
            while(left < right && nums[right] === nums[right - 1]) right--
            left++
            right--
        } else if(sum < 0) {
            left++
        } else {
            right--
        }
    }
  }
  return res;
}


console.log(threeSums([-1, 0, 1, 2, -1, -4]))


// bar();       // ❌ TypeError — bar is undefined at call time
// var bar = function () { console.log("bye"); };



//closures
const counter = () => {
    let count = 0;
    function increment() {
        count++
        return count
    }
    return increment;
}

const c = counter()
console.log(c())
console.log(c())

function createBankAccount(initial) {
    let balance = initial
    return {
        deposite: amt => (balance += amt),
        withdraw: amt => (balance -= amt),
        getbalance: () => balance
    }
}

const acc = createBankAccount(100);
acc.deposite(50);
console.log(acc.getbalance())
console.log(acc.balance)



const maxSubArray = (nums) => {
  let curr = nums[0], best = nums[0]
  for( i = 1; i < nums.length; i++) {
    curr = Math.max(nums[i], curr + nums[i])
    best = Math.max(best, curr)
  }
  return best;
}

console.log(maxSubArray([-2,1,-3,4,-1,2,1,-5,4]))


const lengthOfLogestSubstring = (string) => {
    let seen = new Set();
    let left = 0, best = 0;
    for(let right = 0; right < string.length -1; right++) {
        while(seen.has(right)) {
            seen.delete(string[left])
            left++
        }
        seen.add(string[right])
        best = Math.max(best, right - left + 1)
    }

    return best;
}


console.log(lengthOfLogestSubstring('aabcdgh'));


const subArraySumEqualsK = (nums, k) => {
  const seen = new Map([[0, 1]]);
  let sum = 0, count = 0;
  for(let num of nums) {
      sum += num
    count += seen.get(sum - k) || 0
    seen.set(sum, (seen.get(sum) || 0) + 1)
  }
  return count
}

console.log(subArraySumEqualsK([1, 1, 1], 2))



const productOfArrayExceptItself = (nums) => {
   let n = nums.length
   let res = new Array(n).fill(1)
   let left = 1;
   for(let i = 0; i < n; i++) {
     res[i] = left;
     left *= nums[i];
   }
   let right = 1;
   for(let i = n -1; i >= 0; i--) {
      res[i] *= right
      right *= nums[i]
   }

   return res;

}

console.log(productOfArrayExceptItself([1, 2, 3, 4]))

const maxArea = (heights) => {
    let left = 0, right = heights.length -1, best = 0
    while(left < right) {
        const area = Math.min(heights[left], heights[right]) * (right - left)
        best = Math.max(best, area)
        if(heights[left] < heights[right]) {
            left++

        } else {
            right--
        }
    }
    return best
}


console.log(maxArea([1,8,6,2,5,4,8,3,7]))



//stack and Queue lebel Questions 

const isValidp = (s) => {
  let pairs = { ')': '(', ']': '[', '}': '{' };
  let stack = [];
  for(let ch of s) {
     if(ch === '{' || ch == '[' || ch === '(') {
      stack.push(ch)
     } else if(stack.pop() !== pairs[ch]) return false
  }
  return stack.length === 0
}

console.log(isValidp('{[]}'))



//stack problem regarding min stack

class MinStack {
  constructor() {
    this.stack = []
    this.minstack = []
  }

  push(val) {
    this.stack.push(val)
    const currentMin = this.minstack.length ? Math.min(val, this.minstack[this.minstack.length -1]): val
    this.minstack.push(currentMin)
  }

  pop() {
    this.stack.pop()
    this.minstack.pop()
  }

  top(){
    return this.stack[this.stack.length -1]
  }

  getMin() {
    return this.minstack[this.minstack.length - 1]
  }
}

const st = new MinStack()
st.push(-2)
st.push(0)
st.push(-3)
console.log(st.getMin())  // -3
st.pop()
console.log(st.top())     // 0
console.log(st.getMin())  // -2


//daily temorature 

const dailyTemptreture = (tempretures) => {
    const result = new Array(tempretures.length - 1).fill(0);
    const stack = [];
    for(let i = 0; i < tempretures.length; i++) {
       while(i > 0 && tempretures[i] > tempretures[stack[stack.length - 1]]){
           const prevIndex = stack.pop();
           result[prevIndex] = i - prevIndex
       }
       stack.push(i)
    }
    return result;
}


//largest reactagle























