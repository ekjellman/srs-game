import random
import collections

# TODO: Should probably move these to a different place
STATS = ["Strength", "Stamina", "Speed", "Intellect"]
DEFENSES = ["Defense", "Magic Defense"]
SLOTS = ["Weapon", "Helm", "Chest", "Legs", "Accessory"]
RARITY = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
RARITY_COLORS = ["`160,160,160`", "`0,160,0`", "`0,0,160`", "`160,0,160`",
                 "`255,140,0`"]
ABBREVIATIONS = {"Defense": "Def",
                 "Magic Defense": "MDef"}
WEAPON_STATS = ["Low", "High", "Type"]

class Equipment(object):
  def __init__(self, item_level, attributes, slot, rarity):
    # int, power level of the item
    self.item_level = item_level
    # dictionary from attribute -> value
    self.attributes = attributes
    # Common / Uncommon / Rare / Epic / Legendary
    self.rarity = rarity
    # 0-4, Weapon, Helm, Chest, Legs, Accessory
    self.slot = slot
    # TODO: Implement damage range for weapons
    #       Figure out what is reasonable against growing monster stamina
    #       2-3 hits against a normal monster is probably about right
    self.enchant_count = 0
    self.reforge_count = 0

  @classmethod
  def comparison_text(cls, old, new):
    assert old.slot == new.slot
    pieces = []
    attributes = set().union(old.attributes, new.attributes)
    for attr in attributes:
      if attr not in STATS and attr not in DEFENSES:
        continue
      old_attribute = old.attributes[attr] if attr in old.attributes else 0
      new_attribute = new.attributes[attr] if attr in new.attributes else 0
      difference = new_attribute - old_attribute
      if difference != 0:
        color_string = "`255,0,0`" if difference < 0 else "`0,160,0`"
        pieces.append("%s%+d %s" % (color_string, difference, attr))
    if old.slot == 0:
      # TODO: Might be worth having an "Average Damage" attribute
      old_average = (old.attributes["Low"] + old.attributes["High"]) / 2.0
      new_average = (new.attributes["Low"] + new.attributes["High"]) / 2.0
      difference = new_average - old_average
      color = "`255,0,0`" if difference < 0 else "`0,160,0`"
      pieces.append("%s%+0.1f average damage" % (color, difference))
      if old.attributes["Type"] != new.attributes["Type"]:
        pieces.append("`0,0,0`Weapon type change")
    return "\n".join(pieces)

  # TODO: If we make an Enchanter shop class, these should probably move there.
  def enchant_cost_gold(self):
    return self.item_level * 25 * ((self.enchant_count + 1) ** 2)

  def enchant_cost_materials(self):
    return self.item_level * (self.enchant_count + 1) / 2

  def enchant(self):
    self.enchant_count += 1
    enchanted_stat = random.choice(STATS)
    amount = random.randint(max(1, self.item_level / 4),
                            max(1, self.item_level / 2))
    amount = int(amount * (1.0 + 0.25 * self.rarity))
    if enchanted_stat in self.attributes:
      self.attributes[enchanted_stat] += amount
    else:
      self.attributes[enchanted_stat] = amount
    return "%+d %s" % (amount, enchanted_stat)

  def get_stat_value(self, stat):
    return self.attributes[stat]

  def reforge_cost_gold(self, level):
    return (level - self.item_level) * (25 * ((self.reforge_count + 1) ** 2))

  def reforge_cost_materials(self, level):
    return (level - self.item_level) * (self.reforge_count + 1)

  def reforgable(self, level):
    return level > self.item_level

  def reforge(self, level):
    # TODO: Fix c/p code?
    result_pieces = []
    # Stats
    max_gains = (self.rarity + 1) * (level - self.item_level)
    stat_gains = [0, 0, 0, 0]
    for _ in xrange(max_gains):
      stat_gains[random.randint(0, 3)] += 1
    for i in range(4):
      stat_gains[i] = random.randint(stat_gains[i] / 2, stat_gains[i])
      self.attributes[STATS[i]] += stat_gains[i]
      if stat_gains[i] > 0:
        result_pieces.append("%+d %s" % (stat_gains[i], STATS[i]))
    # Defenses
    max_gains = 2 * (level - self.item_level)
    def_gains = [0, 0]
    for _ in xrange(max_gains):
      stat_gains[random.randint(0, 1)] += 1
    for i in range(2):
      stat_gains[i] = random.randint(stat_gains[i] / 2, stat_gains[i])
      self.attributes[DEFENSES[i]] += stat_gains[i]
      if stat_gains[i] > 0:
        result_pieces.append("%+d %s" % (stat_gains[i], DEFENSES[i]))
    # Weapon Stats
    if self.slot == 0:
      rarity_factor = 1.0 + (.1 * self.rarity)
      low = int((10 + 5 * level) * random.gauss(1, .2) * rarity_factor)
      high = int((20 + 7 * level) * random.gauss(1, .2) * rarity_factor)
      old_low = self.attributes["Low"]
      old_high = self.attributes["High"]
      old_average = (old_low + old_high) / 2.0
      new_low = max(low, old_low)
      new_high = max(high, old_high)
      if new_low > new_high:
        new_low, new_high = new_high, new_low
      new_average = (new_low + new_high) / 2.0
      difference = new_average - old_average
      if difference > 0:
        result_pieces.append("%+0.1f average damage" % difference)
      self.attributes["Low"] = new_low
      self.attributes["High"] = new_high
    self.reforge_count += 1
    self.item_level = level
    return " ".join(result_pieces)

  @classmethod
  def make_stat_value(cls, item_level, rarity):
    # TODO: Gaussian stuff?
    min_stat = max(1, item_level / 2)
    max_stat = min_stat + item_level + rarity
    return random.randint(min_stat, max_stat)

  def get_damage(self):
    return random.randint(self.attributes["Low"], self.attributes["High"])

  def get_damage_type(self):
    return self.attributes["Type"]

  def get_recycled_materials(self):
    materials = [0] * len(RARITY)
    for _ in xrange(self.item_level):
      # Will slightly push range down due to rounding
      rarity = int(self.rarity + random.gauss(0, 1))
      if rarity < 0:
        continue
      if rarity >= len(RARITY):
        rarity = len(RARITY) - 1
      materials[rarity] += 1
    return materials

  @classmethod
  def materials_string(cls, materials):
    pieces = []
    for i in xrange(len(materials)):
      if materials[i] > 0:
        pieces.append("%d %s materials" % (materials[i], RARITY[i]))
    if pieces:
      return ", ".join(pieces)
    else:
      return "no materials"

  def get_value(self):
    value = self.item_level * 25
    for attribute in STATS + DEFENSES:
      value += self.attributes[attribute] ** 2
    value *= max(1, self.rarity - 1)
    if self.slot == 0:  # Weapon
      average_damage = (self.attributes["Low"] + self.attributes["High"]) / 2
      value += average_damage
    return value

  @classmethod
  def get_new_armor(cls, item_level, slot=None, require=None, rarity=1):
    attributes = collections.defaultdict(int)
    if slot is None:
      slot = random.randint(0, len(SLOTS) - 1)
    slots = 1 + rarity
    if require:
      attributes[require] = cls.make_stat_value(item_level, rarity)
      slots -= 1
    for _ in range(slots):
      attributes[random.choice(STATS)] += cls.make_stat_value(item_level,
                                                              rarity)
    for defense in DEFENSES:
      attributes[defense] = cls.make_stat_value(item_level, rarity)
    if SLOTS[slot] == "Weapon":
      rarity_factor = 1.0 + (.1 * rarity)
      low = int((10 + 5 * item_level) * random.gauss(1, .2) * rarity_factor)
      high = int((20 + 7 * item_level) * random.gauss(1, .2) * rarity_factor)
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
        attributes["Type"] = random.choice(("Magic", "Physical"))
    return Equipment(item_level, attributes, slot, rarity)

  def __str__(self):
    pieces = []
    pieces.append(SLOTS[self.slot])
    pieces.append(": ")
    pieces.append(RARITY_COLORS[self.rarity])
    pieces.append("(%d %s) " % (self.item_level, RARITY[self.rarity][0]))
    if SLOTS[self.slot] == "Weapon":
      pieces.append("(%s %d-%d) " % (self.attributes["Type"],
                                     self.attributes["Low"],
                                     self.attributes["High"]))
    defense_pieces = []
    stat_pieces = []
    for attr in self.attributes:
      if attr in STATS:
        if self.attributes[attr] > 0:
          stat_pieces.append("%+d %s " % (self.attributes[attr], attr))
      elif attr in DEFENSES:
        defense_pieces.append("%d %s" % (self.attributes[attr],
                                         ABBREVIATIONS[attr]))
      else:
        assert attr in WEAPON_STATS
    pieces.append("(%s) " % " / ".join(defense_pieces))
    pieces.append("".join(stat_pieces))
    pieces.append("`0,0,0`")
    return "".join(pieces)

if __name__ == "__main__":
  for i in xrange(5):
    equip = Equipment.get_new_armor(10, slot=i, rarity=4)
    print equip
    print equip.reforge(20)
    print equip
    print "---"
