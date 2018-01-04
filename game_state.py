"""Represents the current state of the game. Main game logic module."""
import random
from character import Character, TRAITS
from monster import Monster
from combat import Combat
from equipment import Equipment
from quest import Quest
import rooms
from items import Item
import skills

# TODO: Start here: Write Jolt Cup-level external docs
# TODO: Log more. Certainly including victory
# TODO: Equipment keeping predictor?

TOWN_BUILDINGS = [rooms.ArmorShop, rooms.Enchanter, rooms.Forge,
                  rooms.Alchemist, rooms.TrainingRoom, rooms.Temple,
                  rooms.Inn, rooms.WeaponShop, rooms.Dungeon, rooms.Crafthall,
                  rooms.Jeweler]

TOWER_BUILDINGS = [rooms.ArmorShop, rooms.Enchanter, rooms.Forge,
                   rooms.Alchemist, rooms.TrainingRoom, rooms.Temple,
                   rooms.Inn, rooms.WeaponShop, rooms.Crafthall,
                   rooms.Jeweler, rooms.RareGoodsShop]

CHOICES = {"CHAR_CREATE": ["Strength", "Stamina", "Speed", "Intellect"],
           "RUNE_WORLD": ["Explore", "", "Item", "Leave Rune"],
           "TOWER": ["Explore", "Rest", "Item", "Leave Tower"],
           "SUMMIT": ["Stronghold of the Ten", "Infinity Dungeon", "Town",
                      "Descend Tower"],
           "STRONGHOLD": ["Enter Room", "Rest", "Item", "Leave Stronghold"],
           "DUNGEON": ["Explore", "Rest", "Item", "Leave Dungeon"],
           "LOOT_EQUIPMENT": ["", "Keep Current", "Keep New", ""],
           "VICTORY": [""] * 4,
           "ACCEPT_QUEST": ["", "Accept Quest", "Decline Quest", ""]}

#                           Hoard,Shop,Chest,Boss,Teleport
EXPLORE_CHANCES = {"Tower": [.01, .02, .15, .04, .01],
                   "Dungeon": [.02, .00, .20, .05, .02],
                   "Infinity Dungeon": [.03, .03, .25, .06, .00]}

DEATH_TIME_FACTOR = {"TOWER": 1.0, "QUEST": 0.5, "DUNGEON": 0.7,
                     "STRONGHOLD": 1.5, "RUNE_WORLD": 0.0}

TOWER_LEVELS = 40
UPDATE_TIME = 360
DEBUG_FLOOR = None
DEBUG_BUILDING = None
DEBUG_GOLD = None
DEBUG_MATERIALS = None
DEBUG_CHARACTER = None
DEBUG_TOWER_START = None

#DEBUG_BUILDING = rooms.TeleportChamber
DEBUG_FLOOR = 39
DEBUG_GOLD = 100000
DEBUG_MATERIALS = [100, 100, 100, 100, 100]
DEBUG_CHARACTER = 70
DEBUG_TOWER_START = 39

# TODO: http://www.pyinstaller.org/ to get packages
# TODO: It is probably not best to be passing logs around to everything?
#       it could be part of the GameState, or we could use a logger for real
# TODO: add traits to weapons/armor
# TODO: Add an "acknowledgement" state, to make certain uncommon states harder
#       to skip past (levelling up, finding a shop in a tower, etc)
# TODO: Add a few options boxes. One in particular to "value" stats, so you can
#       quickly get a value for whether a piece of equipment is better or not
#       Maybe one for name, too, eh?

# Game Balance notes:
# -- Make it so dying in a quest and dungeon takes less time than in the Tower
#    That allows the player to use the quest as a guide to whether they should
#    attempt the tower, somewhat.
# -- Is there any way to have a build that doesn't require a heal? This is a
#    real weakness to physical builds right now.
# To Test:
# -- Max buff percentage? (like say 50%)

# -- Floating point error on buffs. (39% for 9 turns at level 2)

class GameState(object):
  """
    GameState represents all the state for the current game, and functions for
    interacting with the GameState.

    In general, the GameState is updated by the player making one of four
    choices, and the UI will then call GameState.apply_choice, which updates
    the GameState.
  """
  def __init__(self):
    self.state = ["CHAR_CREATE"]
    self.character = Character()
    if DEBUG_GOLD:
      self.character.gold = DEBUG_GOLD
    self.floor = 1
    self.frontier = 1
    self.time_spent = 0
    self.energy = 200
    self.towns = self.generate_towns()
    self.tower_lock = [True] * (TOWER_LEVELS + 1)
    self.tower_lock[1] = False
    self.tower_faction = [1.0] * (TOWER_LEVELS + 1)
    self.tower_update_ready = False
    self.tower_quests = self.generate_quests()
    # Number of encounters remaining in current tower ascension
    self.ascension_encounters = 0
    self.current_shop = None
    # Monster currently in combat with
    self.monster = None
    self.quest = None
    # When we defeat a monster, treasure goes here so we can handle it a piece
    # at a time
    self.treasure_queue = []
    self.equipment_choice = None
    self.rune_level = -1
    self.levelups = 0
    self.skillups = 0
    self.skills_used = set()
    self.skill_choices = []
    self.trait_choices = []
    self.infinity_dungeon = False
    self.stronghold_room = 0
    if DEBUG_TOWER_START:
      self.frontier = DEBUG_TOWER_START
      self.floor = DEBUG_TOWER_START
      for i in range(self.frontier):
        self.tower_lock[i] = False

  ###
  # Helper methods for changing state
  ###

  @staticmethod
  def generate_quests():
    quests = [None]
    for i in range(1, TOWER_LEVELS + 1):
      quests.append(Quest(i))
    return quests

  @staticmethod
  def generate_towns():
    # Level 0 does not exist
    tower = [None]
    for level in range(1, TOWER_LEVELS):
      shop_set = set()
      while len(shop_set) < 3:
        shop_set.add(random.choice(TOWN_BUILDINGS))
      shops = []
      for shop in shop_set:
        shops.append(shop(level))
      tower.append(shops)
    if DEBUG_BUILDING:
      tower[DEBUG_FLOOR][0] = DEBUG_BUILDING(DEBUG_FLOOR)
    summit_shops = [rooms.Inn(TOWER_LEVELS), rooms.Temple(TOWER_LEVELS),
                    rooms.Crafthall(TOWER_LEVELS)]
    tower.append(summit_shops)
    base_floor_shops = [rooms.Inn(1), rooms.Temple(1), rooms.Alchemist(1)]
    tower[1] = base_floor_shops
    return tower

  def tower_update(self):
    self.tower_quests = self.generate_quests()
    for level in range(1, TOWER_LEVELS + 1):
      for shop in range(3):
        self.towns[level][shop].refresh()

  def time_to_refresh(self):
    return UPDATE_TIME - (self.time_spent % UPDATE_TIME)

  def pass_time(self, amount, logs):
    old_period = self.time_spent // UPDATE_TIME
    if self.rune_level == -1:
      self.time_spent += amount
    new_period = self.time_spent // UPDATE_TIME
    if old_period != new_period:
      self.tower_update_ready = True
      logs.append("The tower is ready to update.")
    self.character.pass_time(amount)
    if self.monster:
      self.monster.pass_time(amount)

  def current_state(self):
    """Return the current state."""
    return self.state[-1]

  def faction_update(self, base_floor):
    for floor in range(max(1, base_floor - 4),
                        min(base_floor + 4, TOWER_LEVELS) + 1):
      difference = abs(floor - base_floor)
      multiplier = .95 + (.01 * difference)
      assert .94 < multiplier < 1.0
      self.tower_faction[floor] *= multiplier

  def get_choices(self):
    """Return choices for next actions for the UI."""
    current_state = self.current_state()
    if current_state in CHOICES:
      return CHOICES[current_state]
    if current_state == "TOWN":
      choices = ["Leave Town"]
      choices.extend([shop.get_name() for shop in self.towns[self.floor]])
      return choices
    elif current_state == "SHOP":
      return self.current_shop.get_buttons(self.character)
    elif current_state == "OUTSIDE":
      choices = []
      choices.append("" if self.tower_lock[self.floor] else "Ascend Tower")
      choices.append("Quest" if self.tower_quests[self.floor] else "")
      choices.append("Town")
      choices.append("Descend Tower")
      return choices
    elif current_state == "QUEST":
      if self.quest.complete():
        return ["Complete Quest", "", "", "Leave Quest"]
      else:
        return ["Continue Quest", "Rest", "Item", "Leave Quest"]
    elif current_state == "COMBAT":
      if self.monster.boss or self.infinity_dungeon or self.rune_level != -1:
        return ["Attack", "Skill", "Item", ""]
      else:
        return ["Attack", "Skill", "Item", "Escape"]
    elif current_state == "USE_ITEM":
      choices = []
      for i in range(len(self.character.items)):
        choices.append("Use Item #{}".format(i + 1))
      while len(choices) < 3:
        choices.insert(0, "")
      choices.append("Never Mind")
      return choices
    elif current_state == "LEVEL_UP":
      return self.trait_choices
    elif current_state == "LEVEL_UP_SKILL":
      return self.skill_choices
      # Next: Handle the trait choice, then implement the traits
    elif current_state == "USE_SKILL":
      choices = [""] * (3 - len(self.character.skills))
      for skill in self.character.skills:
        if (skill.sp_cost() > self.character.current_sp or
            (skill.once_per_battle() and skill.get_name() in self.skills_used)):
          choices.append("")
        else:
          choices.append(skill.get_name())
      choices.append("Never Mind")
      return choices
    else:
      return ["Error", "Error", "Error", "Error"]

  def handle_treasure(self, logs):
    while self.treasure_queue:
      item = self.treasure_queue.pop()
      if isinstance(item, int):
        amount_gained = self.character.gain_gold(item)
        logs.append("You got {} gold.".format(amount_gained))
      elif isinstance(item, Equipment):
        logs.append("You got the following equipment:")
        logs.append(str(item))
        self.add_state("LOOT_EQUIPMENT")
        self.equipment_choice = item
        break  # Have to give choice to player
      elif item == "Rune":
        logs.append("You found a corrupted rune!")
        self.character.runes += 1
      else:
        assert False

  def handle_rune_completion(self, logs):
    if self.rune_level == 0:
      logs.append("Unpurified, the rune dissolves into dust.")
      return
    item = Equipment.get_new_armor(self.rune_level, slot=4, rarity=4)
    self.treasure_queue.append(item)
    self.rune_level = -1
    self.handle_treasure(logs)

  ###
  # Helper methods for changing state
  ###

  def state_change_checks(self):
    if self.current_state() == "TOWN":
      self.character.restore_hp()
      self.character.restore_sp()
      if self.tower_lock[self.floor]:
        self.tower_lock[self.floor] = False
    if self.current_state() == "OUTSIDE" or self.current_state == "TOWN":
      if self.tower_update_ready:
        self.tower_update()
        self.tower_update_ready = False

  def change_state(self, state):
    self.state.pop()
    self.state.append(state)
    self.state_change_checks()

  def add_state(self, state):
    self.state.append(state)
    self.state_change_checks()

  def set_state(self, state):
    self.state = [state]
    self.state_change_checks()

  def leave_state(self):
    self.state.pop()
    self.state_change_checks()

  ###
  # Methods for applying choices in various states
  ###

  def apply_choice_char_create(self, logs, choice_text):
    if DEBUG_CHARACTER:
      self.character = Character.debug_character(DEBUG_CHARACTER, choice_text)
      self.character.runes = 5
    else:
      self.character.make_initial_equipment(choice_text)
    if DEBUG_MATERIALS:
      self.character.materials = DEBUG_MATERIALS
    if DEBUG_GOLD:
      self.character.gold = DEBUG_GOLD
    logs.append("Generated {} starting equipment.".format(choice_text))
    self.change_state("TOWN")

  def start_combat(self, logs, boss_chance, level=None):
    if level is None:
      level = self.floor
    boss = random.random() < boss_chance
    self.add_state("COMBAT")
    self.monster = Monster(level, boss)
    logs.append("You have encountered a monster.")

  def apply_choice_rune_world(self, logs, choice_text):
    if choice_text == "Explore":
      self.rune_level += 1
      self.start_combat(logs, .1, self.rune_level)
    elif choice_text == "Item":
      self.pass_time(0, logs)
      self.add_state("USE_ITEM")
    elif choice_text == "Leave Rune":
      self.pass_time(0, logs)
      self.leave_state()
      logs.append("You leave the world of the rune.")
      self.handle_rune_completion(logs)

  def apply_choice_accept_quest(self, logs, choice_text):
    if choice_text == "Accept Quest":
      self.change_state("QUEST")
      logs.append("You accept the quest.")
    elif choice_text == "Decline Quest":
      self.quest = None
      self.leave_state()
      logs.append("You decline the quest.")

  def apply_choice_use_item(self, logs, choice_text):
    if choice_text.startswith("Use Item #"):
      self.pass_time(0, logs)
      choice = int(choice_text[-1])
      assert choice > 0
      choice -= 1
      item = self.character.items.pop(choice)
      result = item.apply(self.character, self.monster, logs)
      if result == Item.UNUSABLE:
        logs.append("You can't use that item right now.")
        self.character.items.append(item)
      else:
        self.leave_state()
    elif choice_text == "Never Mind":
      self.pass_time(0, logs)
      self.leave_state()

  def apply_choice_quest(self, logs, choice_text):
    if choice_text == "Continue Quest":
      self.pass_time(random.randint(1, 3), logs)
      logs.append("You continue the quest...")
      self.add_state("COMBAT")
      self.monster = self.quest.get_monster()
      logs.append("You have encountered a monster.")
    elif choice_text == "Rest":
      self.rest(logs)
    elif choice_text == "Item":
      self.pass_time(0, logs)
      self.add_state("USE_ITEM")
    elif choice_text == "Leave Quest":
      self.pass_time(1, logs)
      self.leave_state()
    elif choice_text == "Complete Quest":
      logs.append("You have completed the quest.")
      amount_gained = self.character.gain_gold(self.quest.gp_reward)
      logs.append("You gain {} gold.".format(amount_gained))
      levelups = self.character.gain_exp(self.quest.xp_reward, self.floor, logs,
                                         level_adjust=False)
      self.treasure_queue = self.quest.get_treasure()
      self.faction_update(self.floor)
      # Fixes a bug when the tower update is pending
      regenerate_quest = self.tower_update_ready
      self.leave_state()
      if self.current_state() == "OUTSIDE":
        if regenerate_quest:
          self.tower_quests[self.floor] = Quest(self.floor)
        else:
          self.tower_quests[self.floor] = None
      if levelups > 0:
        self.levelups = levelups
        self.skillups = levelups
        self.trait_choices = self.character.get_trait_choices()
        self.skill_choices = self.character.get_skill_choices()
        self.add_state("LEVEL_UP")
      self.handle_treasure(logs)

  def rest(self, logs, enc_chance=False):
    """Rest to restore HP and possibly encounter a monster."""
    self.pass_time(5, logs)
    hp_gained = self.character.rest()
    logs.append("You rest and regain {} HP.".format(hp_gained))
    if enc_chance:
        if random.random() < .2 or self.infinity_dungeon:
            self.start_combat(logs, .1)

  def apply_choice_stronghold(self, logs, choice_text):
    if choice_text == "Enter Room":
      level = TOWER_LEVELS - 10 + (self.stronghold_room * 5)
      self.start_combat(logs, 1.0, level)
    elif choice_text == "Rest":
      self.rest(logs) # Cannot get attacked resting here
    elif choice_text == "Item":
      self.pass_time(0, logs)
      self.add_state("USE_ITEM")
    elif choice_text == "Leave Stronghold":
      self.pass_time(10, logs)
      logs.append("You leave the Stronghold of the Ten.")
      self.leave_state()

  def handle_explore(self, logs, explore_type):
    chances = EXPLORE_CHANCES[explore_type]
    random_number = random.random()
    if random_number < chances[0]:
      logs.append("You find a treasure hoard!")
      self.find_treasure(logs, 8)
    elif random_number < sum(chances[0:2]):
      logs.append("You find a shop.")
      self.character.restore_hp()
      self.character.restore_sp()
      shop = random.choice(TOWER_BUILDINGS)(self.floor)
      self.add_state("SHOP")
      self.current_shop = shop
      if self.floor > TOWER_LEVELS:  # Infinity Dungeon
        faction = 1.0
      else:
        faction = self.tower_faction[self.floor]
      shop.enter_shop(faction)
    elif random_number < sum(chances[0:3]):
      logs.append("You find a treasure chest!")
      self.find_treasure(logs, 1)
    elif random_number < sum(chances[0:4]):
      self.start_combat(logs, 1.0)  # Boss monster
    elif random_number < sum(chances):
      logs.append("You find a teleport chamber.")
      self.character.restore_hp()
      self.character.restore_sp()
      chamber = rooms.TeleportChamber(self.floor)
      self.add_state("SHOP")
      self.current_shop = chamber
    else:
      if explore_type == "Tower" and "Sneaky" in self.character.traits:
        sneak_chance = self.character.traits["Sneaky"] * 0.02
        if random.random() < sneak_chance:
          logs.append("You encountered a monster, but sneaked past.")
          return
      self.start_combat(logs, 0.0)

  def apply_choice_tower(self, logs, choice_text):
    if choice_text == "Explore":
      self.pass_time(random.randint(1, 10), logs)
      logs.append("You explore the tower...")
      if self.ascension_encounters > 0:
        self.ascension_encounters -= 1
        self.handle_explore(logs, "Tower")
      elif self.ascension_encounters == 0:
        self.ascension_encounters -= 1
        self.start_combat(logs, 1.0)  # Floor boss
      else:
        assert self.ascension_encounters == -1
        self.floor += 1
        self.frontier = max(self.frontier, self.floor)
        logs.append("Congratulations, you have reached floor {}!".format(self.floor))
        if self.floor < TOWER_LEVELS:
          self.leave_state()
          self.change_state("OUTSIDE")
        elif self.floor == TOWER_LEVELS:
          self.leave_state()
          self.change_state("SUMMIT")
        else:
          assert False
    elif choice_text == "Rest":
      self.rest(logs, True) # May get attacked resting here
    elif choice_text == "Item":
      self.pass_time(0, logs)
      self.add_state("USE_ITEM")
    elif choice_text == "Leave Tower":
      self.pass_time(10, logs)
      logs.append("You leave the tower.")
      self.change_state("OUTSIDE")

  def find_treasure(self, logs, item_count):
    treasure = []
    for i in range(item_count):
      if random.random() < .7:
        min_gold = self.floor * 10
        max_gold = self.floor * 20
        treasure.append(random.randint(min_gold, max_gold))
      else:
        rarity = min(random.randint(1, 4) for _ in range(4))
        if self.infinity_dungeon:
          rarity = max(rarity, min(random.randint(1, 4) for _ in range(4)))
        level = max(1, int(self.floor + random.gauss(0, 1)))
        treasure.append(Equipment.get_new_armor(level, None, None, rarity))
    self.treasure_queue = treasure
    self.handle_treasure(logs)

  def apply_choice_dungeon(self, logs, choice_text):
    if choice_text == "Explore":
      if self.infinity_dungeon:
        self.floor += 1
      self.pass_time(random.randint(1, 5), logs)
      logs.append("You explore the dungeon...")
      if self.infinity_dungeon:
        self.handle_explore(logs, "Infinity Dungeon")
      else:
        self.handle_explore(logs, "Dungeon")
    elif choice_text == "Rest":
      self.rest(logs, True) # May get attacked resting here
    elif choice_text == "Item":
      self.pass_time(0, logs)
      self.add_state("USE_ITEM")
    elif choice_text == "Leave Dungeon":
      self.pass_time(5, logs)
      logs.append("You leave the dungeon.")
      if self.infinity_dungeon:
        self.infinity_dungeon = False
        self.floor = TOWER_LEVELS
        self.leave_state()
        self.change_state("SUMMIT")
      else:
        self.leave_state()

  def apply_death(self, logs):
    self.leave_state()  # COMBAT
    self.monster.buffs = []
    self.monster.debuffs = []
    self.skills_used = set()
    self.monster = None
    if self.floor > TOWER_LEVELS:
      self.floor = TOWER_LEVELS
    if self.current_state() == "RUNE_WORLD":
      self.leave_state()
      self.character.apply_death(logs, penalty=False)
      self.handle_rune_completion(logs)
      return
    state = self.current_state()
    self.leave_state()  # Wherever they died
    if self.current_state() == "SHOP":
      self.current_shop = None
      self.leave_state()
    self.character.apply_death(logs)
    self.change_state("TOWN")
    factor = DEATH_TIME_FACTOR[state]
    time_lost = random.randint(1, int(3 * self.floor * factor))
    self.pass_time(time_lost, logs)
    logs.append("You lost {} time units.".format(time_lost))

  def dungeon_victory_update(self, base_floor):
    if self.infinity_dungeon:
      return
    for floor in range(max(1, base_floor - 3),
                        min(base_floor + 3, TOWER_LEVELS) + 1):
      difference = abs(floor - base_floor)
      multiplier = 1.0 - (.008 / (2 ** abs(difference)))
      assert .992 <= multiplier < 1.0
      self.tower_faction[floor] *= multiplier

  def handle_combat_result(self, logs, result):
    if result == Combat.CHARACTER_DEAD:
      self.apply_death(logs)
    elif result == Combat.MONSTER_DEAD:
      self.skills_used = set()
      logs.append("You have defeated {}!".format(self.monster.name))
      levelups = self.character.gain_exp(self.monster.calculate_exp(),
                                         self.monster.level, logs)
      self.treasure_queue = self.monster.get_treasure(self.infinity_dungeon)
      self.monster = None
      self.leave_state()
      if self.current_state() == "QUEST":
        self.quest.defeat_monster()
      if self.current_state() == "DUNGEON":
        self.dungeon_victory_update(self.floor)
      if self.current_state() == "STRONGHOLD":
        self.stronghold_room += 1
        if self.stronghold_room == 10:
          self.change_state("VICTORY")
      if levelups > 0:
        self.levelups = levelups
        self.skillups = levelups
        self.trait_choices = self.character.get_trait_choices()
        self.skill_choices = self.character.get_skill_choices()
        self.add_state("LEVEL_UP")
      self.handle_treasure(logs)

  def apply_choice_combat(self, logs, choice_text):
    if choice_text == "Attack":
      result = Combat.perform_turn("Attack", None, self.character, self.monster,
                                   logs)
      self.pass_time(1, logs)
      self.handle_combat_result(logs, result)
    elif choice_text == "Skill":
      self.add_state("USE_SKILL")
    elif choice_text == "Item":
      self.pass_time(0, logs)
      self.add_state("USE_ITEM")
    elif choice_text == "Escape":
      logs.append("You attempt to escape...")
      result = Combat.perform_turn("Escape", None, self.character, self.monster,
                                   logs)
      self.pass_time(1, logs)
      if result == Combat.CHARACTER_DEAD:
        self.apply_death(logs)
      elif result == Combat.CHARACTER_ESCAPED:
        logs.append("You escaped successfully!")
        self.monster = None
        self.leave_state()

  def apply_choice_use_skill(self, logs, choice_text):
    if choice_text == "Never Mind":
      self.leave_state()
    else:
      for skill in self.character.skills:
        if skill.get_name() == choice_text:
          self.leave_state()  # USE_SKILL
          self.character.current_sp -= skill.sp_cost()
          result = Combat.perform_turn("Skill", skill, self.character,
                                       self.monster, logs)
          self.pass_time(1, logs)
          self.skills_used.add(choice_text)
          self.handle_combat_result(logs, result)
          break
      else:
        assert False

  def apply_choice_level_up(self, logs, choice_text):
    assert self.levelups > 0
    learned = self.character.learn_trait(choice_text)
    if learned:
      self.levelups -= 1
      if self.levelups == 0:
        self.change_state("LEVEL_UP_SKILL")
      else:
        self.trait_choices = self.character.get_trait_choices()

  def apply_choice_level_up_skill(self, logs, choice_text):
    assert self.skillups > 0
    learned = self.character.learn_skill(choice_text)
    if learned:
      self.skillups -= 1
      if self.skillups == 0:
        self.leave_state()
      else:
        self.skill_choices = self.character.get_skill_choices()

  def apply_choice_town(self, logs, choice_text):
    if choice_text == "Leave Town":
      self.pass_time(2, logs)
      if self.floor == TOWER_LEVELS:
        self.change_state("SUMMIT")
      else:
        self.change_state("OUTSIDE")
      logs.append("You left the town.")
    else:
      shop = None
      for shop in self.towns[self.floor]:
        if shop.get_name() == choice_text:
          self.current_shop = shop
          break
      if shop:
        self.pass_time(1, logs)
        logs.append("You went to the {}.".format(shop.get_name()))
        self.add_state("SHOP")
        shop.enter_shop(self.tower_faction[self.floor])

  def apply_choice_shop(self, logs, choice_text):
    time_cost, result = self.current_shop.apply_choice(choice_text, logs,
                                                       self.character)
    self.pass_time(time_cost, logs)
    if result == self.current_shop.LEAVE_ROOM:
      self.leave_state()
    elif result == self.current_shop.NO_CHANGE:
      pass
    elif result == self.current_shop.USE_ITEM:
      self.add_state("USE_ITEM")
    elif result == self.current_shop.PURIFY_RUNE:
      self.character.runes -= 1
      self.rune_level = 0
      self.add_state("RUNE_WORLD")
    elif result == self.current_shop.ENTER_DUNGEON:
      self.add_state("DUNGEON")
    elif result == self.current_shop.LEVEL_UP:
      self.levelups = 1
      self.skillups = 1
      self.trait_choices = self.character.get_trait_choices()
      self.skill_choices = self.character.get_skill_choices()
      self.add_state("LEVEL_UP")
    elif result == self.current_shop.MINOR_TELEPORT:
      self.teleport(1)
    elif result == self.current_shop.TELEPORT:
      self.teleport(2)
    elif result == self.current_shop.MAJOR_TELEPORT:
      self.teleport(3)
    else:
      assert False

  def teleport(self, floors):
    self.floor += floors
    self.floor = min(TOWER_LEVELS, self.floor)
    self.frontier = max(self.frontier, self.floor)
    for i in range(self.floor, max(1, self.floor - floors - 1), -1):
      self.tower_lock[i] = False
    self.set_state("TOWN")
    self.ascension_encounters = 0
    self.current_shop = None

  def apply_choice_summit(self, logs, choice_text):
    if choice_text == "Stronghold of the Ten":
      self.add_state("STRONGHOLD")
      self.stronghold_room = 0
    elif choice_text == "Infinity Dungeon":
      self.infinity_dungeon = True
      self.add_state("DUNGEON")
    elif choice_text == "Town":
      self.pass_time(5, logs)
      self.change_state("TOWN")
      logs.append("You went to the town.")
    elif choice_text == "Descend Tower":
      self.pass_time(10, logs)
      self.floor -= 1  # Bug if there's only one floor, I guess.
      self.change_state("OUTSIDE")
      logs.append("You descended to floor {}.".format(self.floor))


  def apply_choice_outside(self, logs, choice_text):
    if choice_text == "Ascend Tower":
      self.pass_time(10, logs)
      if self.frontier <= self.floor:
        self.add_state("TOWER")
        self.ascension_encounters = random.randint(5, 8)
        logs.append("You entered the tower.")
      else:
        self.floor += 1
        logs.append("You ascended to floor {}.".format(self.floor))
        if self.floor == TOWER_LEVELS:
          self.change_state("SUMMIT")
    elif choice_text == "Quest":
      self.pass_time(5, logs)
      self.add_state("ACCEPT_QUEST")
      logs.append("You look for a quest giver.")
      self.quest = self.tower_quests[self.floor]
    elif choice_text == "Town":
      self.pass_time(5, logs)
      self.change_state("TOWN")
      logs.append("You went to the town.")
    elif choice_text == "Descend Tower":
      self.pass_time(10, logs)
      if self.floor > 1:
        self.floor -= 1
        logs.append("You descended to floor {}.".format(self.floor))
      else:
        logs.append("Cannot descend while on floor 1.")

  def apply_choice_loot_equipment(self, logs, choice_text):
    if choice_text == "Keep Current":
      recycle = self.equipment_choice
    elif choice_text == "Keep New":
      recycle = self.character.equip(self.equipment_choice)
      self.equipment_choice = None
    logs.append("You recycled {} for materials.".format(recycle))
    materials = recycle.get_recycled_materials()
    self.character.gain_materials(materials)
    logs.append("It turned into {}.".format(Equipment.materials_string(materials)))
    # Add materials to character, add materials inventory to character string
    self.leave_state()
    self.handle_treasure(logs)

  def apply_choice(self, choice):
    """Apply the given action choice to this gamestate, modifying it."""
    logs = []
    current_state = self.current_state()
    choice_text = self.get_choices()[choice]
    method_name = "apply_choice_" + current_state.lower()
    try:
      method = getattr(GameState, method_name)
      method(self, logs, choice_text)
    #except AttributeError as exc:
    except IOError as exc:
      print(exc)  # pylint: disable=print-statement
      logs.append("apply_choice not implemented yet, state: {}".format(current_state))
    return logs

  def loot_choice_text(self):
    slot = self.equipment_choice.slot
    return Equipment.equipment_comparison_text(self.character.equipment[slot],
                                               self.equipment_choice)

  def use_item_text(self):
    pieces = []
    for i, item in enumerate(self.character.items):
      pieces.append("Use Item #{}: {}".format(i + 1, item.get_name()))
    return "\n".join(pieces)

  def trait_text(self):
    pieces = []
    pieces.append("Select a trait.")
    choices = self.get_choices()
    for choice in choices:
      if choice in TRAITS:
        pieces.append("{}: {}".format(choice, TRAITS[choice]))
    return "\n".join(pieces)

  def skill_text(self):
    pieces = []
    pieces.append("Select a skill.")
    pieces.extend(self.get_choices())
    return "\n".join(pieces)

  def skill_select_text(self):
    pieces = []
    for skill in self.character.skills:
      insufficient_sp = ("" if self.character.current_sp >= skill.sp_cost()
                         else " (Insufficient SP)")
      if skill.once_per_battle() and skill.get_name() in self.skills_used:
        already_used = "(Already Used)"
      else:
        already_used = ""
      pieces.append("{}: {} sp {}{}\n{}".format(skill.get_name(), skill.sp_cost(),
                                            insufficient_sp, already_used,
                                            skill.get_description()))
    return "\n".join(pieces)

  def combat_text(self):
    buffs = ", ".join(str(buff) for buff in self.character.buffs)
    buffs = buffs or "None"
    libra_string = self.monster.libra_string(self.character.traits.get("Libra", 0))
    return "Your HP: {}\nBuffs: {}\n\n{}".format(self.character.colored_hp(),
                                             buffs, libra_string)

  def panel_text(self):
    """Return text to display to the player about the current game state."""
    # TODO: Add explanations for menu choices, as well.
    current_state = self.current_state()
    if current_state == "CHAR_CREATE":
      return "Please choose the starting specialization for your character."
    elif current_state == "TOWN":
      return "You are in the town on tower level {}.".format(self.floor)
    elif current_state == "OUTSIDE":
      return "You are outside the town on tower level {}.".format(self.floor)
    elif current_state == "SUMMIT":
      return "You stand at the summit of the tower."
    elif current_state == "TOWER":
      return "You are inside the tower, ascending to level {}.".format(self.floor + 1)
    elif current_state == "COMBAT":
      return self.combat_text()
    elif current_state == "LOOT_EQUIPMENT":
      return self.loot_choice_text()
    elif current_state == "ACCEPT_QUEST" or current_state == "QUEST":
      return str(self.tower_quests[self.floor])
    elif current_state == "SHOP":
      return self.current_shop.get_text(self.character)
    elif current_state == "USE_ITEM":
      return self.use_item_text()
    elif current_state == "RUNE_WORLD":
      return "You are in level {} of the rune world.".format(self.rune_level + 1)
    elif current_state == "DUNGEON":
      return "You are in level {} of the dungeon.".format(self.floor)
    elif current_state == "LEVEL_UP":
      return self.trait_text()
    elif current_state == "LEVEL_UP_SKILL":
      return self.skill_text()
    elif current_state == "USE_SKILL":
      return self.skill_select_text()
    elif current_state == "STRONGHOLD":
      return "You are in the Stronghold of the Ten: Room {}.".format(self.stronghold_room + 1)
    elif current_state == "VICTORY":
      return "You win! Victory Time: {}.".format(self.time_spent)
    else:
      return "Error, no text for state {}".format(current_state)
