#include "markov.h"

bool markov::predict_branch(champsim::address ip) {
  auto &entry = markov_table[hash(ip)];
  return entry.n_taken > entry.n_not_taken;
}

void markov::last_branch_result(champsim::address ip, champsim::address branch_target, bool taken, uint8_t branch_type) {
  auto &entry = markov_table[hash(ip)];
  if (taken) {
    ++entry.n_taken;
  }
  else {
    ++entry.n_not_taken;
  }
}

