# Proteus
## Goal
I built Proteus as a tool to assist me during the recon phase of bug bounty hunting. I found myself manually generating permutations of the subdomains I had found over and over again, so I decided it was time to automate the process. Proteus does exactly this: it takes my methodology for finding more subdomains, and automatically executes the process from start to finish.
## What to expect when using Proteus
Proteus is still in the early stages of development. The first working version (just core functionality, many features still missing) was released on January 23, 2026. I have built the tool in a way that I believe to be quite robust, with error handling wherever needed and error messages describing exactly what went wrong and how to fix it. If using the tool properly though, there shouldn't be any issues that lead to running into errors.
## What to expect in the future
I plan to expand proteus to be a pretty large project. I want to have it handle all my subdomain permutation needs, including more types of permutation and more diverse inputs and outputs. Proteus will continue to grow in the coming weeks/months/years.
## Tips for using proteus:
Proteus relies on DNSX (by ProjectDiscovery) to handle the resolving of subdomains. Because of this, you won't be able to resolve at rates as high as when using a tool like massdns (which I plan to implement eventually). I recommend setting your rate limit on DNSX somewhere between 200 and 300 rps, as higher than this can cause your ISP to rate limit you. Depending on your ISP this limit may be higher or lower, so take care when choosing a rate limit and experiment in small batches first.
## Small VPS machines 
Proteus is fairly lightweight, meaning that for most small and medium sized inputs a small vps should be able to handle it just fine. With small I specifically mean a VPS like DigitalOcean's 1vCPU and 1GB RAM droplets, or similar machines from other services.

For larger inputs, resulting in generated lists of 5 million targets or more, I recommend splitting the workload into smaller batches as DNSX might cause your machine to freeze or get stuck in a swap loop when attempting to load large lists into a small amount of RAM. To solve this issue I will be implementing a "low RAM mode", but this currently has not been implemented yet.
## Copyright
As per the MIT license, you are permitted to use, modify, distribute, etc. Proteus, provided that any projects based on Proteus or using Proteus also include the MIT license. I would also appreciate to be credited where my work is used, but this is not a hard requirement
## Contact
If you feel the need to contact me for any reason please feel free to do so on discord (._lars)