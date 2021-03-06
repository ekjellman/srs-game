from plat import nl
from util import pd, pf1

# TODO: Make stats always be in a specific order [OrderedDict or array]
# TODO: Should probably move these to a different place
STATS = ["Strength", "Stamina", "Speed", "Intellect"]
DEFENSES = ["Defense", "Magic Defense"]
SLOTS = ["Weapon", "Hat", "Shirt", "Pants", "Accessory"]
RARITY = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
RARITY_COLORS = ["rgb(160,160,160)", "rgb(0,160,0)", "rgb(0,0,160)", "rgb(160,0,160)",
                 "rgb(255,140,0)"]
ABBREVIATIONS = {"Defense": "Def",
                 "Magic Defense": "MDef"}
WEAPON_STATS = ["Low", "High", "Type"]

class Equipment(object):
  def __init__(self, game, item_level, attributes, slot, rarity):
    self.game = game
    # int, power level of the item
    self.item_level = item_level
    # dictionary from attribute -> value
    self.attributes = attributes
    # Common / Uncommon / Rare / Epic / Legendary
    self.rarity = rarity
    # 0-4, Weapon, Hat, Shirt, Pants, Accessory
    self.slot = slot
    self.enchant_count = 0
    self.reforge_count = 0

  def stat_score(self):
    # Primarily for tests
    score = 0
    for attribute in self.attributes.keys():
      if attribute in WEAPON_STATS: continue
      score += self.attributes[attribute]
    if self.slot == 0:
      score += (self.attributes["Low"] + self.attributes["High"] / 2)
    return score

  @staticmethod
  def equipment_comparison_text(current, new):
    pieces = []
    pieces.append(nl("Current Equipment:"))
    pieces.append(str(current))
    pieces.append(nl() + nl("New Equipment:"))
    pieces.append(str(new))
    pieces.append(nl() + nl("Comparison:"))
    pieces.append(Equipment.comparison_text(current, new))
    return "".join(pieces)

  @classmethod
  def comparison_text(cls, old, new):
    assert old.slot == new.slot
    pieces = []
    # NB: We avoid union, for which Transcrypt seems to only support 1 argument.
    attributes = set(old.attributes.keys())
    attributes.update(new.attributes.keys())
    for attr in attributes:
      if attr not in STATS and attr not in DEFENSES:
        continue
      old_attribute = old.attributes.get(attr, 0) if attr in old.attributes else 0
      new_attribute = new.attributes.get(attr, 0) if attr in new.attributes else 0
      difference = new_attribute - old_attribute
      if difference != 0:
        color_string = "rgb(255,0,0)" if difference < 0 else "rgb(0,160,0)"
        pieces.append("<span style=\"color: {}\">{} {}</span>".format(color_string, pd(difference), attr))
    if old.slot == 0:
      old_average = (old.attributes.get("Low", 0) + old.attributes.get("High", 0)) / 2.0
      new_average = (new.attributes.get("Low", 0) + new.attributes.get("High", 0)) / 2.0
      difference = new_average - old_average
      color = "rgb(255,0,0)" if difference < 0 else "rgb(0,160,0)"
      pieces.append("<span style=\"color: {}\">{} average damage</span>".format(color, pf1(difference)))
      if old.attributes.get("Type", 0) != new.attributes.get("Type", 0):
        pieces.append("Weapon type change")
    return nl().join(pieces)

  def enchant(self):
    self.enchant_count += 1
    enchanted_stat = self.game.rng.choice(STATS)
    amount = self.game.rng.randint(max(1, self.item_level // 4),
                            max(1, self.item_level // 2))
    amount = int(amount * (1.0 + 0.25 * self.rarity))
    self.attributes[enchanted_stat] = self.attributes.get(enchanted_stat, 0) + amount
    return "{} {}".format(pd(amount), enchanted_stat)

  def get_stat_value(self, stat):
    return self.attributes.get(stat, 0)

  def reforge(self, level):
    result_pieces = []
    # Stats
    max_gains = (self.rarity + 1) * (level - self.item_level)
    stat_gains = [0, 0, 0, 0]
    for _ in range(max_gains):
      stat_gains[self.game.rng.randint(0, 3)] += 1
    for i in range(4):
      stat_gains[i] = self.game.rng.randint(stat_gains[i] // 2, stat_gains[i])
      self.attributes[STATS[i]] = self.attributes.get(STATS[i], 0) + stat_gains[i]
      if stat_gains[i] > 0:
        result_pieces.append("{} {}".format(pd(stat_gains[i]), STATS[i]))
    # Defenses
    max_gains = 2 * (level - self.item_level)
    def_gains = [0, 0]
    for _ in range(max_gains):
      def_gains[self.game.rng.randint(0, 1)] += 1
    for i in range(2):
      def_gains[i] = self.game.rng.randint(def_gains[i] // 2, def_gains[i])
      self.attributes[DEFENSES[i]] = self.attributes.get(DEFENSES[i], 0) + def_gains[i]
      if def_gains[i] > 0:
        result_pieces.append("{} {}".format(pd(def_gains[i]), DEFENSES[i]))
    # Weapon Stats
    if self.slot == 0:
      rarity_factor = 1.0 + (.1 * self.rarity)
      low = int((10 + 5 * level) * self.game.rng.gauss(1, .2) * rarity_factor)
      high = int((20 + 7 * level) * self.game.rng.gauss(1, .2) * rarity_factor)
      old_low = self.attributes.get("Low", 0)
      old_high = self.attributes.get("High", 0)
      old_average = (old_low + old_high) / 2.0
      new_low = max(low, old_low)
      new_high = max(high, old_high)
      if new_low > new_high:
        new_low, new_high = new_high, new_low
      new_average = (new_low + new_high) / 2.0
      difference = new_average - old_average
      if difference > 0:
        result_pieces.append("{} average damage".format(pf1(difference)))
      self.attributes["Low"] = new_low
      self.attributes["High"] = new_high
    self.reforge_count += 1
    self.item_level = level
    return " ".join(result_pieces)

  @classmethod
  def make_stat_value(cls, game, item_level, rarity):
    min_stat = max(1, item_level // 2)
    max_stat = min_stat + item_level + rarity
    return game.rng.randint(min_stat, max_stat)

  def get_damage(self):
    return self.game.rng.randint(self.attributes.get("Low", 0), self.attributes.get("High", 0))

  def get_damage_type(self):
    return self.attributes.get("Type", 0)

  def get_recycled_materials(self):
    materials = [0] * len(RARITY) # __:opov
    count = 0
    for _ in range(self.item_level):
      if self.game.rng.random() > .85 ** count:
        continue
      rarity = int(self.rarity + self.game.rng.gauss(0, 1))
      if rarity < 0:
        continue
      if rarity >= len(RARITY):
        rarity = len(RARITY) - 1
      materials[rarity] += 1
      count += 1
    return materials

  @classmethod
  def materials_string(cls, materials):
    pieces = []
    for i in range(len(materials)):
      if materials[i] > 0:
        pieces.append("{} {} materials".format(materials[i], RARITY[i]))
    if pieces:
      return ", ".join(pieces)
    else:
      return "no materials"

  def get_value(self):
    value = self.item_level * 25
    # __pragma__ ('opov')
    for attribute in STATS + DEFENSES:
      value += self.attributes.get(attribute, 0) ** 2
    # __pragma__ ('noopov')
    value *= max(1, self.rarity - 1)
    if self.slot == 0:  # Weapon
      average_damage = (self.attributes.get("Low", 0) + self.attributes.get("High", 0)) / 2
      value += average_damage
    return value

  @classmethod
  def get_new_gear(cls, game, item_level, slot=None, require=None, rarity=1):
    attributes = {}
    if slot is None:
      slot = game.rng.randint(0, len(SLOTS) - 1)
    slots = 1 + rarity
    if require:
      attributes[require] = cls.make_stat_value(game, item_level, rarity)
      slots -= 1
    for _ in range(slots):
      stat = game.rng.choice(STATS)
      attributes[stat] = attributes.get(stat, 0) + cls.make_stat_value(game, item_level, rarity)
    for defense in DEFENSES:
      attributes[defense] = cls.make_stat_value(game, item_level, rarity)
    if SLOTS[slot] == "Weapon":
      rarity_factor = 1.0 + (.1 * rarity)
      low = int((10 + 5 * item_level) * game.rng.gauss(1, .2) * rarity_factor)
      high = int((20 + 7 * item_level) * game.rng.gauss(1, .2) * rarity_factor)
      if low > high:
        low, high = high, low
      if low < 1:
        low = 1
      attributes["Low"] = low
      attributes["High"] = high
      if require == "Strength":
        attributes["Type"] = "Physical"
      elif require == "Intellect":
        attributes["Type"] = "Magic"
      else:
        attributes["Type"] = game.rng.choice(("Magic", "Physical"))
    return Equipment(game, item_level, attributes, slot, rarity)

  def __str__(self):
    pieces = []
    pieces.append(SLOTS[self.slot])
    pieces.append(": ")
    pieces.append("<span style=\"color: {}\">".format(RARITY_COLORS[self.rarity]))
    # __pragma__ ('opov')
    pieces.append("({}{} {}) ".format(self.item_level,
                                  "*" * self.enchant_count,
                                  RARITY[self.rarity][0]))
    # __pragma__ ('noopov')
    if SLOTS[self.slot] == "Weapon":
      pieces.append("({} {}-{}) ".format(self.attributes.get("Type", 0),
                                     self.attributes.get("Low", 0),
                                     self.attributes.get("High", 0)))
    defense_pieces = []
    stat_pieces = []
    for attr in self.attributes.keys():
      if attr in STATS:
        if self.attributes.get(attr, 0) > 0:
          stat_pieces.append("{} {}".format(pd(self.attributes.get(attr, 0)), attr))
      elif attr in DEFENSES:
        defense_pieces.append("{} {}".format(self.attributes.get(attr, 0),
                                         ABBREVIATIONS[attr]))
      else:
        assert attr in WEAPON_STATS
    pieces.append("({}) ".format(" / ".join(defense_pieces)))
    pieces.append(" ".join(stat_pieces))
    pieces.append("</span>")
    return "".join(pieces)
