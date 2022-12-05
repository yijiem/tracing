#include "util.h"

#include <string.h>

#include <fstream>
#include <iostream>
#include <ostream>

constexpr char kProcSelfMaps[] = "/proc/self/maps";

void PrintSelfMemoryMap() {
  std::ifstream in_file(kProcSelfMaps);
  if (!in_file) {
    return;
  }
  char buf[1024];
  while (!in_file.eof()) {
    std::streamsize n = sizeof(buf);
    memset(buf, 0, n);
    in_file.getline(buf, n);
    if (!in_file.eof() && in_file.fail()) {
      return;
    }
    std::cout << buf << std::endl;
  }
}
