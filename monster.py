from equipment import Equipment
from effect import Debuff, Effect
from platform import is_browser, nl

STAT_ORDER = ["Strength", "Intellect", "Speed", "Stamina", "Defense",
              "Magic Defense"]

# TODO: Should Monster and Character subclass from something?
CHANCE_TIERS = {1: [0.0, 0.100, 0.050, 0.010, 0.001],
                2: [0.0, 0.200, 0.100, 0.030, 0.010],
                3: [0.0, 0.300, 0.150, 0.060, 0.025]}
RUNE_CHANCES = {1: 0.002, 2: 0.01, 3: 0.02}

STAT_DICE = {"Strength": (12, 1),
             "Defense": (12, 1),
             "Magic Defense": (12, 1),
             "Intellect": (12, 1),
             "Speed": (12, 1),
             "Stamina": (10, 1)}

class Monster(object):

  def __init__(self, game, level, boss, infinity_dungeon=False, stronghold=0,
               rune_world=False):
    self.game = game
    self.stats = {}
    self.level = level
    self.boss = boss

    # TEMP: Initialize monster with a random image, for testing.
    fame_monster = "https://upload.wikimedia.org/wikipedia/commons/d/de/Ladygaga.jpg"
    cute_monster = "https://upload.wikimedia.org/wikipedia/commons/2/28/PEO-monster.svg"
    energy_monster = "https://upload.wikimedia.org/wikipedia/commons/6/69/Lata_de_Monster_Energy.jpg"
    spaghetti_monster = "https://upload.wikimedia.org/wikipedia/commons/3/30/Flying_Spaghetti_Monster.svg"
    monsters = [fame_monster, cute_monster, energy_monster, spaghetti_monster]
    self.image = monsters[game.rng.randint(0, len(monsters) - 1)]

    # If you modify these, make sure to modify the XP calc
    for stat in STAT_DICE.keys():
      die, modifier = STAT_DICE[stat]
      self.stats[stat] = self.roll_stat(die, modifier)
    if boss:
      for stat in self.stats.keys():
        self.stats[stat] = self.stats[stat] * 1.3
      self.stats["Stamina"] *= 4   # Effectively x5.2
    for stat in self.stats.keys():
      # 75-125% change
      self.stats[stat] *= (game.rng.random() * 0.5) + 0.75
      self.stats[stat] = int(self.stats[stat])
      self.stats[stat] = max(1, self.stats[stat])
    if not infinity_dungeon and not stronghold and not rune_world:
      self.set_type()
    else:
      self.monster_type = "None"
    self.set_image(stronghold, infinity_dungeon or rune_world)
    self.max_hp = self.stats["Stamina"] * 5
    self.current_hp = self.max_hp
    if boss:
      self.name = "{} (Level {} Elite)".format(self.game.name_gen.generate_name(),
                                           self.level)
    else:
      self.name = "{} (Level {})".format(self.game.name_gen.generate_name(), self.level)
    self.traits = {}
    self.buffs = []
    self.debuffs = []

  def set_type(self):
    self.stats["Tank"] = (self.stats["Defense"] + self.stats["Magic Defense"]) / 2
    best = 0
    best_stat = None
    for stat in ("Tank", "Strength", "Intellect", "Speed"):
      if self.stats[stat] > best:
       best_stat = stat
       best = self.stats[stat]
    del self.stats["Tank"]
    self.monster_type = best_stat
    for stat in self.stats:
      self.stats[stat] = int(self.stats[stat] * .95)
      self.stats[stat] = max(1, self.stats[stat])
    if self.monster_type == "Tank":
      self.stats["Magic Defense"] = int(self.stats["Magic Defense"] * 1.20)
      self.stats["Defense"] = int(self.stats["Defense"] * 1.20)
    else:
      self.stats[best_stat] = int(self.stats[best_stat] * 1.20)

        # Start here: set self.monster_type
        #             Implement set_image
        #             Make sure infinity_dungeon and stronghold are hooked in

  def set_image(self, stronghold, random_monster=False):
    if stronghold:
      self.image = "boss" + str(stronghold)
      return
    elif random_monster:
      tier = self.game.rng.randint(1, 8)
      image_type = self.game.rng.choice(["Tank", "Intellect", "Speed", "Strength"])
    else:
      tier = int(self.game.rng.gauss(0, .5) + (self.level / 5) + 1)
      if tier > 8: tier = 8
      if tier < 1: tier = 1
      image_type = self.monster_type
    self.image = "t" + str(tier) + image_type

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
    # TODO: Mark elites somehow
    if is_browser:
      pieces.append(nl(nl("<img class=\"monster\" src=\"" + self.image + "\">")));
    pieces.append(nl("Name: {}").format(self.name))
    if libra_level == 0:
      pieces.append(nl("HP: {}").format(self.hp_string()))
    else:
      pieces.append(nl("HP: {} / {}").format(self.current_hp, self.max_hp))
    pieces.append("Debuffs: ")
    pieces.append(", ".join(str(debuff) for debuff in self.debuffs))
    if self.debuffs:
      pieces.append(nl())
    else:
      pieces.append(nl("None"))
    if libra_level > 0:
      for stat in STAT_ORDER:
        pieces.append("{}: {} ({})  ".format(stat, self.get_effective_stat(stat),
                                         self.stats[stat]))
        pieces.append(nl())
    pieces.append("Image: {}".format(self.image))
    return "".join(pieces)

  def __str__(self):
    pieces = []
    pieces.append(nl("Name: {}").format(self.name))
    pieces.append(nl("HP: {}").format(self.hp_string()))
    pieces.append("Debuffs: ")
    pieces.append(", ".join(str(debuff) for debuff in self.debuffs))
    if self.debuffs:
      pieces.append(nl())
    else:
      pieces.append(nl("None"))
    pieces.append(nl("***DEBUG***"))
    for stat in self.stats.keys():
      pieces.append("{}: {} ({})  ".format(stat, self.get_effective_stat(stat),
                                       self.stats[stat]))
      pieces.append(nl())
    pieces.append(nl("stats: {0!r}").format(self.stats))
    pieces.append(nl("HP: {} / {}").format(self.current_hp, self.max_hp))
    pieces.append(nl("XP value: {}").format(self.calculate_exp()))
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
    treasure.append(self.game.rng.randint(min_gold, max_gold))
    treasure_tier = 1
    treasure_tier += (1 if self.boss else 0)
    treasure_tier += (1 if infinity else 0)
    chances = CHANCE_TIERS[treasure_tier]
    for rarity in range(1, len(chances)):
      while self.game.rng.random() < chances[rarity]:
        treasure.append(Equipment.get_new_gear(self.game, self.level, None, None, rarity))
    if rune_world:
      rune_chance = 0.0
    else:
      rune_chance = RUNE_CHANCES[treasure_tier]
    while self.game.rng.random() < rune_chance:
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
    return self.game.rng.randint(low, high)

  def get_damage_type(self):
    if (self.get_effective_stat("Intellect") >
        self.get_effective_stat("Strength")):
      return "Magic"
    else:
      return "Physical"

  def roll_stat(self, die, modifier):
    return sum(self.game.rng.randint(1, die) + modifier for _ in range(self.level))

  def get_action(self, character):
    # Monster AI
    # TODO: Something more sophisticated, especially for special monsters
    return ("Attack", None)
