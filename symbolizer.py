#!/usr/bin/env python3

import os
import subprocess
import sys

DEBUG = False

base_mmap = dict()
end_mmap = dict()


def Main(args):
    for line in sys.stdin:
        if "r-xp" in line:
            # module such as [vdso] needs to be filtered
            if os.path.exists(line.split()[-1]):
                # build memory map <module load address> -> <module filepath>
                base_mmap[line.split()[0].split("-")[0]] = line.split()[-1]
                end_mmap[line.split()[0].split("-")[1]] = line.split()[-1]
            print(line, end="")
        elif len(line.split()) == 1:
            # might be our single address line
            if line.split()[0].startswith("0x"):
                addr = line.split()[0]
                v1 = min(
                    base_mmap.items(), key=lambda i: abs(int(addr, 16) - int(i[0], 16))
                )
                v2 = min(
                    end_mmap.items(), key=lambda i: abs(int(addr, 16) - int(i[0], 16))
                )
                if v1[1] == v2[1]:
                    offset = int(addr, 16) - int(v1[0], 16)
                    cp = subprocess.run(
                        "addr2line -i -e %s -f -C -p %s"
                        % (v1[1], hex(offset)),
                        shell=True,
                        check=True,
                    )
                    if DEBUG:
                        print(cp.args)
                        print(
                            "match - addr: %s v1: %s %s v2: %s %s"
                            % (addr, v1[0], v1[1], v2[0], v2[1])
                        )
                else:
                    # unknown address
                    print(line, end="")
            else:
                print(line, end="")
        else:
            # pass through
            print(line, end="")


if __name__ == "__main__":
    Main(sys.argv)
