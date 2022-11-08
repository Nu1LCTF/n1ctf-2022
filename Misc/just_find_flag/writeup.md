

## just find flag

### 

Extract mem.zip will get mem.raw which is a memory dump. 

We can first use `strings` to get some infomation:

```bash
> strings mem.raw | grep flag

...
flag.zip
C:\Users\dora\Desktop\flag.zip
flag.txtp&X
...
```

It is obviously that there should be a flag.zip in the .mem file.

`foremost` could help us easiliy extract all the zip file.

```bash
> foremost mem.raw
> ls output/zip 
01377758.zip  02522188.zip
```

There is a flag.txt in 01377758.zip. However, It is encrypted, we need a password.

### 

Use `volatility` to analysis it. If we read the cmd history, we can get a hint.

```bash
> volatility -f mem.raw --profile Win7SP1x64 cmdscan

...
Cmd #0 @ 0x382d60: echo "Stucked? You can ask WallPaper god for help."
...
```

And the normally useful `filescan`, `pslist` can not help us get more information about flag.zip

It may be a little imaginative to associate it with the Wallpaper in Windows. The default Wallpaper in Win7SP1x64 is *C:\Windows\Web\Wallpaper\Windows\img0.jpg*，let's search the file related to "Wallpaper" or "img0"

```bash
> volatility -f mem.raw --profile Win7SP1x64 filescan | grep "Wallpaper\|img0"

Volatility Foundation Volatility Framework 2.6
0x000000007eee11c0     10      0 R--r-- \Device\HarddiskVolume1\Windows\Web\Wallpaper\Windows\img0.jpg
0x000000007fc48f20     16      0 R--r-d \Device\HarddiskVolume1\Windows\Web\Wallpaper\Windows\img0.jpeg
```

dump "img0.jpeg" and look at it, you will get the key of password of the .zip file.

```
> volatility -f mem.raw --profile Win7SP1x64 dumpfiles -Q 0x7fc48f20 -D .
DataSectionObject 0x7fc48f20   None   \Device\HarddiskVolume1\Windows\Web\Wallpaper\Windows\img0.jpeg

> eog file.None.0xfffffa8001c98010.dat	# the file just generated
```

the content at the picture is:

```
Are you finding a password?
password is: 
md5(’{full path of the file you want to extract}’.encode()).hexdigest()
1，full path means: you can get the content by type `cat {full path}`
2，full path of target file does not includes “Desktop”
```

We can get the password of the flag.zip if we find its full path.

### 

We have tried `filescan` to find some information about flag, but nothing.

But another plugin `ftmparser` can help us:

```
> volatility -f mem.raw --profile=Win7SP1x64 mftparser | grep flag

Volatility Foundation Volatility Framework 2.6
00000001f0: 28 66 69 6c 65 2c 20 66 6c 61 67 2c 20 6d 6f 64   (file,.flag,.mod
2022-11-04 19:02:03 UTC+0000 2022-11-04 19:02:03 UTC+0000   2022-11-04 19:02:03 UTC+0000   2022-11-04 19:02:03 UTC+0000   Users\dora\AppData\Roaming\MICROS~1\Windows\Recent\flag.lnk
0000000050: 32 00 00 00 00 00 00 00 00 00 80 00 66 6c 61 67   2...........flag
00000000e0: 5c 44 65 73 6b 74 6f 70 5c 66 6c 61 67 2e 7a 69   \Desktop\flag.zi
2022-11-04 19:02:03 UTC+0000 2022-11-04 19:02:03 UTC+0000   2022-11-04 19:02:03 UTC+0000   2022-11-04 19:02:03 UTC+0000   PROGRA~2\WINDOW~2\ACCESS~1\flag.zip
0000000080: 00 20 00 00 00 00 00 00 00 66 6c 61 67 2e 74 78   .........flag.tx
2022-11-04 19:02:26 UTC+0000 2022-11-04 19:02:26 UTC+0000   2022-11-04 19:02:26 UTC+0000   2022-11-04 19:02:26 UTC+0000   Python27\tcl\tk8.5\demos\images\flagup.xbm
2022-11-04 19:02:26 UTC+0000 2022-11-04 19:02:26 UTC+0000   2022-11-04 19:02:26 UTC+0000   2022-11-04 19:02:26 UTC+0000   Python27\tcl\tk8.5\demos\images\flagdown.xbm
0000000000: 23 20 6f 70 65 72 61 74 69 6f 6e 20 66 6c 61 67   #.operation.flag
```

there is a "PROGRA~2\WINDOW~2\ACCESS~1\flag.zip" looks like the realpath.

If you have a Win7SP1x64, you could find it has only two possible result:

```
C:\Program Files (x86)\Windows NT\Accessories\flag.zip
C:\Program Files\Windows NT\Accessories\flag.zip
```

 just try it and the first is the real full path.

```
>>> path = 'C:\Program Files (x86)\Windows NT\Accessories\flag.zip'
>>> hashlib.md5(path.encode()).hexdigest()
'0d3ba7db468bdbd4f93a88c97ba7bef1'
```

use *0d3ba7db468bdbd4f93a88c97ba7bef1* to extract the *01377758.zip*, you will get the flag.

```
n1ctf{0ca175b9c0f7582931d89e2c89231599}
```

