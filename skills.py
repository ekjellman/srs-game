import srs_random
from combat import Combat
import effect

# TODO: A few more interesting magical attacks
# Force bolt?

def get_skill(skill_name, level):
  # Raises if skill_name does not exist
  i = SKILL_NAMES.index(skill_name)
  skill = SKILLS[i](level=level)
  return skill

class Skill(object):
  def __init__(self, level=1):
    self.level = level
  def get_name(self):
    return "Not Implemented"
  def get_description(self):
    return "No Description"
  def level_up(self):
    self.level += 1
  def sp_cost(self):
    return 0
  def once_per_battle(self):
    return False
  def apply_skill(self, actor, opponent, logs):
    pass

class QuickAttack(Skill):
  def get_name(self):
    return "Quick Attack"
  def get_attack_multiple(self):
    return 1.0 + 0.2 * self.level
  def go_again_chance(self):
    return 1.0 - (0.8 ** self.level)
  def get_description(self):
    desc = "Physical attack with {:.2f} multiplier, {:.1f}% chance to go again."
    desc = desc.format(self.get_attack_multiple(), (self.go_again_chance() * 100))
    return desc
  def sp_cost(self):
    return int(self.level * 4 * (1.1 ** self.level))
  def apply_skill(self, actor, opponent, logs):
    result = Combat.action_attack(None, actor, opponent, logs, "Physical",
                                  self.get_attack_multiple())
    if result == Combat.TARGET_DEAD:
      return result
    if srs_random.random() < self.go_again_chance():
      logs.append("Quick attack succeeded!")
      return Combat.ACTOR_TURN
    else:
      logs.append("Quick attack failed.")
      return Combat.TARGET_ALIVE

class Blind(Skill):
  def get_name(self):
    return "Blind"
  def get_attack_multiple(self):
    return 1.0 + 0.2 * self.level
  def blind_chance(self):
    return 1.0 - (0.5 ** self.level)
  def get_description(self):
    desc = "Physical attack with {:.2f} multiplier, {:.1f}% chance to blind."
    desc = desc.format(self.get_attack_multiple(), (self.blind_chance() * 100))
    return desc
  def sp_cost(self):
    return int(self.level * 4 * (1.1 ** self.level))
  def apply_skill(self, actor, opponent, logs):
    result = Combat.action_attack(None, actor, opponent, logs, "Physical",
                                  self.get_attack_multiple())
    if srs_random.random() < self.blind_chance():
      if opponent.boss:
        logs.append("Blind resisted.")
      else:
        logs.append("{} has been blinded.".format(opponent.name))
        opponent.add_debuff(effect.Blinded(10))
    return result

class Bash(Skill):
  def get_name(self):
    return "Bash"
  def get_attack_multiple(self):
    return 1.0 + 0.2 * self.level
  def stun_chance(self):
    return 1.0 - (0.8 ** self.level)
  def get_description(self):
    desc = "Physical attack with {:.2f} multiplier, {:.1f}% chance to stun."
    desc = desc.format(self.get_attack_multiple(), (self.stun_chance() * 100))
    return desc
  def sp_cost(self):
    return int(self.level * 5 * (1.1 ** self.level))
  def apply_skill(self, actor, opponent, logs):
    result = Combat.action_attack(None, actor, opponent, logs, "Physical",
                                  self.get_attack_multiple())
    if srs_random.random() < self.stun_chance():
      if opponent.boss:
        logs.append("Your stun was resisted.")
      else:
        logs.append("{} is stunned!".format(opponent.name))
        opponent.add_debuff(effect.Stunned(3))
    return result

class Protection(Skill):
  def get_name(self):
    return "Protection"
  def buff_duration(self):
    return 5 + (5 * self.level)
  def get_description(self):
    return "Increase def/mdef by 100% for {} time units.".format(self.buff_duration())
  def sp_cost(self):
    return int(self.level * 6 * (1.1 ** self.level))
  def apply_skill(self, actor, opponent, logs):
    actor.add_buff(effect.Protection(self.buff_duration()))
    return Combat.TARGET_ALIVE

class HeavySwing(Skill):
  def get_name(self):
    return "Heavy Swing"
  def get_attack_multiple(self):
    return 2.0 + 0.25 * self.level
  def miss_chance(self):
    return 0.3 * (.9 ** (self.level - 1))
  def get_description(self):
    desc = "Physical attack with {:.2f} multiplier, {:.1f}% chance for normal damage."
    desc = desc.format(self.get_attack_multiple(), (self.miss_chance() * 100))
    return desc
  def sp_cost(self):
    return int(self.level * 5 * (1.1 ** self.level))
  def apply_skill(self, actor, opponent, logs):
    if srs_random.random() < self.miss_chance():
      logs.append("Heavy Swing lands a glancing blow...")
      result = Combat.action_attack(None, actor, opponent, logs, "Physical")
      return result
    else:
      result = Combat.action_attack(None, actor, opponent, logs, "Physical",
                                    self.get_attack_multiple())
      return result

class LastStand(Skill):
  def get_name(self):
    return "Last Stand"
  def duration(self):
    return 3 + self.level
  def get_description(self):
    return "Cannot die for {} time units.".format(self.duration())
  def sp_cost(self):
    return 30 + int(self.level * 10 * (1.1 ** self.level))
  def once_per_battle(self):
    return True
  def apply_skill(self, actor, opponent, logs):
    logs.append("{} takes a Last Stand.".format(actor.name))
    actor.add_buff(effect.LastStand(self.duration()))

class Surge(Skill):
  def get_name(self):
    return "Surge"
  def buff_duration(self):
    return 5 + (2 * self.level)
  def buff_power(self):
    return 1.2 + 0.1 * self.level
  def get_description(self):
    return "Strength up by {:.1f}% for {} time units.".format((self.buff_power() - 1) * 100,
                                               self.buff_duration())
  def sp_cost(self):
    return int(self.level * 5 * (1.1 ** self.level))
  def apply_skill(self, actor, opponent, logs):
    actor.add_buff(effect.Surge(self.buff_duration(), self.buff_power()))
    return Combat.TARGET_ALIVE

class Concentrate(Skill):
  def get_name(self):
    return "Concentrate"
  def buff_duration(self):
    return 5 + (2 * self.level)
  def buff_power(self):
    return 1.2 + 0.1 * self.level
  def get_description(self):
    return "Intellect up by {:.1f}% for {} time units.".format((self.buff_power() - 1) * 100,
                                                self.buff_duration())
  def sp_cost(self):
    return int(self.level * 5 * (1.1 ** self.level))
  def apply_skill(self, actor, opponent, logs):
    actor.add_buff(effect.Concentrate(self.buff_duration(), self.buff_power()))
    return Combat.TARGET_ALIVE

class Swiftness(Skill):
  def get_name(self):
    return "Swiftness"
  def buff_duration(self):
    return 5 + (2 * self.level)
  def buff_power(self):
    return 1.2 + 0.1 * self.level
  def get_description(self):
    return "Speed up by {:.1f}% for {} time units.".format((self.buff_power() - 1) * 100,
                                            self.buff_duration())
  def sp_cost(self):
    return int(self.level * 7 * (1.1 ** self.level))
  def apply_skill(self, actor, opponent, logs):
    actor.add_buff(effect.Swiftness(self.buff_duration(), self.buff_power()))
    return Combat.TARGET_ALIVE

class BulkUp(Skill):
  def get_name(self):
    return "Bulk Up"
  def buff_duration(self):
    return 5 + (2 * self.level)
  def buff_power(self):
    return 1.2 + 0.1 * self.level
  def get_description(self):
    return "Stamina up by {:.1f}% for {} time units.".format((self.buff_power() - 1) * 100,
                                            self.buff_duration())
  def sp_cost(self):
    return int(self.level * 7 * (1.1 ** self.level))
  def apply_skill(self, actor, opponent, logs):
    actor.add_buff(effect.BulkUp(self.buff_duration(), self.buff_power()))
    return Combat.TARGET_ALIVE

class Cannibalize(Skill):
  def get_name(self):
    return "Cannibalize"
  def percent_converted(self):
    return 3 + self.level
  def get_description(self):
    desc = "Convert up to {:.1f}% of max HP into half as many SP."
    return desc.format(self.percent_converted())
  def sp_cost(self):
    return 0
  def apply_skill(self, actor, opponent, logs):
    hp_to_convert = actor.max_hp * self.percent_converted() // 100
    hp_to_convert = min(hp_to_convert, actor.current_hp - 1)
    sp_gained = hp_to_convert // 2
    actor.current_hp -= hp_to_convert
    sp_gained = actor.restore_sp(sp_gained)
    logs.append("Converted {} HP into {} SP".format(hp_to_convert, sp_gained))
    return Combat.TARGET_ALIVE

class PoisonedBlade(Skill):
  def get_name(self):
    return "Poisoned Blade"
  def get_attack_multiple(self):
    return 1.0 + 0.2 * self.level
  def kill_chance(self):
    return 0.05 + (0.02 * self.level)
  def get_description(self):
    desc = "Physical attack with {:.2f} multiplier, {:.1f}% chance to auto-kill."
    desc = desc.format(self.get_attack_multiple(), (self.kill_chance() * 100))
    return desc
  def sp_cost(self):
    return int(self.level * 4 * (1.1 ** self.level))
  def apply_skill(self, actor, opponent, logs):
    if srs_random.random() < self.kill_chance() and not opponent.boss:
      logs.append("Assassinated!")
      return Combat.TARGET_DEAD
    else:
      result = Combat.action_attack(None, actor, opponent, logs, "Physical",
                                    self.get_attack_multiple())
      return result

class Meditate(Skill):
  def get_name(self):
    return "Meditate"
  def percent_gained(self):
    return 8 + self.level
  def get_description(self):
    desc = "Gain {:.1f}% of max SP. Has a chance to fail based on current SP."
    return desc.format(self.percent_gained())
  def sp_cost(self):
    return 0
  def chance_to_fail(self, actor):
    return (actor.current_sp / float(actor.max_sp) * (.99 ** self.level))
  def apply_skill(self, actor, opponent, logs):
    if srs_random.random() > self.chance_to_fail(actor):
      sp_gained = actor.restore_sp(actor.max_sp * self.percent_gained() // 100)
      logs.append("Your meditating restored {} of your SP.".format(sp_gained))
    else:
      logs.append("Your meditation failed to restore any SP.")
    return Combat.TARGET_ALIVE

class Heal(Skill):
  def get_name(self):
    return "Heal"
  def base_hp_gain(self):
    return 200 * self.level
  def get_description(self):
    return "Gain {} HP (base).".format(self.base_hp_gain())
  def sp_cost(self):
    return int(self.level * 5 * (1.1 ** self.level))
  def apply_skill(self, actor, opponent, logs):
    effective_int = actor.get_effective_stat("Intellect")
    hp_gained = int(self.base_hp_gain() * ((effective_int / 100.0) ** .5))
    actor.restore_hp(hp_gained)
    logs.append("Your Heal restored {} HP.".format(hp_gained))
    return Combat.TARGET_ALIVE

class Drain(Skill):
  def get_name(self):
    return "Drain"
  def get_attack_multiple(self):
    return 1.0 + 0.1 * self.level
  def get_description(self):
    desc = "Magical attack with {:.2f} multiplier. Gains some HP."
    desc = desc.format(self.get_attack_multiple())
    return desc
  def sp_cost(self):
    return int(self.level * 5 * (1.1 ** self.level))
  def apply_skill(self, actor, opponent, logs):
    drain_base = (actor.get_effective_stat("Intellect") * self.level) ** .7
    hp_gained = int(drain_base)
    result = Combat.action_attack(None, actor, opponent, logs, "Magic",
                                  self.get_attack_multiple())
    actor.restore_hp(hp_gained)
    logs.append("Drain restored {} of your HP.".format(hp_gained))
    return result

class Wither(Skill):
  def get_name(self):
    return "Wither"
  def get_attack_multiple(self):
    return 0.9 + 0.1 * self.level
  def get_wither_stacks(self):
    return self.level
  def get_wither_length(self):
    return 9 + self.level
  def get_description(self):
    desc = "Magical attack with {:.2f} multiplier. Adds {} stacks of Wither."
    desc = desc.format(self.get_attack_multiple(), self.get_wither_stacks())
    return desc
  def sp_cost(self):
    return int(self.level * 6 * (1.1 ** self.level))
  def apply_skill(self, actor, opponent, logs):
    result = Combat.action_attack(None, actor, opponent, logs, "Magic",
                                  self.get_attack_multiple())
    opponent.add_debuff(effect.Wither(self.get_wither_length(),
                                      self.get_wither_stacks()))
    return result

class ChainLightning(Skill):
  def get_name(self):
    return "Chain Lightning"
  def get_attack_multiple(self):
    return 1.0 + 0.15 * self.level
  def get_repeat_chance(self):
    return 1.0 - (0.75 ** self.level)
  def get_description(self):
    desc = "Magical attack with {:.2f} multiplier. {:.1f}% initial repeat chance."
    desc = desc.format(self.get_attack_multiple(), self.get_repeat_chance() * 100)
    return desc
  def sp_cost(self):
    return int(self.level * 6 * (1.1 ** self.level))
  def apply_skill(self, actor, opponent, logs):
    repeat_chance = self.get_repeat_chance()
    result = Combat.action_attack(None, actor, opponent, logs, "Magic",
                                  self.get_attack_multiple())
    while result == Combat.TARGET_ALIVE and srs_random.random() < repeat_chance:
      repeat_chance *= .9
      result = Combat.action_attack(None, actor, opponent, logs, "Magic",
                                    self.get_attack_multiple())
    return result

class FinalStrike(Skill):
  def get_name(self):
    return "Final Strike"
  def get_description(self):
    return "Ultimate magical attack. Uses all HP and SP. Removes all buffs."
  def sp_cost(self):
    return int(self.level * 6 * (1.1 ** self.level))
  def once_per_battle(self):
    return True
  def apply_skill(self, actor, opponent, logs):
    base_damage = actor.current_hp - 1
    base_damage += (actor.current_sp * 3)
    base_damage *= 1.0 + (0.1 * self.level)
    result = Combat.action_attack(None, actor, opponent, logs, "Magic",
                                  base_damage=base_damage)
    actor.current_sp = 0
    actor.current_hp = 1
    actor.buffs = []
    return result

class Renew(Skill):
  def get_name(self):
    return "Renew"
  def base_hp_gain(self):
    return int(50 * (self.level ** .5))
  def buff_duration(self):
    return 6 + (2 * self.level)
  def get_description(self):
    return "Gain {} HP/turn (base) for {} time units.".format(self.base_hp_gain(),
                                                     self.buff_duration())
  def sp_cost(self):
    return int(self.level * 6 * (1.1 ** self.level))
  def apply_skill(self, actor, opponent, logs):
    effective_int = actor.get_effective_stat("Intellect")
    buff_strength = int(self.base_hp_gain() * ((effective_int / 100.0) ** .5))
    actor.add_buff(effect.Renew(self.buff_duration(), buff_strength))
    return Combat.TARGET_ALIVE

class AutoLife(Skill):
  def get_name(self):
    return "Auto Life"
  def hp_gain(self):
    return 250 * self.level
  def buff_duration(self):
    return 20
  def get_description(self):
    return "Buff that restores {} HP on death once.".format(self.hp_gain())
  def sp_cost(self):
    return int(self.level * 10 * (1.1 ** self.level))
  def apply_skill(self, actor, opponent, logs):
    actor.add_buff(effect.AutoLife(self.buff_duration(), self.hp_gain()))
    return Combat.TARGET_ALIVE

class HolyBlade(Skill):
  def get_name(self):
    return "Holy Blade"
  def get_attack_multiple(self):
    return 0.9 + 0.1 * self.level
  def get_aura_stacks(self):
    return self.level
  def get_aura_length(self):
    return 8 + self.level
  def get_heal_percent(self):
    return 5 + self.level
  def get_description(self):
    desc = "Physical attack with {:.2f} multiplier. Gives {} stacks of Aura. {:.1f}% heal."
    desc = desc.format(self.get_attack_multiple(), self.get_aura_stacks(),
                   self.get_heal_percent())
    return desc
  def sp_cost(self):
    return int(self.level * 6 * (1.1 ** self.level))
  def apply_skill(self, actor, opponent, logs):
    result = Combat.action_attack(None, actor, opponent, logs, "Physical",
                                  self.get_attack_multiple())
    actor.add_buff(effect.Aura(self.get_aura_length(),
                               self.get_aura_stacks()))
    heal = actor.max_hp * self.get_heal_percent() // 100
    heal = actor.restore_hp(heal)
    logs.append("You restore {} HP.".format(heal))
    return result

SKILLS = [QuickAttack, Blind, Bash, Protection, HeavySwing, LastStand, Surge,
          Concentrate, Swiftness, BulkUp, Cannibalize, PoisonedBlade,
          Meditate, Heal, Drain, Wither, ChainLightning, FinalStrike, Renew,
          AutoLife, HolyBlade]
SKILL_NAMES = [skill().get_name() for skill in SKILLS]
