#include "plru.h"
#include <cassert>
#include <cmath>

plru::plru(CACHE* cache) : plru(cache, cache->NUM_SET, cache->NUM_WAY) {}

plru::plru(CACHE* cache, long sets, long ways)
  : replacement(cache),
    NUM_WAY(ways),
    plru_bits(static_cast<std::size_t>(sets), 0),
    plru_sizes(static_cast<std::size_t>(sets), static_cast<uint32_t>(ways - 1)) {
  assert((ways & (ways - 1)) == 0 && "power of 2 required");
}

long plru::find_victim(uint32_t triggering_cpu, uint64_t instr_id, long set,
                       const champsim::cache_block* current_set, champsim::address ip,
                       champsim::address full_addr, access_type type) {
  uint32_t tree = plru_bits[set];
  int idx = 0;

  while (idx < NUM_WAY - 1) {
    bool direction = (tree >> idx) & 1;
    idx = 2 * idx + 1 + direction;
  }

  return idx - (NUM_WAY - 1);
}

void plru::replacement_cache_fill(uint32_t triggering_cpu, long set, long way,
                                  champsim::address full_addr, champsim::address ip,
                                  champsim::address victim_addr, access_type type) {}

void plru::update_replacement_state(uint32_t triggering_cpu, long set, long way,
                                    champsim::address full_addr, champsim::address ip,
                                    champsim::address victim_addr, access_type type, uint8_t hit) {
  if (!hit && access_type{type} == access_type::WRITE) {
    return;
  }

  auto idx = static_cast<int32_t>(way + NUM_WAY - 1);
  while (idx > 0) {
    int32_t parent = (idx - 1) / 2;

    bool is_right = (idx % 2 == 1);
    if (is_right) {
        plru_bits[set] |= (1U << parent);
    }
    else {
        plru_bits[set] &= ~(1U << parent);
    }

    idx = parent;
  }
}
