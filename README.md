# tracing

## Issues:

1. Due to https://github.com/iovisor/bpftrace/issues/246, if the tracee exits first then the stacktrace would not be symbolicated by bpftrace.

   Current plan is to use an offline approach:

   - print the `/proc/self/maps` as provided by [util.h](util.h) at the start of the tracee program
   - calculate the relative file offset of the instruction by doing `<instruction address> - <module load address>`
   - use something like `addr2line -a -e <binary> -f -C <offset>` to translate the offset into function name, file and line number.

   [symbolizer.py](symbolizer.py) has basic support for this, it still has some issues though.
