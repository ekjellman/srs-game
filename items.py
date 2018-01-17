import effect

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