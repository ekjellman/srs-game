import random
from skills import SKILLS, SKILL_NAMES
from equipment import Equipment, RARITY
from effect import Effect, Buff, Debuff
import items

STAT_ORDER = ["Strength", "Intellect", "Speed", "Stamina", "Defense",
              "Magic Defense"]

TRAITS = {"Beefy!": "Increase physical damage",
          "Wizardry": "Increase magical damage",
          "Perseverance": "Chance to survive fatal attacks in combat",
          "Scholar": "On level up, chance to choose new skills",
          "Self-Improvement": "On level up, chance to choose new passives",
          "Quick Learner": "Improved experience gain",
          "Merchant Warrior": "Improved gold gain",
          "Clarity of Mind": "SP regeneration over time",
          "Regeneration": "HP regeneration over time",
          "Stocky!": "Reduce physical damage",
          "Mental Toughness": "Reduce magical damage",
          "Combobreaker!": "Chance to prevent multiple consecutive enemy turns",
          "Libra": "See monster stats",
         }

GREEN_HP = "`0,160,0`"
YELLOW_HP = "`200,200,0`"
ORANGE_HP = "`224,136,20`"
RED_HP = "`255,0,0`"
BLACK = "`0,0,0`"

# TRAITS:
# TODO: There are more on the sheet
# -- Increased Stats
# -- Lightning Strike (chance to automatically go again after an attack)
# -- Dodge (chance to avoid all damage from an attack)

class Character(object):
  def __init__(self):
    # Weapon, Helm, Chest, Legs, Accessory
    self.equipment = [None, None, None, None, None]
    self.items = []
    self.skills = []
    self.stats = {"Strength": 20, "Stamina": 20, "Defense": 20, "Speed": 20,
                  "Intellect": 20, "Magic Defense": 20}
    self.gold = 100
    self.name = "Hero"
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
    self.traits = {}
    random.seed()
    self.reroll_counter = random.randint(0, 1000000)

  def colored_hp(self):
    hp_percent = self.current_hp * 100 / self.max_hp
    if hp_percent > 75:
      color = GREEN_HP
    elif hp_percent > 50:
      color = YELLOW_HP
    elif hp_percent > 25:
      color = ORANGE_HP
    else:
      color = RED_HP
    return "{}{} / {}{}".format(color, self.current_hp, self.max_hp, BLACK)

  @classmethod
  def debug_character(cls, level, choice_text):
    character = Character()
    for i in range(1, level):
      character.level_up([])
      trait_choices = character.get_trait_choices()
      choice = ""
      while choice not in TRAITS:
        choice = random.choice(trait_choices)
      character.learn_trait(choice)
      skill_choices = character.get_skill_choices()
      choice = ""
      while choice not in SKILL_NAMES + ["Improve stats"]:
        choice = random.choice(skill_choices)
      chance = 10.0 / i
      if random.random() < chance:
        character.learn_skill(choice)
      else:
        character.learn_skill("Improve stats")
    character.make_debug_equipment(level, choice_text)
    character.level = level
    return character

  def make_debug_equipment(self, level, choice):
    for i in range(len(self.equipment)):
      self.equip(Equipment.get_new_armor(level, i, choice, 3))

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
      if buff.turn_by_turn():
        for _ in range(time_passed):
          buff.pass_time(1)
          effect = Effect.get_combined_impact("HP Restore", self.buffs,
                                              self.debuffs)
          self.restore_hp(effect)
          if not buff.active():
            break
      else:
        buff.pass_time(time_passed)
      if buff.active():
        remaining_buffs.append(buff)
    self.buffs = remaining_buffs
    restored_hp = self.traits.get("Regeneration", 0) * 3 * time_passed
    # Not used yet
    restored_sp = self.traits.get("Clarity of Mind", 0) * time_passed
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
    amount_gained = amount * (1.00 + (0.05 * self.traits.get("Merchant Warrior", 0)))
    amount_gained = int(amount_gained)
    self.gold += amount_gained
    return amount_gained

  def make_initial_equipment(self, choice):
    for i in range(len(self.equipment)):
      self.equip(Equipment.get_new_armor(1, i, choice))

  def __str__(self):
    pieces = []
    pieces.append("Character:\n")
    pieces.append("HP: {} / {}\n".format(self.current_hp, self.max_hp))
    pieces.append("SP: {} / {}\n".format(self.current_sp, self.max_sp))
    pieces.append("Level: {} ".format(self.level))
    pieces.append("({} / {})\n".format(self.exp, self.next_level_exp()))
    for stat in STAT_ORDER:
      pieces.append("{}: {} ({})  ".format(stat, self.get_effective_stat(stat),
                                       self.stats[stat]))
    pieces.append("\n")
    pieces.append("Equipment:\n")
    for piece in self.equipment:
      pieces.append(str(piece) + "\n")
    pieces.append("Traits: ")
    if sum(self.traits.values()) == 0:
      pieces.append("None")
    else:
      for trait in self.traits.keys():
        if self.traits.get(trait, 0) > 0:
          pieces.append("{}: {}  ".format(trait, self.traits.get(trait, 0)))
    pieces.append("\n")
    pieces.append("Skills: ")
    if not self.skills:
      pieces.append("None")
    else:
      for skill in self.skills:
        pieces.append("{}: {}  ".format(skill.get_name(), skill.level))
    pieces.append("\n")
    pieces.append("Materials: ")
    if sum(self.materials) == 0:
      pieces.append("None\n")
    else:
      for i in range(len(self.materials)):
        if self.materials[i] > 0:
          pieces.append("{}: {}  ".format(RARITY[i], self.materials[i]))
      pieces.append("\n")
    pieces.append("Buffs: ")
    pieces.append(", ".join(str(buff) for buff in self.buffs))
    if self.buffs:
      pieces.append("\n")
    else:
      pieces.append("None\n")
    pieces.append("Items: ")
    if self.items:
      pieces.append(", ".join(item.get_name() for item in self.items))
      pieces.append("\n")
    else:
      pieces.append("None\n")
    pieces.append("Corrupted runes: {}".format(self.runes))
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
      logs.append("You lost {} gold".format(lost_gold))
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
    return int(self.level * 100 * (1.01 ** self.level))

  def recalculate_maxes(self):
    new_max_hp = self.get_effective_stat("Stamina") * 5 + self.base_hp
    difference = new_max_hp - self.max_hp
    self.current_hp += max(0, difference)  # Don't lose HP for equipping
    self.max_hp = new_max_hp
    self.current_hp = min(self.current_hp, self.max_hp)  # Unless max_hp drops
    new_max_sp = self.get_effective_stat("Intellect") + self.base_sp
    #difference = new_max_sp - self.max_sp
    #self.current_sp += max(0, difference)  # Don't lose HP for equipping
    self.max_sp = new_max_sp
    self.current_sp = min(self.current_sp, self.max_sp)  # Unless max_sp drops

  def level_up(self, logs):
    for stat in self.stats.keys():
      increase = random.randint(1, 3)
      if increase > 0:
        self.stats[stat] += increase
        logs.append("You have gained {} {}".format(increase, stat))
    hp_gain = random.randint(10, 20)
    sp_gain = random.randint(5, 10)
    self.base_hp += hp_gain
    self.base_sp += sp_gain
    logs.append("You have gained {} HP".format(hp_gain))
    logs.append("You have gained {} SP".format(sp_gain))
    self.recalculate_maxes()

  def train_xp(self, level, logs):
    return self.gain_exp(level * 25, level, logs, level_adjust=False)

  def train_stats(self, logs):
    stat = random.choice(self.stats.keys())
    self.stats[stat] += 1
    logs.append("Gained +1 {}".format(stat))

  def gain_materials(self, materials):
    for i in range(len(materials)):
      self.materials[i] += materials[i]

  def get_trait_choices(self):
    choices = [""]
    reroll_trait_level = self.traits.get("Self-Improvement", 0)
    reroll_chance = float(reroll_trait_level) / (reroll_trait_level + 1)
    if random.random() < reroll_chance:
      choices.append("Get New Traits")
    while len(choices) < 4:
      best_roll, best_trait = 0.0, None
      for trait in TRAITS.keys():
        rerolls = max(1, int((self.traits.get(trait, 0) + 1) ** .5))
        roll = min(random.random() for _ in range(rerolls))
        if trait == "Libra" and self.traits.get(trait, 0) > 0:  # Only one libra level
          roll = 0.0
        if roll > best_roll:
          best_roll, best_trait = roll, trait
      if best_trait not in choices:
        choices.append(best_trait)
    return choices

  def learn_trait(self, trait):
    if trait == "Get New Traits":
      self.reroll_counter += 1
      return False
    #assert trait in TRAITS
    self.traits[trait] = self.traits.get(trait, 0) + 1
    return True

  def get_skill_choices(self):
    # TODO: Have one of the skills be a new one, even if character has all
    #       three skills? In this case, we'd have to replace one of the existing
    #       skills, which might get tricky.
    choices = []
    random.seed((self.exp, self.current_hp, self.gold, self.reroll_counter))
    choices.append("Improve stats")
    # If we have three skills already, we can just choose from those
    if len(self.skills) == 3:
      choices.extend(skill.get_name() for skill in self.skills)
    else:
      reroll_skill_level = self.traits.get("Scholar", 0)
      reroll_chance = float(reroll_skill_level) / (reroll_skill_level + 1)
      if random.random() < reroll_chance:
        choices.append("Get New Skills")
      while len(choices) < 4:
        best_roll, best_skill = 0.0, None
        for skill_name in SKILL_NAMES:
          current_skill = self.have_skill(skill_name)
          if current_skill is None:
            rerolls = 1
          else:
            rerolls = int(current_skill.level ** .5)
          roll = min(random.random() for _ in range(rerolls))
          if roll > best_roll:
            best_roll, best_skill = roll, skill_name
        if best_skill not in choices:
          choices.append(best_skill)
    return choices

  def have_skill(self, name):
    for skill in self.skills:
      if skill.get_name() == name:
        return skill
    return None

  def learn_skill(self, skill_name):
    if skill_name == "Improve stats":
      for stat in self.stats.keys():
        self.stats[stat] += 1
      self.recalculate_maxes()
      return True
    if skill_name == "Get New Skills":
      self.reroll_counter += 1
      return False
    assert skill_name in SKILL_NAMES
    current_skill = self.have_skill(skill_name)
    if current_skill:
      current_skill.level += 1
      return True
    else:
      assert len(self.skills) < 3
      new_skill = None
      # TODO: Use a dictionary
      for skill in SKILLS:
        skill_instance = skill()
        if skill_instance.get_name() == skill_name:
          new_skill = skill_instance
      self.skills.insert(0, new_skill)
      return True

  def gain_exp(self, exp, encounter_level, logs, level_adjust=True):
    exp_gained = exp * (1.0 + (0.03 * self.traits.get("Quick Learner", 0)))
    level_difference = encounter_level - self.level
    if level_adjust:
      exp_gained = int(exp_gained * (1.03 ** level_difference))
    xp_buff = Effect.get_combined_impact("XP Gain", self.buffs, self.debuffs)
    total_xp_gain = int(exp_gained * xp_buff)
    self.exp += total_xp_gain
    added_xp = total_xp_gain - exp_gained
    logs.append("You have gained {} XP ({:+d} buffs)".format(exp_gained, added_xp))
    levels_gained = 0
    while self.exp >= self.next_level_exp():
      self.exp -= self.next_level_exp()
      self.level += 1
      logs.append("You have reached level {}!".format(self.level))
      self.level_up(logs)
      levels_gained += 1
    return levels_gained
