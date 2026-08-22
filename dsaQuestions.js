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




