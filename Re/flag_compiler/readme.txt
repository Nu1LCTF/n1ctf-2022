C++ template is "turing complete". flag_compiler implmented a stack-based VM in C++.
flag is checked in compile-time. The CPU has 2 registers (IP,SP) and a 17-words RAM. 
And the opcodes are stored in ROM.
You can expand the macros first , and restore all consts like this bin2int<bin_one,bin_zero,bin_one,bin_zero,bin_zero,bin_one>.
and then clang-format
The VM is easy, you can finally find out what it is doing and getflag.
Convert your input to 10 u32 -> linear transform -> linear transform2 -> fast pow -> compare 
just find the expected output , calcuate discrete log and invert two linear transforms. You will get the correct input.
