import srs_random
from equipment import Equipment
from effect import Debuff, Effect
from name_generator import NameGenerator

STAT_ORDER = ["Strength", "Intellect", "Speed", "Stamina", "Defense",
              "Magic Defense"]

# TODO: Should Monster and Character subclass from something?
CHANCE_TIERS = {1: [0.0, 0.100, 0.050, 0.010, 0.001],
                2: [0.0, 0.200, 0.100, 0.030, 0.010],
                3: [0.0, 0.300, 0.150, 0.060, 0.025]}
RUNE_CHANCES = {1: 0.002, 2: 0.01, 3: 0.02}

NAME_GENERATOR = NameGenerator("monsters.txt", "banned.txt")

STAT_DICE = {"Strength": (12, 1),
             "Defense": (12, 1),
             "Magic Defense": (12, 1),
             "Intellect": (12, 1),
             "Speed": (12, 1),
             "Stamina": (10, 1)}

class Monster(object):
  def __init__(self, level, boss):
    self.stats = {}
    self.level = level
    self.boss = boss
    # If you modify these, make sure to modify the XP calc
    for stat in STAT_DICE.keys():
      die, modifier = STAT_DICE[stat]
      self.stats[stat] = self.roll_stat(self.level, die, modifier)
    if boss:
      for stat in self.stats.keys():
        self.stats[stat] = self.stats[stat] * 1.3
      self.stats["Stamina"] *= 4   # Effectively x5.2
    for stat in self.stats.keys():
      # 75-125% change
      self.stats[stat] *= (srs_random.random() * 0.5) + 0.75
      self.stats[stat] = int(self.stats[stat])
      self.stats[stat] = max(1, self.stats[stat])
    self.max_hp = self.stats["Stamina"] * 5
    self.current_hp = self.max_hp
    if boss:
      self.name = "{} (Level {} Elite)".format(NAME_GENERATOR.generate_name(),
                                           self.level)
    else:
      self.name = "{} (Level {})".format(NAME_GENERATOR.generate_name(), self.level)
    self.traits = {}
    self.buffs = []
    self.debuffs = []

  def hp_string(self):
    percent = int(100 * self.current_hp // self.max_hp)
    return "{}%".format(percent)

  def pass_time(self, amount):
    remaining_debuffs = []
    for debuff in self.debuffs:
      debuff.pass_time(amount)
      if debuff.active():
        remaining_debuffs.append(debuff)
    self.debuffs = remaining_debuffs

  def add_debuff(self, new_debuff):
    Debuff.add_debuff(self.debuffs, new_debuff)

  def libra_string(self, libra_level):
    pieces = []
    pieces.append("Name: {}\n".format(self.name))
    if libra_level == 0:
      pieces.append("HP: {}\n".format(self.hp_string()))
    else:
      pieces.append("HP: {} / {}\n".format(self.current_hp, self.max_hp))
    pieces.append("Debuffs: ")
    pieces.append(", ".join(str(debuff) for debuff in self.debuffs))
    if self.debuffs:
      pieces.append("\n")
    else:
      pieces.append("None\n")
    if libra_level > 0:
      for stat in STAT_ORDER:
        pieces.append("{}: {} ({})  ".format(stat, self.get_effective_stat(stat),
                                         self.stats[stat]))
        pieces.append("\n")
    return "".join(pieces)

  def __str__(self):
    pieces = []
    pieces.append("Name: {}\n".format(self.name))
    pieces.append("HP: {}\n".format(self.hp_string()))
    pieces.append("Debuffs: ")
    pieces.append(", ".join(str(debuff) for debuff in self.debuffs))
    if self.debuffs:
      pieces.append("\n")
    else:
      pieces.append("None\n")
    pieces.append("***DEBUG***\n")
    for stat in self.stats.keys():
      pieces.append("{}: {} ({})  ".format(stat, self.get_effective_stat(stat),
                                       self.stats[stat]))
      pieces.append("\n")
    pieces.append("stats: {0!r}\n".format(self.stats))
    pieces.append("HP: {} / {}\n".format(self.current_hp, self.max_hp))
    pieces.append("XP value: {}\n".format(self.calculate_exp()))
    return "".join(pieces)

  def calculate_exp(self):
    effective_level = 0
    for stat in STAT_DICE.keys():
      die, modifier = STAT_DICE[stat]
      average = ((1 + die) / 2.0) + modifier
      effective_level += (self.stats[stat] / average)
    effective_level /= 6
    return int(10 * effective_level)

  def get_treasure(self, infinity=False, rune_world=False):
    # list of treasure from this monster.
    # May be int (for gold), Equipment objects, or the string "Rune"
    treasure = []
    boss_factor = 4 if self.boss else 1
    min_gold = 5 * self.level * boss_factor
    max_gold = 15 * self.level * boss_factor
    treasure.append(srs_random.randint(min_gold, max_gold))
    treasure_tier = 1
    treasure_tier += (1 if self.boss else 0)
    treasure_tier += (1 if infinity else 0)
    chances = CHANCE_TIERS[treasure_tier]
    for rarity in range(1, len(chances)):
      while srs_random.random() < chances[rarity]:
        treasure.append(Equipment.get_new_armor(self.level, None, None, rarity))
    if rune_world:
      rune_chance = 0.0
    else:
      rune_chance = RUNE_CHANCES[treasure_tier]
    while srs_random.random() < rune_chance:
      treasure.append("Rune")
    return treasure

  def get_effective_stat(self, stat):
    value = self.stats[stat]
    effect = Effect.get_combined_impact(stat, self.buffs, self.debuffs)
    value = int(value * effect)
    return value

  def get_damage(self):
    boss_factor = 1.20 if self.boss else 1.0
    low = (10 + (7 * self.level)) * boss_factor
    high = (20 + (14 * self.level)) * boss_factor
    low, high = int(low), int(high)
    return srs_random.randint(low, high)

  def get_damage_type(self):
    if (self.get_effective_stat("Intellect") >
        self.get_effective_stat("Strength")):
      return "Magic"
    else:
      return "Physical"

  @classmethod
  def roll_stat(cls, level, die, modifier):
    return sum(srs_random.randint(1, die) + modifier for _ in range(level))

  def get_action(self, character):
    # Monster AI
    # TODO: Something more sophisticated, especially for special monsters
    return ("Attack", None)
