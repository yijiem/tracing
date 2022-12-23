#!/usr/bin/env python3

import os
import subprocess
import sys

DEBUG = False
PLACEHOLDER = "<placeholder>"

base_mmap = dict()
end_mmap = dict()


def build_mmap(line: str):
    # module such as [vdso] needs to be filtered
    if os.path.exists(line.split()[-1]):
        # build memory map <module load address> -> <module filepath>
        base_mmap[line.split()[0].split("-")[0]] = line.split()[-1]
        end_mmap[line.split()[0].split("-")[1]] = line.split()[-1]


def slow():
    """slow option

    Read input line by line and call to addr2line for each potential addresses. Pass through everything else.

    This option is very slow due to many addr2line runs.
    """
    for line in sys.stdin:
        if "r-xp" in line:
            build_mmap(line)
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
                        "addr2line -i -e %s -f -C -p %s" % (v1[1], hex(offset)),
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


def fast():
    """fast option

    Read input line by line, build list of addresses and exes and put a placeholder for each address in the original content.
    Then sweep and merge addresses for the same exe and call addr2line for all addresses in an exe.

    This option is fast since it drastically reduces the number of addr2line call.
    """
    content = ""
    addresses = []
    exes = []
    for line in sys.stdin:
        if "r-xp" in line:
            build_mmap(line)
            content += line
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
                # Skip libc.so.6 for now to save some hassle.
                # TODO: do not skip when symbolicating libc is supported
                if v1[1] == v2[1] and "libc.so.6" not in v1[1]:
                    offset = int(addr, 16) - int(v1[0], 16)
                    addresses.append(hex(offset))
                    exes.append(v1[1])
                    # replace the line with a placeholder
                    content += PLACEHOLDER
                else:
                    # unknown address
                    content += line
            else:
                content += line
        else:
            content += line

    assert len(addresses) == len(exes)
    # hopefully one big addr2line!
    prev = ""
    addr = ""
    for i in range(len(addresses)):
        if not prev:
            prev = exes[i]
            addr = addresses[i]
        elif exes[i] != prev:
            # fire up one and capture result
            cp = subprocess.run(
                "addr2line -e %s -f -C -p %s" % (prev, addr),
                shell=True,
                check=True,
                capture_output=True,
                encoding="utf-8",
            )
            prev = exes[i]
            addr = addresses[i]
            for line in cp.stdout.splitlines(keepends=True):
                content = content.replace(PLACEHOLDER, line, 1)
            if DEBUG:
                print(cp.args)
                print(cp.stdout)
        else:
            addr = addr + " " + addresses[i]

    if addr:
        cp = subprocess.run(
            "addr2line -e %s -f -C -p %s" % (prev, addr),
            shell=True,
            check=True,
            capture_output=True,
            encoding="utf-8",
        )
        for line in cp.stdout.splitlines(keepends=True):
            content = content.replace(PLACEHOLDER, line, 1)
        if DEBUG:
            print(cp.args)
            print(cp.stdout)

    # finally
    print(content)


def Main(args):
    fast()


if __name__ == "__main__":
    Main(sys.argv)
