import collections
import srs_random

class NameGenerator(object):
  def __init__(self, filename, shortest=3, longest=100):
    self.monsters = self.read_monster_list(filename)
    self.table = self.make_markov_table(self.monsters)
    self.shortest = shortest
    self.longest = longest

  def read_monster_list(self, filename):
    with open(filename, "r") as file_in:
      lines = file_in.readlines()
    monsters = []
    for line in lines:
      line = line.lower()
      line = "".join(ch for ch in line if ch == " " or ch.isalpha())
      if len(line) > 2:
        monsters.append(line)
    return set(monsters)

  def make_markov_table(self, monsters):
    table = {}
    for letter in "abcdefghijklmnopqrstuvwxyz ":
      table[letter] = collections.defaultdict(int)
    table["START"] = collections.defaultdict(int)
    for monster in monsters:
      current = "START"
      for letter in monster:
        table[current][letter] += 1
        current = letter
      table[current]["END"] += 1
    return table

  def generate_name(self):
    # Hacky and inefficient. TODO, maybe
    name = []
    current = "START"
    while current != "END":
      entry = self.table[current]
      next_letter = None
      total = 0
      for candidate in entry:
        count = entry[candidate]
        total += count
        if srs_random.randint(1, total) <= count:
          next_letter = candidate
      if next_letter == "END":
        if len(name) >= self.shortest and len(name) <= self.longest:
          return "".join(name).title()
        else:
          return self.generate_name()
      else:
        name.append(next_letter)
        current = next_letter
