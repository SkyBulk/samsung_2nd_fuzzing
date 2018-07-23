#include <stdint.h>
#include <stdio.h>
#include <sanitizer/coverage_interface.h>

extern "C" void __sanitizer_cov_trace_pc_guard_init(uint32_t *start,
                                                    uint32_t *stop) {
  static uint64_t N;
  if (start == stop || *start) return;
  printf("INIT: %p %p\n", start, stop);
  for (uint32_t *x = start; x < stop; x++)
    *x = ++N;
}

extern "C" void __sanitizer_cov_trace_pc_guard(uint32_t *guard) {
  if (!*guard) return;
  void *PC = __builtin_return_address(0);
  char PcDescr[1024];
  __sanitizer_symbolize_pc(PC, "%p %F %L", PcDescr, sizeof(PcDescr));
  printf("guard: %p %x PC %s\n", guard, *guard, PcDescr);
}