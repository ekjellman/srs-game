import random
from effect import Effect
from monster import Monster

class Combat(object):
  CHARACTER_DEAD = 0
  MONSTER_DEAD = 1
  CHARACTER_TURN = 2
  MONSTER_TURN = 3
  TARGET_DEAD = 4
  TARGET_ALIVE = 5
  ACTOR_SUCCEEDED = 6
  ACTOR_FAILED = 7
  CHARACTER_ESCAPED = 8
  MONSTER_ESCAPED = 9
  ACTOR_ESCAPED = 10
  ACTOR_TURN = 11

  @classmethod
  def perform_turn(cls, action, info, character, monster, logs):
    # Character action
    result = cls.perform_action(action, info, character, monster, logs)
    if result == cls.TARGET_DEAD:
      return cls.MONSTER_DEAD
    elif result == cls.ACTOR_ESCAPED:
      return cls.CHARACTER_ESCAPED

    if result == Combat.ACTOR_TURN:
      next_turn = cls.CHARACTER_TURN
    else:
      next_turn = cls.get_next_actor(character, monster)

    combobreaker_chance = 0.0
    while next_turn == cls.MONSTER_TURN:
      if Effect.get_combined_impact("Stunned", monster.buffs,
                                    monster.debuffs) > 0:
        logs.append("{} is stunned".format(monster.name))
        return cls.CHARACTER_TURN
      action, info = monster.get_action(character)
      result = cls.perform_action(action, info, monster, character, logs)
      if result == cls.TARGET_DEAD:
        if Effect.get_combined_impact("Immortal", character.buffs,
                                      character.debuffs) > 0:
          logs.append("You survive due to Last Stand")
          character.current_hp = 1
        elif Effect.get_combined_impact("Auto Life", character.buffs,
                                        character.debuffs) > 0:
          logs.append("Your Auto Life effect restored your HP")
          effect = Effect.get_combined_impact("Auto Life", character.buffs,
                                              character.debuffs)
          character.current_hp = 1
          character.restore_hp(effect - 1)
          # TODO: Fix cohesion
          for buff in character.buffs:
            if buff.get_name() == "Auto Life":
              buff.duration = 0
        else:
          death_chance = 0.95 ** character.traits.get("Perseverance", 0)
          if random.random() < death_chance:
            return cls.CHARACTER_DEAD
          else:
            logs.append("Your perseverance saved you from death.")
            character.current_hp = 1
      elif result == cls.ACTOR_ESCAPED:
        return cls.MONSTER_ESCAPED
      next_turn = cls.get_next_actor(character, monster)
      # Combobreaker
      if next_turn == cls.MONSTER_TURN:
        if random.random() < combobreaker_chance:
          next_turn = cls.CHARACTER_TURN
          logs.append("Combobreaker! prevented the next enemy turn")
      combobreaker_chance += character.traits.get("Combobreaker!", 0) / 100.0
    return cls.CHARACTER_TURN

  @classmethod
  def perform_action(cls, action, info, actor, target, logs):
    """Performs an action. Returns if target died."""
    try:
      method_name = "action_" + action.lower()
      method = getattr(Combat, method_name)
      return method(info, actor, target, logs)
    except AttributeError as exc:
      print(exc)
      logs.append("Combat option {} not implemented".format(action))
      return cls.TARGET_ALIVE

  @classmethod
  def apply_damage(cls, target, damage):
    target.current_hp -= damage
    return cls.TARGET_DEAD if target.current_hp <= 0 else cls.TARGET_ALIVE

  @classmethod
  def apply_traits(cls, damage, damage_type, actor, target):
    if damage_type == "Physical":
      attack_factor = 1.00 + (.05 * actor.traits.get("Beefy!", 0))
      defense_factor = 0.95 ** target.traits.get("Stocky!", 0)
    elif damage_type == "Magic":
      attack_factor = 1.00 + (.05 * actor.traits.get("Wizardry", 0))
      defense_factor = 0.95 ** target.traits.get("Mental Toughness", 0)
    else:
      assert False
    damage = max(1, damage * attack_factor * defense_factor)
    return damage

  @classmethod
  def action_skill(cls, info, actor, target, logs):
    logs.append("{} uses {}".format(actor.name, info.get_name()))
    return info.apply_skill(actor, target, logs)

  @classmethod
  def action_attack(cls, _, actor, target, logs, attack_type=None,
                    multiplier=None, base_damage=None):
    """Attacks, applies damage, returns True if target dies."""
    assert (multiplier is None) or (base_damage is None)
    logs.append("{} attacks {}".format(actor.name, target.name))
    damage = base_damage or actor.get_damage()
    damage_type = attack_type or actor.get_damage_type()
    damage = cls.apply_traits(damage, damage_type, actor, target)
    if damage_type == "Physical":
      attack = actor.get_effective_stat("Strength")
      defense = target.get_effective_stat("Defense")
    elif damage_type == "Magic":
      attack = actor.get_effective_stat("Intellect")
      defense = target.get_effective_stat("Magic Defense")
    else:
      assert False
    factor = float(attack) / defense
    factor = factor ** .5
    if multiplier:
      factor *= multiplier
    if damage_type != actor.get_damage_type():
      factor *= .5   # Weapon is the wrong kind
    level_factor = 1.02 ** (actor.level - target.level)
    damage = int(damage * factor * level_factor)
    if damage > 9999: damage = 9999
    if Effect.get_combined_impact("Blinded", actor.buffs, actor.debuffs) > 0:
      if random.random() < .5:
        logs.append("Misses due to Blindness")
        return cls.TARGET_ALIVE
    color_string = "`255,0,0`" if isinstance(actor, Monster) else ""
    logs.append("{}Hits for {} {} damage`0,0,0`".format(color_string, damage,
                                                    damage_type))
    return cls.apply_damage(target, damage)

  @classmethod
  def get_next_actor(cls, character, monster):
    result = cls.skill_check("Speed", character, monster)
    if result == cls.ACTOR_SUCCEEDED:
      return cls.CHARACTER_TURN
    else:
      return cls.MONSTER_TURN

  @classmethod
  def skill_check(cls, stat, actor, target):
    actor_stat = actor.get_effective_stat(stat)
    target_stat = target.get_effective_stat(stat)
    total_stat = actor_stat + target_stat
    actor_chance = float(actor_stat) / total_stat
    if random.random() < actor_chance:
      return cls.ACTOR_SUCCEEDED
    else:
      return cls.ACTOR_FAILED

  @classmethod
  def action_escape(cls, _, actor, target, logs):
    result = cls.skill_check("Speed", actor, target)
    if result == cls.ACTOR_SUCCEEDED:
      return cls.ACTOR_ESCAPED
    else:
      logs.append("Escape unsuccessful")
      return cls.ACTOR_FAILED
