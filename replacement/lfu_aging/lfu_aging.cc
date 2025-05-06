#include "lfu_aging.h"
#include <algorithm>
#include <cassert>

lfu_aging::lfu_aging(CACHE* cache) : lfu_aging(cache, cache->NUM_SET, cache->NUM_WAY) {}

lfu_aging::lfu_aging(CACHE* cache, long sets, long ways)
  : replacement(cache),
    NUM_WAY(ways),
    access_counts(static_cast<std::size_t>(sets * ways), 0)
{}

long lfu_aging::find_victim(uint32_t triggering_cpu, uint64_t instr_id, long set,
                            const champsim::cache_block* current_set, champsim::address ip,
                            champsim::address full_addr, access_type type) {
  auto begin = access_counts.begin() + set * NUM_WAY;
  auto end = begin + NUM_WAY;
  auto victim = std::min_element(begin, end);
  assert(victim != end);
  return std::distance(access_counts.begin() + set * NUM_WAY, victim);
}

void lfu_aging::replacement_cache_fill(uint32_t triggering_cpu, long set, long way,
                                       champsim::address full_addr, champsim::address ip,
                                       champsim::address victim_addr, access_type type) {
  access_counts.at((std::size_t)(set * NUM_WAY + way)) = 1;
}

void lfu_aging::update_replacement_state(uint32_t triggering_cpu, long set, long way,
                                         champsim::address full_addr, champsim::address ip,
                                         champsim::address victim_addr, access_type type, uint8_t hit) {
  std::size_t index = static_cast<std::size_t>(set * NUM_WAY + way);
  if (hit && access_type{type} != access_type::WRITE) {
    ++access_counts.at(index);
  }

  if (++global_access_counter % AGING_INTERVAL == 0) {
    for (auto& count : access_counts) {
        count >>= 1;
    }
  }
}


