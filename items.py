import effect
from equipment import RARITY
from character import TRAITS
from character import STAT_ORDER
import srs_random

# TODO: Add substitute (automatic rez when you die)
# TODO: Add names to items (based on stats / slot)

class Item(object):
  UNUSABLE = 0
  def __init__(self):
    self.info = {"name": "Not Implemented",
                 "value": 2**100,
                 "item_level": 100}
  def apply(self, character, monster, logs):  # monsters don't get items
    # Will return an error code if the item can't be used.
    pass
  def get_name(self):
    return self.info["name"]
  def get_value(self):
    return self.info["value"]
  def get_item_level(self):
    return self.info["item_level"]

class HealthPotion(Item):
  HP_POTIONS = {"Minor": {"value": 100, "level": 1, "effect": 200},
                "Standard": {"value": 500, "level": 10, "effect": 600},
                "Major": {"value": 2500, "level": 30, "effect": 1800},
                "Super": {"value": 15000, "level": 30, "effect": 5400},
               }
  def __init__(self, rank):
    super(HealthPotion, self).__init__()
    self.rank = rank
    name = "{} HP Pot".format(rank)
    value = self.HP_POTIONS[rank]["value"]
    level = self.HP_POTIONS[rank]["level"]
    self.info = {"name": name, "value": value, "item_level": level}

  def apply(self, character, monster, logs):
    hp_gained = character.restore_hp(self.HP_POTIONS[self.rank]["effect"])
    logs.append("You restored {} HP.".format(hp_gained))

class MagicPotion(Item):
  SP_POTIONS = {"Minor": {"value": 200, "level": 1, "effect": 50},
                "Standard": {"value": 1200, "level": 10, "effect": 200},
                "Major": {"value": 7500, "level": 30, "effect": 600},
               }
  def __init__(self, rank):
    super(MagicPotion, self).__init__()
    self.rank = rank
    name = "{} SP Pot".format(rank)
    value = self.SP_POTIONS[rank]["value"]
    level = self.SP_POTIONS[rank]["level"]
    self.info = {"name": name, "value": value, "item_level": level}

  def apply(self, character, monster, logs):
    sp_gained = character.restore_sp(self.SP_POTIONS[self.rank]["effect"])
    logs.append("You restored {} SP.".format(sp_gained))

class InnFood(Item):
  def __init__(self):
    super(InnFood, self).__init__()
    self.info = {"name": "Inn-made Bento",
                 "value": 0,
                 "item_level": 1}

  def apply(self, character, monster, logs):
    if monster:
      logs.append("You cannot eat the Inn-made Bento in combat.")
      return Item.UNUSABLE
    else:
      character.add_buff(effect.WellFed(300))
      logs.append("You ate the Inn-made Bento.")

class EffectPotion(Item):
  # No "Standard" potions because there is no "default" effect to conflict with
  EFFECT_POTIONS = {"Minor Surge": {"value": 100, "level": 1, "effect": effect.Surge(5, 1.5)},
                    "Surge": {"value": 500, "level": 10, "effect": effect.Surge(10, 2.0)},
                    "Major Surge": {"value": 2500, "level": 30, "effect": effect.Surge(15, 2.5)},
                    "Minor Concentrate": {"value": 100, "level": 1, "effect": effect.Concentrate(5, 1.5)},
                    "Concentrate": {"value": 500, "level": 10, "effect": effect.Concentrate(10, 2.0)},
                    "Major Concentrate": {"value": 2500, "level": 30, "effect": effect.Concentrate(15, 2.5)},
                    "Minor Swiftness": {"value": 100, "level": 1, "effect": effect.Swiftness(5, 1.5)},
                    "Swiftness": {"value": 500, "level": 10, "effect": effect.Swiftness(10, 2.0)},
                    "Major Swiftness": {"value": 2500, "level": 30, "effect": effect.Swiftness(15, 2.5)},
                    "Minor BulkUp": {"value": 300, "level": 1, "effect": effect.BulkUp(5, 1.4)},
                    "BulkUp": {"value": 1500, "level": 10, "effect": effect.BulkUp(10, 1.7)},
                    "Major BulkUp": {"value": 7500, "level": 30, "effect": effect.BulkUp(15, 2.0)},
  }
  def __init__(self, name):
    super(EffectPotion, self).__init__()
    self.effect = self.EFFECT_POTIONS[name]["effect"]
    value = self.EFFECT_POTIONS[name]["value"]
    level = self.EFFECT_POTIONS[name]["level"]
    pot_name = "{} Pot".format(name)
    # TODO: Pull buff names from effect classes
    self.buff_name = name.split(' ')[-1] # Example: "Minor Surge" class gives "Surge" buff
    self.info = {"name": pot_name, "value": value, "item_level": level}

  def apply(self, character, monster, logs):
    character.add_buff(self.effect)
    logs.append("You have gained the {} buff.".format(self.buff_name))

# Mystery Trader items
# These are all applied outside of combat, and should NOT appear in other shops

class RareCandy(Item):
  def __init__(self):
    self.info = {"name": "Rare Candy",
                 "value": 50,
                 "item_level": 1}
  def apply(self, character, monster, logs):  # monsters don't get items
    # NB: This item does not trigger level up routines in game_state.
    #     Whatever calls this is responsible for that.
    character.level += 1
    logs.append("You have reached level {}!".format(character.level))
    character.level_up(logs)
    # Start here: Finish the Inn, and test this.

class TeleportStone(Item):
  def __init__(self):
    self.info = {"name": "Teleport Stone",
                 "value": 70,
                 "item_level": 1}
  def apply(self, character, monster, logs):
    # NB: This item does not trigger tower climbing routines in game_state.
    pass

class StatStone(Item):
  STONE_TYPES = STAT_ORDER + ["Rainbow"]
  def __init__(self):
    self.stone_type = srs_random.choice(self.STONE_TYPES)
    self.info = {"name": "{} Stone".format(self.stone_type),
                 "value": 100,
                 "item_level": 1}
  def apply(self, character, monster, logs):
    if self.stone_type == "Rainbow":
      for stat in character.stats:
        amount = srs_random.randint(2, 4)
        logs.append("You gained {} {}".format(amount, stat))
        character.stats[stat] += amount
    else:
      amount = srs_random.randint(8, 12)
      logs.append("You gained {} {}".format(amount, self.stone_type))
      character.stats[self.stone_type] += amount

class MaterialPack(Item):
  def __init__(self):
    self.material_type = srs_random.randint(0, 4)
    value = 40 * (2**self.material_type)
    self.info = {"name": "{} Materials Pack".format(RARITY[self.material_type]),
                 "value": value,
                 "item_level": 1}
  def apply(self, character, monster, logs):
    counts = [0] * 5
    for i in range(40):
      rarity = self.material_type + srs_random.gauss(.5, 1)
      rarity = max(0, min(4, int(rarity)))
      counts[rarity] += 1
    for i, count in enumerate(counts):
      if count > 0:
        logs.append("You got {} {} materials".format(count, RARITY[i]))
        character.materials[i] += count

class Tome(Item):
  TOME_TYPES = TRAITS.keys() + ["Rainbow"]
  TOME_TYPES.remove("Libra")

  def __init__(self):
    self.tome_type = srs_random.choice(self.TOME_TYPES)
    value = 200 if self.tome_type == "Rainbow" else 100
    self.info = {"name": "{} Tome".format(self.tome_type),
                 "value": value,
                 "item_level": 1}
  def apply(self, character, monster, logs):
    if self.tome_type == "Rainbow":
      for trait in TRAITS.keys():
        if trait == "Libra": continue
        if srs_random.random() > .5:
          logs.append("You improved the {} trait.".format(trait))
          character.traits[trait] = character.traits.get(trait, 0) + 1
    else:
      levels = srs_random.randint(1, 3)
      logs.append("You gained {} levels of the {} trait".format(levels,
                                                                self.tome_type))
      character.traits[self.tome_type] = character.traits.get(self.tome_type, 0) + levels

class CorruptedRune(Item):
  def __init__(self):
    self.info = {"name": "Corrupted Rune",
                 "value": 150,
                 "item_level": 1}
  def apply(self, character, monster, logs):
    character.runes += 1

class GoldSack(Item):
  SIZES = ["Small", "Medium", "Large", "Huge", "Gigantic"]
  def __init__(self):
    self.size = srs_random.randint(0, 4)
    value = 50 * (2**self.size)
    self.info = {"name": "{} Sack of Gold".format(self.SIZES[self.size]),
                 "value": value,
                 "item_level": 1}
  def apply(self, character, monster, logs):
    gold = 2500 * (2**self.size)
    gold *= srs_random.gauss(1, .05)
    gold_gained = character.gain_gold(gold)
    logs.append("You gained {} gold".format(gold_gained))

class HPStone(Item):
  def __init__(self):
    self.info = {"name": "HP Stone",
                 "value": 75,
                 "item_level": 1}
  def apply(self, character, monster, logs):
    character.base_hp += 50
    character.recalculate_maxes()
    logs.append("You gain 50 HP")

class SPStone(Item):
  def __init__(self):
    self.info = {"name": "SP Stone",
                 "value": 150,
                 "item_level": 1}
  def apply(self, character, monster, logs):
    character.base_sp += 30
    character.recalculate_maxes()
    logs.append("You gain 30 SP")
