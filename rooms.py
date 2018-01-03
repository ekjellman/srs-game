import random
from equipment import Equipment, RARITY
from effect import WellRested, Blessed
import items

# TODO: Rooms ideas:
#       Trader: For 5g? per piece, "trades" materials. Gaussian distribution
#               again. 

class Room(object):
  NO_CHANGE = 0
  LEAVE_ROOM = 1
  USE_ITEM = 2
  PURIFY_RUNE = 3
  ENTER_DUNGEON = 4
  LEVEL_UP = 5

  def __init__(self, level):
    self.level = level
    self.faction_rate = 1.0

  def refresh(self):
    pass

  @classmethod
  def get_name(cls):
    return "Unnamed Room"

  def get_buttons(self, character):
    return ["Not Implemented"] * 4

  def get_text(self, character):
    return "Not Implemented"

  def apply_choice(self, choice_text, logs, character):
    return (0, Room.LEAVE_ROOM)

  def enter_shop(self, faction_rate):
    self.faction_rate = faction_rate

class TrainingRoom(Room):
  def __init__(self, level):
    super(TrainingRoom, self).__init__(level)
    self.level = level
    self.train_count = 0

  @classmethod
  def get_name(cls):
    return "Trainer"

  def get_buttons(self, character):
    return ["", "Gain XP", "Gain Stats", "Leave Shop"]

  def stat_training_cost(self, character):
    return int(sum(character.stats.values()) * (self.train_count + 1) *
               self.faction_rate)

  def xp_training_cost(self):
    return int(self.level * ((self.train_count + 1) ** 2) * 50 *
               self.faction_rate)

  def get_text(self, character):
    pieces = []
    pieces.append("Gain XP: %d gold (%d base xp)" %
                  (self.xp_training_cost(), self.level * 25))
    pieces.append("Gain Stats: %d gold (+1 random stat)" %
                  self.stat_training_cost(character))
    return "\n".join(pieces)

  def apply_choice(self, choice_text, logs, character):
    if choice_text == "Gain XP":
      cost = self.xp_training_cost()
      if cost <= character.gold:
        levelups = character.train_xp(self.level, logs)
        self.train_count += 1
        character.gold -= cost
        if levelups > 0:
          # TODO (?): There's a bug here. What if the character levels up more
          # than once? That "shouldn't" happen, but...
          # One fix would be to make train_xp stop short of a level as a design
          # tradeoff, so levelling up doesn't happen in here.
          return (5, Room.LEVEL_UP)
        else:
          return (5, Room.NO_CHANGE)
      else:
        logs.append("Not enough money to train XP.")
        return (0, Room.NO_CHANGE)
    elif choice_text == "Gain Stats":
      cost = self.stat_training_cost(character)
      if cost <= character.gold:
        character.train_stats(logs)
        self.train_count += 1
        character.gold -= cost
        return (5, Room.NO_CHANGE)
      else:
        logs.append("Not enough money to train stats.")
        return (0, Room.NO_CHANGE)
    elif choice_text == "Leave Shop":
      return (0, Room.LEAVE_ROOM)
    assert False

class Enchanter(Room):
  def __init__(self, level):
    super(Enchanter, self).__init__(level)
    self.level = level
    self.enchanting_armor = False

  @classmethod
  def get_name(cls):
    return "Enchanter"

  def get_buttons(self, character):
    if self.enchanting_armor:
      return ["Enchant Helm", "Enchant Chest", "Enchant Legs", "Never Mind"]
    else:
      return ["Enchant Weapon", "Enchant Armor", "Enchant Accessory",
              "Leave Shop"]

  def enchant_cost_gold(self, item):
    return int(item.item_level * 25 * ((item.enchant_count + 1) ** 2) *
               self.faction_rate)

  @classmethod
  def enchant_cost_materials(cls, item):
    return item.item_level * (item.enchant_count + 1) / 2

  def armor_text(self, character):
    pieces = []
    for name, slot in (("Helm", 1), ("Chest", 2), ("Legs", 3)):
      item = character.equipment[slot]
      cost = self.enchant_cost_gold(item)
      material_cost = self.enchant_cost_materials(item)
      pieces.append("Enchant %s: %d gold and %d %s materials" %
                    (name, cost, material_cost, RARITY[item.rarity]))
    return "\n".join(pieces)

  def normal_text(self, character):
    pieces = []
    weapon = character.equipment[0]
    pieces.append("Enchant Weapon: %d gold and %d %s materials" %
                  (self.enchant_cost_gold(weapon),
                   self.enchant_cost_materials(weapon),
                   RARITY[weapon.rarity]))
    pieces.append("Enchant Armor: [submenu]")
    acc = character.equipment[4]
    pieces.append("Enchant Accessory: %d gold and %d %s materials" %
                  (self.enchant_cost_gold(acc),
                   self.enchant_cost_materials(acc),
                   RARITY[acc.rarity]))
    return "\n".join(pieces)

  def get_text(self, character):
    if self.enchanting_armor:
      return self.armor_text(character)
    else:
      return self.normal_text(character)

  def apply_enchantment(self, item, logs, character):
    cost = self.enchant_cost_gold(item)
    mat_cost = self.enchant_cost_materials(item)
    if (cost <= character.gold and
        mat_cost <= character.materials[item.rarity]):
      character.gold -= cost
      character.materials[item.rarity] -= mat_cost
      old_item_string = str(item)
      enchantment = item.enchant()
      logs.append("Your %s was enchanted (%s)." % (old_item_string, enchantment))
      return (3, Room.NO_CHANGE)
    else:
      logs.append("You do not have sufficient payment.")
      return (0, Room.NO_CHANGE)

  def apply_choice_enchanter(self, choice_text, logs, character):
    item = None
    if choice_text == "Enchant Weapon":
      item = character.equipment[0]
    elif choice_text == "Enchant Armor":
      self.enchanting_armor = True
      return (0, Room.NO_CHANGE)
    elif choice_text == "Enchant Accessory":
      item = character.equipment[4]
    elif choice_text == "Leave Shop":
      return (0, Room.LEAVE_ROOM)
    if item:
      return self.apply_enchantment(item, logs, character)
    assert False

  def apply_choice_enchant_armor(self, choice_text, logs, character):
    item = None
    if choice_text == "Enchant Helm":
      item = character.equipment[1]
    elif choice_text == "Enchant Chest":
      item = character.equipment[2]
    elif choice_text == "Enchant Legs":
      item = character.equipment[3]
    elif choice_text == "Never Mind":
      self.enchanting_armor = False
      return (0, Room.NO_CHANGE)
    if item:
      return self.apply_enchantment(item, logs, character)
    assert False

  def apply_choice(self, choice_text, logs, character):
    if self.enchanting_armor:
      return self.apply_choice_enchant_armor(choice_text, logs, character)
    else:
      return self.apply_choice_enchanter(choice_text, logs, character)

  def enter_shop(self, faction_rate):
    self.enchanting_armor = False
    self.faction_rate = faction_rate

class Forge(Room):
  def __init__(self, level):
    super(Forge, self).__init__(level)
    self.level = level
    self.forging_armor = False

  @classmethod
  def get_name(cls):
    return "Forge"

  def get_buttons(self, character):
    choices = []
    if self.forging_armor:
      for name, slot in (("Helm", 1), ("Chest", 2), ("Legs", 3)):
        if self.reforgable(character.equipment[slot]):
          choices.append("Reforge %s" % name)
        else:
          choices.append("")
      choices.append("Never Mind")
    else:
      choices.append("")
      if self.reforgable(character.equipment[0]):
        choices.append("Reforge Weapon")
      else:
        choices.append("")
      choices.append("Reforge Armor")
      choices.append("Leave Shop")
    return choices

  def reforge_cost_gold(self, item):
    level = item.item_level
    return int((self.level - level)
               * ((15 * level) * ((item.reforge_count + 1) ** 2))
               * self.faction_rate)

  def reforge_cost_materials(self, item):
    return (self.level - item.item_level) * (item.reforge_count + 1)

  def reforgable(self, item):
    return item.item_level < self.level

  def forge_text(self, character):
    pieces = []
    weapon = character.equipment[0]
    if self.reforgable(weapon):
      pieces.append("Reforge Weapon: %d gold and %d %s materials" %
                    (self.reforge_cost_gold(weapon),
                     self.reforge_cost_materials(weapon),
                     RARITY[weapon.rarity]))
    else:
      pieces.append("Weapon cannot currently be reforged.")
    pieces.append("Reforge Armor: [submenu]")
    return "\n".join(pieces)

  def forge_armor_text(self, character):
    pieces = []
    for name, slot in (("Helm", 1), ("Chest", 2), ("Legs", 3)):
      item = character.equipment[slot]
      if self.reforgable(item):
        cost = self.reforge_cost_gold(item)
        material_cost = self.reforge_cost_materials(item)
        pieces.append("Reforge %s: %d gold and %d %s materials" %
                      (name, cost, material_cost, RARITY[item.rarity]))
      else:
        pieces.append("%s cannot currently be reforged." % name)
    return "\n".join(pieces)

  def get_text(self, character):
    if self.forging_armor:
      return self.forge_armor_text(character)
    else:
      return self.forge_text(character)

  def apply_reforge(self, item, character, logs):
    cost = self.reforge_cost_gold(item)
    mat_cost = self.reforge_cost_materials(item)
    if (cost <= character.gold and
        mat_cost <= character.materials[item.rarity]):
      character.gold -= cost
      character.materials[item.rarity] -= mat_cost
      old_item_string = str(item)
      improvement = item.reforge(self.level)
      logs.append("Your %s was reforged (%s)." % (old_item_string, improvement))
      return (3, Room.NO_CHANGE)
    else:
      logs.append("You do not have sufficient payment.")
      return (0, Room.NO_CHANGE)

  def apply_choice(self, choice_text, logs, character):
    item = None
    if choice_text == "Reforge Weapon":
      item = character.equipment[0]
    elif choice_text == "Reforge Helm":
      item = character.equipment[1]
    elif choice_text == "Reforge Chest":
      item = character.equipment[2]
    elif choice_text == "Reforge Legs":
      item = character.equipment[3]
    elif choice_text == "Reforge Armor":
      self.forging_armor = True
      return (0, Room.NO_CHANGE)
    elif choice_text == "Leave Shop":
      return (0, Room.LEAVE_ROOM)
    elif choice_text == "Never Mind":
      self.forging_armor = False
      return (0, Room.NO_CHANGE)
    if item:
      return self.apply_reforge(item, character, logs)
    assert False

  def enter_shop(self, faction_rate):
    self.forging_armor = False
    self.faction_rate = faction_rate

class EquipmentShop(Room):
  def __init__(self, level, shop_type):
    self.level = level
    self.inventory = None
    self.buying = False
    self.shop_choice = None
    self.shop_type = shop_type

  def get_buttons(self, character):
    if self.buying:
      return ["", "Keep Current", "Buy", ""]
    else:
      choices = []
      for i in range(len(self.inventory)):
        if self.inventory[i]:
          choices.append("%s #%d" % (self.shop_type, i + 1))
        else:
          choices.append("")
      choices.append("Leave Shop")
      return choices

  def get_cost(self, item):
    return int(item.get_value() * self.faction_rate)

  def get_text(self, character):
    if self.buying:
      equip = self.inventory[self.shop_choice]
      slot = equip.slot
      return Equipment.equipment_comparison_text(character.equipment[slot],
                                                 equip)
    else:
      pieces = []
      for i, item in enumerate(self.inventory):
        if item is not None:
          pieces.append("%s #%d  (%d gold)" % (self.shop_type, i + 1, 
                                               self.get_cost(item)))
          pieces.append(str(item))
      if not pieces:
        pieces.append("You cleaned 'em out!")
      return "\n".join(pieces)

  def apply_choice_buy_equipment(self, choice_text, logs, character):
    if choice_text == "Keep Current":
      self.buying = False
      return (0, Room.NO_CHANGE)
    elif choice_text == "Buy":
      equipment = self.inventory[self.shop_choice]
      value = self.get_cost(equipment)
      if character.gold >= value:
        character.gold -= value
        recycle = character.equip(equipment)
        self.inventory[self.shop_choice] = None
        self.shop_choice = None
        self.buying = False
        logs.append("Purchased %s for %d gold." % (str(equipment), value))
        logs.append("Recycled %s." % recycle)
        materials = recycle.get_recycled_materials()
        character.gain_materials(materials)
        logs.append("Received %s" % Equipment.materials_string(materials))
        return (1, Room.NO_CHANGE)
      else:
        logs.append("You do not have enough money.")
        self.buying = False
        self.shop_choice = None
        return (0, Room.NO_CHANGE)

  def apply_choice(self, choice_text, logs, character):
    if self.buying:
      return self.apply_choice_buy_equipment(choice_text, logs, character)
    elif choice_text.startswith("%s #" % self.shop_type):
      choice = int(choice_text[-1])
      self.shop_choice = choice - 1
      self.buying = True
      logs.append("You consider %s..." % choice_text)
      return (0, Room.NO_CHANGE)
    elif choice_text == "Leave Shop":
      return (0, Room.LEAVE_ROOM)

  def enter_shop(self, faction_rate):
    self.buying = False
    self.shop_choice = None
    self.faction_rate = faction_rate

class ArmorShop(EquipmentShop):
  def __init__(self, level):
    super(ArmorShop, self).__init__(level, "Armor")
    self.refresh()

  def refresh(self):
    self.inventory = [Equipment.get_new_armor(self.level, slot)
                      for slot in range(1, 4)]

  @classmethod
  def get_name(cls):
    return "Armorer"

class WeaponShop(EquipmentShop):
  def __init__(self, level):
    super(WeaponShop, self).__init__(level, "Weapon")
    self.refresh()

  def refresh(self):
    self.inventory = [Equipment.get_new_armor(self.level, 0) for _ in range(3)]

  @classmethod
  def get_name(cls):
    return "Weaponsmith"

class Jeweler(EquipmentShop):
  def __init__(self, level):
    super(Jeweler, self).__init__(level, "Accessory")
    self.refresh()

  def refresh(self):
    self.inventory = [Equipment.get_new_armor(self.level, 4) for _ in range(3)]

  @classmethod
  def get_name(cls):
    return "Jeweler"

class RareGoodsShop(EquipmentShop):
  def __init__(self, level):
    super(RareGoodsShop, self).__init__(level, "Equipment")
    self.refresh()

  def refresh(self):
    self.inventory = []
    for _ in range(3):
      level = max(1, self.level + int(random.gauss(0, 3)))
      rarity = random.randint(2, 4)
      slot = random.randint(0, 4)
      equip = Equipment.get_new_armor(level, slot=slot, rarity=rarity)
      self.inventory.append(equip)

  @classmethod
  def get_name(cls):
    return "Rare Goods Shop"

class Inn(Room):
  @classmethod
  def get_name(cls):
    return "Inn"

  def get_buttons(self, character):
    return ["", "Rest", "Buy Food", "Leave Inn"]

  def get_rest_cost(self):
    return int(self.level * 10 * self.faction_rate)

  def get_food_cost(self):
    return int(self.level * 10 * self.faction_rate)

  def get_text(self, character):
    pieces = []
    pieces.append("Rest: (%dg + 30 time) Well Rested buff" %
                  self.get_rest_cost())
    pieces.append("Buy Food: %d gold" % self.get_food_cost())
    return "\n".join(pieces)

  def apply_choice(self, choice_text, logs, character):
    if choice_text == "Rest":
      cost = self.get_rest_cost()
      if cost <= character.gold:
        character.gold -= cost
        character.add_buff(WellRested(510))
        logs.append("You became well rested.")
        return (30, Room.NO_CHANGE)
      else:
        logs.append("You do not have sufficient money.")
        return (0, Room.NO_CHANGE)
    # TODO: There's a lot of very similar "buying things" code to consolidate
    elif choice_text == "Buy Food":
      if character.gold >= self.get_food_cost():
        item = items.InnFood()
        result = character.add_item(item)
        if result:
          character.gold -= self.get_food_cost()
          logs.append("You purchase the %s." % item.get_name())
          return (1, Room.NO_CHANGE)
        else:
          logs.append("Your inventory is full!")
          return (0, Room.USE_ITEM)
      else:
        logs.append("You do not have enough gold to buy that.")
        return (0, Room.NO_CHANGE)
    elif choice_text == "Leave Inn":
      return (0, Room.LEAVE_ROOM)

  def enter_shop(self, faction_rate):
    self.faction_rate = faction_rate

class Temple(Room):
  @classmethod
  def get_name(cls):
    return "Temple"

  def refresh(self):
    pass

  def get_buttons(self, character):
    return ["", "Blessing", "Purify Rune", "Leave Temple"]

  def get_text(self, character):
    pieces = []
    pieces.append("Blessing: (%dg) Blessed buff" % (self.get_blessing_cost()))
    pieces.append("Purify Rune: Enter the rune world to cleanse a rune")
    return "\n".join(pieces)

  def get_blessing_cost(self):
    return int(50 * self.level * self.faction_rate)

  def apply_choice(self, choice_text, logs, character):
    if choice_text == "Blessing":
      cost = self.get_blessing_cost()
      if cost <= character.gold:
        character.gold -= cost
        character.add_buff(Blessed(241))
        logs.append("You were blessed.")
        return (1, Room.NO_CHANGE)
      else:
        logs.append("You do not have sufficient money.")
        return (0, Room.NO_CHANGE)
    elif choice_text == "Purify Rune":
      if character.runes <= 0:
        logs.append("You don't have any corrupted runes.")
        return (0, Room.NO_CHANGE)
      else:
        logs.append("The priest sends you into the world of the rune...")
        return (0, Room.PURIFY_RUNE)
    elif choice_text == "Leave Temple":
      return (0, Room.LEAVE_ROOM)

  def enter_shop(self, faction_rate):
    self.faction_rate = faction_rate

class Alchemist(Room):
  def __init__(self, level):
    super(Alchemist, self).__init__(level)
    self.level = level
    self.faction_rate = 1.0
    self.possible_items = [items.MinorHealthPotion, items.MajorHealthPotion,
                           items.HealthPotion, items.SuperHealthPotion,
                           items.MagicPotion, items.MinorMagicPotion,
                           items.MajorMagicPotion,
                           items.SurgePotion, items.MajorSurgePotion,
                           items.MinorSurgePotion,
                           items.SwiftnessPotion, items.MajorSwiftnessPotion,
                           items.MinorSwiftnessPotion,
                           items.BulkUpPotion, items.MajorBulkUpPotion,
                           items.MinorBulkUpPotion,
                           items.ConcentratePotion,
                           items.MajorConcentratePotion,
                           items.MinorConcentratePotion]
    self.inventory = self.generate_inventory()

  def item_rate(self, item):
    """Returns a number representing how much it should appear in the shop."""
    return random.random() / (abs(self.level - item.get_item_level()) + 1)

  def generate_inventory(self):
    inventory = []
    for _ in range(3):
      pots = [x() for x in self.possible_items]   # Shouldn't redefine item
      inventory.append(max((self.item_rate(p), p) for p in pots)[1])
    return inventory

  def refresh(self):
    self.inventory = self.generate_inventory()

  @classmethod
  def get_name(cls):
    return "Alchemist"

  def get_buttons(self, character):
    choices = []
    for i, item in enumerate(self.inventory):
      if item:
        choices.append("Choice #%d" % (i + 1))
      else:
        choices.append("")
    choices.append("Leave Shop")
    return choices

  def get_cost(self, item):
    return int(item.get_value() * self.faction_rate)

  def get_text(self, character):
    pieces = []
    for i, item in enumerate(self.inventory):
      if item:
        pieces.append("Choice #%d: %s (%d gold)" % (i + 1, item.get_name(),
                                                    self.get_cost(item)))
      else:
        pieces.append("")
    return "\n".join(pieces)

  def apply_choice(self, choice_text, logs, character):
    if choice_text.startswith("Choice #"):
      choice = int(choice_text[-1]) - 1
      item = self.inventory[choice]
      if character.gold >= self.get_cost(item):
        result = character.add_item(item)
        if result:
          character.gold -= self.get_cost(item)
          logs.append("You purchase a %s." % item.get_name())
          self.inventory[choice] = None
          return (1, Room.NO_CHANGE)
        else:
          logs.append("Your inventory is full!")
          return (0, Room.USE_ITEM)
      else:
        logs.append("You do not have enough gold to buy that.")
        return (0, Room.NO_CHANGE)
    elif choice_text == "Leave Shop":
      return (0, Room.LEAVE_ROOM)
    assert False

  def enter_shop(self, faction_rate):
    self.faction_rate = faction_rate

class Crafthall(Room):
  def __init__(self, level):
    super(Crafthall, self).__init__(level)
    self.level = level
    self.faction_rate = 1.0  # Ignored
    self.crafting = False
    self.crafted_piece = None

  @classmethod
  def get_name(cls):
    return "Crafthall"

  def get_buttons(self, character):
    if self.crafting:
      return ["", "Keep Current", "Keep New", ""]
    else:
      return ["Craft Uncommon", "Craft Rare", "Craft Epic", "Leave Shop"]

  def get_text(self, character):
    if self.crafting:
      equip = self.crafted_piece
      slot = equip.slot
      return Equipment.equipment_comparison_text(character.equipment[slot],
                                                 equip)
    else:
      pieces = []
      pieces.append("Craft Uncommon: %d gold, %d common mats, %d uncommon mats"
                    % (self.level * 10, self.level, self.level))
      pieces.append("Craft Rare: %d gold, %d common mats, %d rare mats"
                    % (self.level * 20, self.level, self.level))
      pieces.append("Craft Epic: %d gold, %d common mats, %d epic mats"
                    % (self.level * 30, self.level, self.level))
      return "\n".join(pieces)

  @classmethod
  def get_craft_rarity(cls, starting_rarity):
    rarity = starting_rarity
    while random.random() < .1:
      rarity += 1
    return min(rarity, 4)

  def handle_craft(self, rarity, logs, character):
    if (character.materials[0] >= self.level and
        character.materials[rarity] >= self.level and
        character.gold >= 10 * rarity * self.level):
      character.materials[0] -= self.level
      character.materials[rarity] -= self.level
      character.gold -= 10 * rarity * self.level
      rarity = self.get_craft_rarity(rarity)
      self.crafting = True
      level = int(self.level + max(0, random.gauss(0, 1)))
      self.crafted_piece = Equipment.get_new_armor(level, rarity=rarity)
      return (3, Room.NO_CHANGE)
    else:
      logs.append("You do not have enough money or materials.")
      self.crafting = False
      self.crafted_piece = None
      return (0, Room.NO_CHANGE)

  def apply_choice(self, choice_text, logs, character):
    if choice_text == "Keep Current":
      recycle = self.crafted_piece
      self.crafted_piece = None
      self.crafting = False
      logs.append("Recycled %s" % recycle)
      materials = recycle.get_recycled_materials()
      character.gain_materials(materials)
      logs.append("Received %s." % Equipment.materials_string(materials))
      return (0, Room.NO_CHANGE)
    elif choice_text == "Keep New":
      equipment = self.crafted_piece
      recycle = character.equip(equipment)
      self.crafted_piece = None
      self.crafting = False
      logs.append("Recycled %s." % recycle)
      materials = recycle.get_recycled_materials()
      character.gain_materials(materials)
      logs.append("Received %s." % Equipment.materials_string(materials))
      return (0, Room.NO_CHANGE)
    elif choice_text == "Craft Uncommon":
      return self.handle_craft(1, logs, character)
    elif choice_text == "Craft Rare":
      return self.handle_craft(2, logs, character)
    elif choice_text == "Craft Epic":
      return self.handle_craft(3, logs, character)
    elif choice_text == "Leave Shop":
      return (0, Room.LEAVE_ROOM)

  def enter_shop(self, faction_rate):
    self.crafting = False
    self.crafted_piece = None
    self.faction_rate = faction_rate

class Dungeon(Room):
  @classmethod
  def get_name(cls):
    return "Dungeon"

  def get_buttons(self, character):
    return ["Enter Dungeon", "", "", "Never Mind"]

  def get_text(self, character):
    return "Level %d Dungeon" % self.level

  def apply_choice(self, choice_text, logs, character):
    if choice_text == "Enter Dungeon":
      logs.append("You enter the dungeon...")
      return (0, Room.ENTER_DUNGEON)
    elif choice_text == "Never Mind":
      return (0, Room.LEAVE_ROOM)
