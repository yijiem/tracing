# grpc-bpftrace

## Issues:

1. Due to https://github.com/iovisor/bpftrace/issues/246, if the tracee exits first then the stacktrace would not be symbolicated by bpftrace.

   Current plan is to use an offline approach:

   - print the `/proc/self/maps` as provided by [util.h](util.h) at the start of the tracee program
   - calculate the relative offset of the instruction in the .text section by doing `<instruction address> - <module load address>`
   - use something like `addr2line -a -e <binary> -j .text -f -C <offset>` to figure out the symbol

   UPDATE: this seems to work now, an automated script should come next.
