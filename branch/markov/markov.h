#ifndef BRANCH_MARKOV_MARKOV_H
#define BRANCH_MARKOV_MARKOV_H

#include <unordered_map>

#include "address.h"
#include "modules.h"

class markov : champsim::modules::branch_predictor {
  [[nodiscard]] static constexpr auto hash(champsim::address ip) { return ip.to<unsigned long>() % PRIME; }
  static constexpr std::size_t TABLE_SIZE = 16384;
  static constexpr std::size_t PRIME = 16381;

  struct markov_freqs {
    uint32_t n_taken = 1;
    uint32_t n_not_taken = 1;
  };

  std::array<markov_freqs, TABLE_SIZE> markov_table;

public:
  using branch_predictor::branch_predictor;

  bool predict_branch(champsim::address ip);
  void last_branch_result(champsim::address ip, champsim::address branch_target, bool taken, uint8_t branch_type);
};

#endif // BRANCH_MARKOV_MARKOV_H
