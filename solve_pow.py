# python3
import gmpy2,os
from pwn import remote
def do_pow(r:remote):
    if os.environ.get('NOPOW') is not None: return
    r.recvuntil(b'2^(2^')
    bit=int(r.recvuntil(b')',drop=True))
    r.recvuntil(b'mod ')
    mod=int(r.recvuntil(b' =',drop=True))
    r.sendline(str(gmpy2.powmod(2,gmpy2.bit_set(0,bit),mod)).encode())
    r.recvuntil(b'ok\n')
