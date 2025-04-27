#include "markov_probable.h"

bool markov_probable::predict_branch(champsim::address ip) {
  auto &entry = markov_table[hash(ip)];
  double total = entry.n_taken + entry.n_not_taken;
  double probability = static_cast<double>(entry.n_taken) / total;
  return dis(gen) < probability;
}

void markov_probable::last_branch_result(champsim::address ip, champsim::address branch_target, bool taken, uint8_t branch_type) {
  auto &entry = markov_table[hash(ip)];
  if (taken) {
    ++entry.n_taken;
  }
  else {
    ++entry.n_not_taken;
  }
}