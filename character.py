import random
import collections
import skills
from equipment import Equipment, RARITY
from effect import Effect, Buff, Debuff

STAT_ORDER = ["Strength", "Intellect", "Speed", "Stamina", "Defense",
              "Magic Defense"]

TRAITS = {"Beefy!": "Increase physical damage",
          "Wizardry": "Increase magical damage",
          "Perseverance": "Chance to survive fatal attacks in combat",
          # "Scholar": "On level up, chance to choose new skills",
          "Self-Improvement": "On level up, chance to choose new passives",
          "Quick Learner": "Improved experience gain",
          "Merchant Warrior": "Improved gold gain",
          "Clarity of Mind": "SP regeneration over time",
          "Regeneration": "HP regeneration over time",
          "Stocky!": "Reduce physical damage",
          "Mental Toughness": "Reduce magical damage",
         }


# TRAITS:
# TODO: To implement: Scholar
# TODO: There are more on the sheet
# -- Increased Stats
# -- Lightning Strike (chance to automatically go again after an attack)
# -- Dodge (chance to avoid all damage from an attack)
# -- Repeated Valor (chance to have once-per-battle skills refresh per turn)
# -- Durable (Chance to resist debuffs)
# -- OHKO resist (Chance to resist any attack that does more than Max HP)
# -- C-c-c-combobreaker (Chance to prevent opponent getting multiple turns)
# -- Libra (See monster stats... with some percent chance? accuracy?)
# TODO: General resist damage trait?

class Character(object):
  def __init__(self):
    # Weapon, Helm, Chest, Legs, Accessory
    self.equipment = [None, None, None, None, None]
    self.items = []
    self.skills = []
    self.stats = {"Strength": 20, "Stamina": 20, "Defense": 20, "Speed": 20,
                  "Intellect": 20, "Magic Defense": 20}
    self.gold = 100
    self.name = "Hero?"
    self.base_hp = 20
    self.base_sp = 20
    self.max_hp = 5 * self.stats["Stamina"] + self.base_hp
    self.max_sp = self.base_sp + self.stats["Intellect"]
    self.current_hp = self.max_hp
    self.current_sp = self.max_sp
    self.level = 1
    self.exp = 0
    self.materials = [0] * len(RARITY)
    self.buffs = []
    self.debuffs = []
    self.runes = 0
    self.traits = collections.defaultdict(int)
    self.reroll_counter = 0
    # DEBUG
    self.skills.append(skills.Concentrate(5))

  def add_item(self, item):
    if len(self.items) >= 3:
      return False
    self.items.append(item)
    return True

  def use_item(self, index, monster, logs):
    item = self.items.pop(index)
    item.apply(self, monster, logs)

  def add_buff(self, new_buff):
    Buff.add_buff(self.buffs, new_buff)
    self.recalculate_maxes()

  def add_debuff(self, new_debuff):
    Debuff.add_debuff(self.debuffs, new_debuff)
    self.recalculate_maxes()

  def pass_time(self, time_passed):
    remaining_buffs = []
    for buff in self.buffs:
      buff.pass_time(time_passed)
      if buff.active():
        remaining_buffs.append(buff)
    self.buffs = remaining_buffs
    restored_hp = self.traits["Regeneration"] * self.max_hp * time_passed / 100
    # Not used yet
    restored_sp = self.traits["Clarity of Mind"] * time_passed
    self.restore_hp(restored_hp)
    self.restore_sp(restored_sp)
    self.recalculate_maxes()

    remaining_debuffs = []
    for debuff in self.debuffs:
      debuff.pass_time(time_passed)
      if debuff.active():
        remaining_debuffs.append(debuff)
    self.debuffs = remaining_debuffs
    self.recalculate_maxes()

  def gain_gold(self, amount):
    amount_gained = amount * (1.00 + (0.05 * self.traits["Merchant Warrior"]))
    amount_gained = int(amount_gained)
    self.gold += amount_gained
    return amount_gained

  def make_initial_equipment(self, choice):
    for i in range(len(self.equipment)):
      self.equip(Equipment.get_new_armor(1, slot=i, require=choice))

  def __str__(self):
    pieces = []
    pieces.append("Character:\n")
    pieces.append("HP: %d / %d\n" % (self.current_hp, self.max_hp))
    pieces.append("SP: %d / %d\n" % (self.current_sp, self.max_sp))
    pieces.append("Level: %d " % self.level)
    pieces.append("(%d / %d)\n" % (self.exp, self.next_level_exp()))
    for stat in STAT_ORDER:
      pieces.append("%s: %d (%d)  " % (stat, self.get_effective_stat(stat),
                                       self.stats[stat]))
    pieces.append("\n")
    pieces.append("Equipment:\n")
    for piece in self.equipment:
      pieces.append(str(piece) + "\n")
    pieces.append("Traits: ")
    if sum(self.traits.values()) == 0:
      pieces.append("None")
    else:
      for trait in self.traits:
        if self.traits[trait] > 0:
          pieces.append("%s: %d  " % (trait, self.traits[trait]))
    pieces.append("\n")
    pieces.append("Skills: ")
    if not self.skills:
      pieces.append("None")
    else:
      for skill in self.skills:
        pieces.append("%s: %d" % (skill.get_name(), skill.level))
    pieces.append("\n")
    pieces.append("Materials: ")
    if sum(self.materials) == 0:
      pieces.append("None\n")
    else:
      # TODO: Use function in Equipment?
      for i in xrange(len(self.materials)):
        if self.materials[i] > 0:
          pieces.append("%s: %d  " % (RARITY[i], self.materials[i]))
      pieces.append("\n")
    pieces.append("Buffs: ")
    pieces.append(", ".join(str(buff) for buff in self.buffs))
    if self.buffs:
      pieces.append("\n")
    else:
      pieces.append("None\n")
    pieces.append("Debuffs: ")
    pieces.append(", ".join(str(debuff) for debuff in self.debuffs))
    if self.debuffs:
      pieces.append("\n")
    else:
      pieces.append("None\n")
    pieces.append("Items: ")
    if self.items:
      pieces.append(", ".join(item.get_name() for item in self.items))
      pieces.append("\n")
    else:
      pieces.append("None\n")
    pieces.append("Corrupted runes: %d" % self.runes)
    return "".join(pieces)

  def restore_hp(self, amount=None):
    old_current = self.current_hp
    if amount is None:
      self.current_hp = self.max_hp
    else:
      self.current_hp = min(self.max_hp, self.current_hp + amount)
    return self.current_hp - old_current

  def restore_sp(self, amount=None):
    old_current = self.current_sp
    if amount is None:
      self.current_sp = self.max_sp
    else:
      self.current_sp = min(self.max_sp, self.current_sp + amount)
    return self.current_sp - old_current

  def rest(self):
    hp_gained = self.max_hp/10
    return self.restore_hp(hp_gained)

  def apply_death(self, logs, penalty=True):
    logs.append("You have been defeated.")
    self.restore_hp()
    self.restore_sp()
    self.debuffs = []
    if penalty:
      logs.append("You were found by a passerby, and brought back to town.")
      lost_gold = self.gold / 2
      logs.append("You lost %d gold" % lost_gold)
      self.gold -= lost_gold
      self.buffs = []

  def get_effective_stat(self, stat):
    value = self.stats[stat]
    for piece in self.equipment:
      if piece:
        value += piece.get_stat_value(stat)
    effect = Effect.get_combined_impact(stat, self.buffs, self.debuffs)
    value = int(value * effect)
    return value

  def equip(self, item):
    slot = item.slot
    removed = self.equipment[slot]
    self.equipment[slot] = item
    self.recalculate_maxes()
    return removed

  def get_damage(self):
    # 0 is weapon
    return self.equipment[0].get_damage()

  def get_damage_type(self):
    return self.equipment[0].get_damage_type()

  def next_level_exp(self):
    # TODO: Something more "complex", lol
    return self.level * 100

  def recalculate_maxes(self):
    new_max_hp = self.get_effective_stat("Stamina") * 5 + self.base_hp
    difference = new_max_hp - self.max_hp
    self.current_hp += max(0, difference)  # Don't lose HP for equipping
    self.max_hp = new_max_hp
    self.current_hp = min(self.current_hp, self.max_hp)  # Unless max_hp drops
    new_max_sp = self.get_effective_stat("Intellect") + self.base_sp
    difference = new_max_sp - self.max_sp
    self.current_sp += max(0, difference)  # Don't lose HP for equipping
    self.max_sp = new_max_sp
    self.current_sp = min(self.current_sp, self.max_sp)  # Unless max_hp drops

  def level_up(self, logs):
    for stat in self.stats:
      increase = random.randint(1, 3)
      if increase > 0:
        self.stats[stat] += increase
        logs.append("You have gained %d %s" % (increase, stat))
    hp_gain = random.randint(10, 20)
    sp_gain = random.randint(5, 10)
    self.base_hp += hp_gain
    self.base_sp += sp_gain
    logs.append("You have gained %d HP" % hp_gain)
    logs.append("You have gained %d SP" % sp_gain)
    self.recalculate_maxes()

  def train_xp(self, level, logs):
    return self.gain_exp(level * 25, level, logs, level_adjust=False)

  def train_stats(self, logs):
    stat = random.choice(self.stats.keys())
    self.stats[stat] += 1
    logs.append("Gained +1 %s" % stat)

  def gain_materials(self, materials):
    for i in xrange(len(materials)):
      self.materials[i] += materials[i]

  def get_trait_choices(self):
    # TODO: DIRTY DIRTY HACK
    # The problem is, in the game_state, it's assumed that multiple calls to
    # get_choices (which calls this) will return the same value. But these
    # choices are random. We want them to be the same for the two calls during
    # level-up, and these values should not change between those two calls.
    # To get around this, we probably would need to store the choices in
    # game_state and know to look at them for only levelling up.
    random.seed((self.exp, self.current_hp, self.gold, self.reroll_counter))
    choices = [""]
    reroll_trait_level = self.traits["Self-Improvement"]
    reroll_chance = float(reroll_trait_level) / (reroll_trait_level + 1)
    if random.random() < reroll_chance:
      choices.append("Get New Traits")
    while len(choices) < 4:
      best_roll, best_trait = 0.0, None
      for trait in TRAITS:
        rerolls = self.traits[trait] + 1
        roll = min(random.random() for _ in range(rerolls))
        if roll > best_roll:
          best_roll, best_trait = roll, trait
      if best_trait not in choices:
        choices.append(best_trait)
    return choices

  def learn_trait(self, trait):
    if trait == "Get New Traits":
      self.reroll_counter += 1
      return False
    assert trait in TRAITS
    self.traits[trait] += 1
    return True

  def gain_exp(self, exp, encounter_level, logs, level_adjust=True):
    exp_gained = exp * (1.0 + (0.03 * self.traits["Quick Learner"]))
    level_difference = encounter_level - self.level
    if level_adjust:
      exp_gained = int(exp_gained * (1.1 ** level_difference))
    xp_buff = Effect.get_combined_impact("XP Gain", self.buffs, self.debuffs)
    total_xp_gain = int(exp_gained * xp_buff)
    self.exp += total_xp_gain
    added_xp = total_xp_gain - exp_gained
    logs.append("You have gained %d XP (%+d buffs)" % (exp_gained, added_xp))
    levels_gained = 0
    while self.exp >= self.next_level_exp():
      self.exp -= self.next_level_exp()
      self.level += 1
      logs.append("You have reached level %d!" % self.level)
      self.level_up(logs)
      levels_gained += 1
    return levels_gained
