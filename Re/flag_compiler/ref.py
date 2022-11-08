import struct
flag=b'C++:teMp1aTe<Vm>_1s_cOo0l-6ut~Slow!;#<=>'
R=[*struct.unpack("I"*10,flag.ljust(40,b'\x00'))]+[0,0]
K=133723339 # prime
M=4200000037 # prime
# print(R)
for j in range(10):
    R[j]=(K*R[j]+j)%M
    K*=133723339
    K%=M
for _ in range(35):
    R[10]=R[0]
    R[11]=R[1]
    for i in range(10):
        R[i]=((R[i]+R[i+1]*2+R[i+2]*3)*K)%M
        K*=133723339
        K%=M
assert(K==1849312651)
# print(R[:10])
for i in range(10):
    R[i]=pow(4294967279,R[i],4294967291) #prime,prime
print(R[:10]) #output
