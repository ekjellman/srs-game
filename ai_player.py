import game_state
import random

# A (hopefully somewhat smarter) AI player for the game.

# Arbitrary simplifying design decisions with no real reasoning
# -- Strength build with Holy Blade, Auto Life, Swiftness
# -- Only use Inn Bento for items

def town_choice(game):
  # Inn, then Temple, then Dungeon. [Trainer (Gain XP) Forge (Reforge Weapon)
  # Inn (Mysteries Trader) TeleportChamber(Major Teleport, Teleport, Minor Teleport)
  # Temple (Blessing, Purify Rune), Crafthall (Craft Epic?)
  choices = game.get_choices()
  buffs = get_buffs(game)
  if "Inn" in choices and "Well Rested" not in buffs and can_inn(game):
    return "Inn"
  if "Temple" in choices and "Blessed" not in buffs and can_bless(game):
    return "Temple"
  if "Temple" in choices and game.character.runes > 0 and game.character.level < 125:
    return "Temple"
  # TODO: Optimize for Trainer, Forge, Crafthall
  if "Dungeon" in choices:
    return "Dungeon"
  return "Leave Town"

def fully_buffed(game):
  buffs = get_buffs(game)
  return ("Well Rested" in buffs and "Blessed" in buffs) or not can_inn(game)

def can_inn(game):
  return game.character.gold >= (game.floor * 10)

def can_bless(game):
  return game.character.gold >= (game.floor * 50)

def can_offer(game):
  return game.character.gold >= (game.floor * 100)

def can_train(game):
  # TODO
  return game.current_shop.xp_training_cost < game.character.gold

def shop_choice(game):
  shop_type = game.current_shop.get_name()
  if shop_type == "Inn":
    if not can_inn(game):
      return "Leave Inn"
    if "Well Rested" not in get_buffs(game):
      return "Rest"
    if len(game.character.items) < 3:
      return "Buy Food"
    if len(game.character.items) == 3 and "Well Fed" not in get_buffs(game):
      return "Buy Food"
    return "Leave Inn"
  if shop_type == "Temple":
    if "Blessed" not in get_buffs(game) and can_bless(game):
      return "Blessing"
    if game.character.runes > 0 and game.character.level < 125:
      return "Purify Rune"
    if "Lucky" not in get_buffs(game) and can_offer(game):
      return "Offering"
    return "Leave Temple"
  if shop_type == "Trainer":
    if can_train(game):
      return "Gain XP"
    return "Leave Shop"
  if shop_type == "Teleport Chamber":
    level = game.current_shop.level
    if level >= 40: return "Leave Chamber"
    if game.character.materials[2] >= level + 2:
      return "Major Teleport"
    if game.character.materials[1] >= level + 1:
      return "Teleport"
    if game.character.materials[0] >= level:
      return "Minor Teleport"
    return "Leave Chamber"
  if shop_type == "Dungeon":
    return "Enter Dungeon"
  choice = game.get_choices()
  assert "Leave" in choice[3]
  return choice[3]

def get_buffs(game):
  return [b.get_name() for b in game.character.buffs]

def get_skills(game):
  return [s.get_name() for s in game.character.skills]

def get_skill_cost(game, skill):
  for s in game.character.skills:
    if s.get_name() == skill:
      return s.sp_cost()
  assert False

def item_or_explore(game, explore_choice):
  buffs = get_buffs(game)
  if "Well Fed" in buffs:
    return explore_choice
  if len(game.character.items) > 0:
    return "Item"
  return explore_choice

def use_or_never_mind(game):
  buffs = get_buffs(game)
  if "Well Fed" in buffs:
    return "Never Mind"
  if len(game.character.items) > 0:
    return "Use Item #1"
  return "Never Mind"

def score_equipment(item):
  score = 0
  if item.attributes.get("Type", 0) == "Magic": return 0
  score += item.attributes.get("Strength", 0) * 1.0
  score += item.attributes.get("Stamina", 0) * 1.0
  score += item.attributes.get("Speed", 0) * 1.5
  score += item.attributes.get("Intellect", 0) * 0.2
  score += item.attributes.get("Defense", 0) * 0.4
  score += item.attributes.get("Magic Defense", 0) * 0.4
  score += item.attributes.get("Low", 0) * 0.5
  score += item.attributes.get("High", 0) * 0.5
  return score

def play_game():
  game = game_state.GameState()
  skill_to_use = None
  while True:
    current_state = game.current_state()
    choice = None
    choices = game.get_choices()
    if current_state == "VICTORY":
      return game
    elif current_state == "CHAR_CREATE":
      choice = "Strength"
    elif current_state == "RUNE_WORLD":
      choice = item_or_explore(game, "Explore")
    elif current_state == "USE_ITEM":
      choice = use_or_never_mind(game)
    elif current_state == "SUMMIT":
      if game.character.runes > 0 and game.character.level < 125:
        choice = "Town"
      if fully_buffed(game):
        # TODO: Optimize
        chance = (game.character.level - 60) / 40.0
        if random.random() < chance:
          choice = "Stronghold of the Ten"
        else:
          choice = "Infinity Dungeon"
      else:
        choice = "Town"
    elif current_state == "STRONGHOLD":
      choice = item_or_explore(game, "Enter Room")
    elif current_state == "DUNGEON":
      choice = item_or_explore(game, "Explore")
    elif current_state == "LOOT_EQUIPMENT":
      slot = game.equipment_choice.slot
      new_score = score_equipment(game.equipment_choice)
      current_score = score_equipment(game.character.equipment[slot])
      if new_score > current_score:
        choice = "Keep New"
      else:
        choice = "Keep Current"
    elif current_state == "SHOP_WARNING":
      choice = "Enter Room"
    elif current_state == "ACCEPT_QUEST":
      choice = "Accept Quest"
    elif current_state == "TOWN":
      choice = town_choice(game)
    elif current_state == "SHOP":
      choice = shop_choice(game)
    elif current_state == "OUTSIDE":
      # TODO: Optimize.
      if game.character.current_hp < game.character.max_hp:
        choice = "Town"
      elif game.character.current_sp < game.character.max_sp:
        choice = "Town"
      elif "Quest" in choices:
        choice = "Quest"
      else:
        choice = "Ascend Tower"
      if choice not in choices:  # Tower not unlocked
        choice = "Town"
    elif current_state == "QUEST":
      if "Complete Quest" in choices:
        choice = "Complete Quest"
      elif "Well Fed" not in get_buffs(game) and len(game.character.items) > 0:
        choice = "Item"
      else:
        choice = "Continue Quest"
    elif current_state == "COMBAT":
      if "Auto Life" not in get_buffs(game) and "Auto Life" in get_skills(game):
        if get_skill_cost(game, "Auto Life") <= game.character.current_sp:
          skill_to_use = "Auto Life"
          choice = "Skill"
      elif game.monster.boss:
        if "Swiftness" not in get_buffs(game) and "Swiftness" in get_skills(game):
          if get_skill_cost(game, "Swiftness") <= game.character.current_sp:
            skill_to_use = "Swiftness"
            choice = "Skill"
        elif "Holy Blade" in get_skills(game):
          if get_skill_cost(game, "Holy Blade") <= game.character.current_sp:
            skill_to_use = "Holy Blade"
            choice = "Skill"
      if choice is None:
        choice = "Attack"
    elif current_state == "LEVEL_UP":
      priority = ["Clarity of Mind", "Beefy", "Stocky", "Mental Toughness",
                  "Quick Learner", "Combobreaker!", "Regeneration",
                  "Get New Traits", "Perserverance", "Sneaky",
                  "Merchant Warrior", "Self-Improvement", "Wizardry",
                  "Libra", "Scholar"]
      for trait in priority:
        if trait in choices:
          choice = trait
          break
    elif current_state == "LEVEL_UP_SKILL":
      priority = ["Auto Life", "Holy Blade", "Swiftness", "Improve stats"]
      if len(game.character.skills) != 3:
        for skill in priority:
          if skill in choices and skill not in get_skills(game):
            choice = skill
            break
      else:
        for skill in game.character.skills:
          cost = skill.sp_cost()
          ratio = game.character.max_sp / cost
          if ratio > 20:
            choice = skill.get_name()
            break
        if choice is None:
          choice = "Improve stats"
    elif current_state == "USE_SKILL":
      choice = skill_to_use
      skill_to_use = None
    elif current_state == "TOWER":
      choice = item_or_explore(game, "Explore")
    else:
      print "Failed: ", current_state
      assert False
    if game.time_spent > 15000:
      print current_state, choice, game.floor, game.time_spent
    assert choice is not None
    logs = game.verification_apply_choice(choice)

if __name__ == "__main__":
  game = play_game() 
  print game.character
  print "Time: ", game.time_spent
