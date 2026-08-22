const twoSums = (nums, target) => {
    const seen = new Map();
    for(let i = 0; i < nums.length; i++) {
        let found = target - nums[i]
        if(seen.has(found)) return [seen.get(found), i]
        seen.set(nums[i], i)
    }

    return []
}

console.log(twoSums([2, 7, 11, 15], 9)) // [0, 1]


const maxProfit = (prices) => {
    let min = Infinity;
    let max = 0;

    for(let i = 0; i < prices.length; i++) {
        min = Math.min(min, prices[i])
        max = Math.max(max, prices[i] - min)
    }
    return max
}

console.log(maxProfit([7, 1, 5, 3, 6, 4])) // 5


const containsDuplicate = (nums) => {
    const seen = new Set();
    
    for(let i = 0; i < nums.length; i++) {
        if(seen.has(nums[i])) return true
        seen.add(nums[i])
    }
    return false    
}


console.log(containsDuplicate([1, 2, 3, 1])) // true
console.log(containsDuplicate([1, 2, 3, 4])) // false


const isValidPalidrom = (string) => {
    let okay =  c => /[a-z0-9]/i.test(c);
    let left = 0, right = string.length - 1
    while(left < right) {
        while(left < right && !okay(string[left])) left++
        while(left < right && !okay(string[right])) right--
        if(string[left].toLowerCase() !== string[right].toLowerCase()) return false
        left++
        right--
    }

    return true

}



console.log(isValidPalidrom("A man, a plan, a canal: Panama"))

const threeSum = (nums) => {
  nums.sort((a, b) => a - b)
  let res = [];
  for(let i = 0; i < nums.length - 2; i++) {
    if(i > 0 && nums[i] === nums[i - 1]) continue
    let left = i + 1, right = nums.length -1
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



console.log(threeSum([-1, 0, 1, 2, -1, -4]))


//maxsubArray Sum

const maxSubArray = (nums) => {
 let curr = 0, max = 0
 for(let i = 0; i < nums.length; i++) {
    curr = Math.max(nums[i], curr + nums[i])
    max = Math.max(max, curr)
 }
 return max
}

console.log(maxSubArray([-2,1,-3,4,-1,2,1,-5,4]))


const lengthOfLongestSubstring = (string) => {
    const seen = new Set();
    let left = 0, best = 0;
    for(let right = 0; right < string.length; right++) {
        while(seen.has(string[right])) {
            seen.delete(string[left])
            left++
        
        }

        seen.add(string[right])
        best = Math.max(best, right - left + 1)
    }
    return best
}


console.log(lengthOfLongestSubstring("abcabcbb"))
console.log(lengthOfLongestSubstring("bbbbb"))


const rangebasedSum = (nums) => {
    const prefix = new Array(nums.length + 1).fill(0)
    for(let i = 0; i < nums.length; i++) {
        prefix[i + 1] = prefix[i] + nums[i]
    }

    return prefix

}


console.log(rangebasedSum([1, 3, 4, 8, 7]))






