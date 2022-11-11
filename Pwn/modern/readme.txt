C++ STL containers is NOT thread safe.
expolit the race condition between vector.push() and vector.pop(),
then you have chance to do OOB read/write.
Then you just need do normal things like other menu heap challs. 
Leak libc, hijack allocation and finally FSOP.
Or you can hijack function pointers on heap , which has a bigger success rate.

script:WIP.
