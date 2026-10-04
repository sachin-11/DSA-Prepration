// Implement a promise-based retry utility (retry 3 times with delay).




// retry(fn, retries = 3, delay = 300) {

// }


const original = {
   user: { name: "Sam", address: { city: "Delhi" } },
   tags: ["js", "react"]
};
 
const copy1 = { ...original };
const copy2 = structuredClone(original);
 
copy1.user.address.city = "Mumbai";
copy1.tags.push("nextjs");
 
console.log(original.user.address.city);
console.log(original.tags);
console.log(copy2.user.address.city);

"mumbai"
["js", "react", "nextjs"]
"delhi"