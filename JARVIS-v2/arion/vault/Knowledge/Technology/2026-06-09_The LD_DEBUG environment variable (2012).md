---
title: "The LD_DEBUG environment variable (2012)"
source: https://bnikolic.co.uk/blog/linux-ld-debug.html
date: 2026-06-09
tags:
  - news
  - auto-learning
  - auto-injected
---

# The LD_DEBUG environment variable (2012)

Originally published 23 April 2012, updated 10 September 2019 (add link to troubleshooting tool), updated 18 October 2019 (moved to Jekyll), updated 3 April 2023 with links to other tools
Development of large systems using many shared (dynamically) loaded libraries can sometimes lead to some frustrating bugs that are difficult to diagnose. These bugs often arise because there a few different versions of libraries on the system and the “wrong” version gets loaded instead of the one the developer used wanted.
Note You may also find of use my online tool for diagnosing linker problems on Linux implemented as an expert system. It is being expanded at the time of writing this but probably useful already.
I used to often debug these problems reasonably efficiently using the
strace
command (man strace)
and checking which libraries are getting accessed. However, there is a
much more efficient but perhaps not very well known way of debugging
shared library loading problems: the LD_DEBUG
environment
variable.
If the LD_DEBUG
variable is set then the Linux dynamic linker will
dump debug information which can be used to resolve most loading
problems very quickly. To see the available options just run any
program with the variable set to help
, i.e.:
LD_DEBUG=help cat
Valid options for the LD_DEBUG environment variable are:
libs display library search paths
reloc display relocation processing
files display progress for input file
symbols display symbol table processing
bindings display information about symbol binding
versions display version dependencies
all all previous options combined
statistics display relocation statistics
unused determined unused DSOs
help display this help message and exit
To direct the debugging output into a file instead of standard output
a filename can be specified using the LD_DEBUG_OUTPUT environment
variable.
Note There are many other useful tools to deal with linking issues:
- The
strace
program provides insight into all system calls, including searching, opening dynamic libraries- The
ldd
program resolves dynamic library dependencies- The
objdump -x YOURFILE | grep NEEDED
command lists the records in the program or library showing which other libraries are needed- The
patchelf
program makes it easy to change therpath
of an ELF executable, changing the built-in search order- The
LD_PRELOAD
environment allows easy substitution of dynamic librariesNeed further advice? With over 20 years of experience we are uniquely placed to help – contact us at webs@bnikolic.co.uk
Note This variable is available Linux only. On MS Windows similar information can be obtained by enabling “Show Loader Snaps” (https://abitofscotland.wordpress.com/2019/12/20/dll-load-failure/) using the
gflags.exe
program to enable this and then usingwindbg
to view the log. For example:
- Install Windows SDK for
gflags
andwindbg
winget install Microsoft.WindowsSDK.10.0.19041
(or download from Microsoft website )- Enable ShowLoaderSnaps for an executable. Example: to enable for
notepad.exe
for example do in Powershell&"C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\gflags.exe" /i notepad.exe +sls
- Execute
notepad.exe
under WinDbg app. Detailed DLL loading log will be displayed
And here is an example run on my laptop:
LD_DEBUG=all cat
28504:
28504: file=libc.so.6 [0]; needed by cat [0]
28504: find library=libc.so.6 [0]; searching
28504: search path=/home/bnikolic/s/lib/tls/x86_64:/home/bnikolic/s/lib/tls:/home/bnikolic/s/lib/x86_64:/home/bnikolic/s/lib:tls/x86_64:tls:x86_64::/home/bnikolic/d/p/R-2.14.1bin/lib/R/lib/tls/x86_64:/home/bnikolic/d/p/R-2.14.1bin/lib/R/lib/tls:/home/bnikolic/d/p/R-2.14.1bin/lib/R/lib/x86_64:/home/bnikolic/d/p/R-2.14.1bin/lib/R/lib (LD_LIBRARY_PATH)
28504: trying file=/home/bnikolic/s/lib/tls/x86_64/libc.so.6
28504: trying file=/home/bnikolic/s/lib/tls/libc.so.6
28504: trying file=/home/bnikolic/s/lib/x86_64/libc.so.6
28504: trying file=/home/bnikolic/s/lib/libc.so.6
28504: trying file=tls/x86_64/libc.so.6
28504: trying file=tls/libc.so.6
28504: trying file=x86_64/libc.so.6
28504: trying file=libc.so.6
28504: trying file=/home/bnikolic/d/p/R-2.14.1bin/lib/R/lib/tls/x86_64/libc.so.6
28504: trying file=/home/bnikolic/d/p/R-2.14.1bin/lib/R/lib/tls/libc.so.6
28504: trying file=/home/bnikolic/d/p/R-2.14.1bin/lib/R/lib/x86_64/libc.so.6
28504: trying file=/home/bnikolic/d/p/R-2.14.1bin/lib/R/lib/libc.so.6
28504: search cache=/etc/ld.so.cache
28504: trying file=/lib/x86_64-linux-gnu/libc.so.6
28504:
28504: file=libc.so.6 [0]; generating link map
28504: dynamic: 0x00007fc38e525b40 base: 0x00007fc38e18c000 size: 0x00000000003a0368
28504: entry: 0x00007fc38e1ad420 phdr: 0x00007fc38e18c040 phnum: 10
28504:
28504: checking for version `GLIBC_2.4' in file /lib/x86_64-linux-gnu/libc.so.6 [0] required by file cat [0]
28504: checking for version `GLIBC_2.3' in file /lib/x86_64-linux-gnu/libc.so.6 [0] required by file cat [0]
28504: checking for version `GLIBC_2.3.4' in file /lib/x86_64-linux-gnu/libc.so.6 [0] req

---
*Synthesized by AutonomousLearner*
