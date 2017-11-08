import random
from equipment import Equipment, RARITY

class Character(object):
  def __init__(self):
    # Weapon, Helm, Chest, Legs, Accessory
    # TODO: Implement wand vs. sword weapons
    self.equipment = [None, None, None, None, None]
    self.stats = {"Strength": 20, "Stamina": 20, "Defense": 20, "Speed": 20,
                  "Intellect": 20, "Magic Defense": 20}
    self.gold = 100
    self.name = "Hero?"
    # TODO: Have separate HP that stamina adds to?
    self.max_hp = 5 * self.stats["Stamina"]
    self.current_hp = self.max_hp
    self.level = 1
    self.exp = 0
    self.materials = [0] * len(RARITY)

  def make_initial_equipment(self, choice):
    for i in range(len(self.equipment)):
      self.equip(Equipment.get_new_armor(1, slot=i, require=choice))

  def __str__(self):
    pieces = []
    pieces.append("Character:\n")
    pieces.append("HP: %d / %d\n" % (self.current_hp, self.max_hp))
    pieces.append("Level: %d\n" % self.level)
    pieces.append("XP: %d / %d\n" % (self.exp, self.next_level_exp()))
    for stat in self.stats:
      pieces.append("%s: %d (%d)\n" % (stat, self.get_effective_stat(stat),
                                       self.stats[stat]))
    pieces.append("Equipment:\n")
    for piece in self.equipment:
      pieces.append(str(piece) + "\n")
    pieces.append("Materials:\n")
    if sum(self.materials) == 0:
      pieces.append("None")
    else:
      # TODO: Use function in Equipment?
      for i in xrange(len(self.materials)):
        if self.materials[i] > 0:
          pieces.append("%s: %d  " % (RARITY[i], self.materials[i]))
    pieces.append("\n")
    return "".join(pieces)

  def restore_hp(self, amount=None):
    old_current = self.current_hp
    if amount is None:
      self.current_hp = self.max_hp
    else:
      self.current_hp = min(self.max_hp, self.current_hp + amount)
    return self.current_hp - old_current

  def rest(self):
    hp_gained = self.max_hp/10
    return self.restore_hp(hp_gained)

  def apply_death(self, logs):
    logs.append("You have been defeated.")
    logs.append("You were found by a passerby, and brought back to town.")
    self.restore_hp()
    lost_gold = self.gold / 2
    logs.append("You lost %d gold" % lost_gold)
    self.gold -= lost_gold

  def get_effective_stat(self, stat):
    value = self.stats[stat]
    for piece in self.equipment:
      if piece:
        value += piece.get_stat_value(stat)
    return value

  def equip(self, item):
    slot = item.slot
    removed = self.equipment[slot]
    self.equipment[slot] = item
    # TODO: Separate function?
    new_max_hp = self.get_effective_stat("Stamina") * 5
    difference = new_max_hp - self.max_hp
    self.current_hp += max(0, difference)  # Don't lose HP for equipping
    self.max_hp = new_max_hp
    self.current_hp = min(self.current_hp, self.max_hp)  # Unless max_hp drops
    return removed

  def get_damage(self):
    # 0 is weapon
    return self.equipment[0].get_damage()

  def get_damage_type(self):
    return self.equipment[0].get_damage_type()

  def next_level_exp(self):
    # TODO: Something more "complex", lol
    return self.level * 100

  def level_up(self, logs):
    for stat in self.stats:
      increase = random.randint(1, 3)
      if increase > 0:
        self.stats[stat] += increase
        logs.append("You have gained %d %s" % (increase, stat))

  def stat_training_cost(self):
    return sum(self.stats.values())

  def train_xp(self, level, logs):
    self.gain_exp(level * 25, level, logs, level_adjust=False)

  def train_stats(self, logs):
    stat = random.choice(self.stats.keys())
    self.stats[stat] += 1
    logs.append("Gained +1 %s" % stat)

  def gain_materials(self, materials):
    for i in xrange(len(materials)):
      self.materials[i] += materials[i]

  def gain_exp(self, exp, encounter_level, logs, level_adjust=True):
    exp_gained = exp
    level_difference = encounter_level - self.level
    if level_adjust:
      exp_gained = int(exp_gained * (1.1 ** level_difference))
    self.exp += exp_gained
    logs.append("You have gained %d XP" % exp_gained)
    while self.exp >= self.next_level_exp():
      self.exp -= self.next_level_exp()
      self.level += 1
      logs.append("You have reached level %d!" % self.level)
      self.level_up(logs)
