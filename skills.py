from combat import Combat
import random
import effect

SKILLS = {
          "Withering Attack": "Chance to inflict stacks of wither",
          "Bubble": "Create a barrier that absorbs damage",
          "Swiftness": "Gain speed buff",
          "Drain": "Perform an attack, absorb a percentage of the damage as HP",
          "Final Strike": "Convert HP/MP to one massive attack",
          "Heal": "Restore HP",
          "Renew": "Restore HP each turn",
          "Chain Lightning": "Do magical damage, chance to repeat",
          "Full Heal": "Restore all HP",
          "Auto-Life": "Add a buff that restores HP on fatal damage",
          "Meditate": "Restore MP. May fail depending on current MP",
          "Poisoned Blade": "Chance to auto-kill non-bosses",
          "Cannibalize": "Convert own HP into MP",
          "Bulk Up": "Increase max HP for the battle",
          # TODO: A few more interesting magical attacks
          # Force bolt?
          # Libra as a buff?
         }

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
    return 1.0 + 0.1 * self.level
  def go_again_chance(self):
    return 1.0 - (0.8 ** self.level)
  def get_description(self):
    desc = "Physical attack with %.2f multiplier, %d%% chance to go again."
    desc = desc % (self.get_attack_multiple(), (self.go_again_chance() * 100))
    return desc
  def sp_cost(self):
    return self.level * 4
  def apply_skill(self, actor, opponent, logs):
    result = Combat.action_attack(None, actor, opponent, logs, "Physical",
                                  self.get_attack_multiple())
    if result == Combat.TARGET_DEAD:
      return result
    if random.random() < self.go_again_chance():
      logs.append("Quick attack succeeded")
      return Combat.ACTOR_TURN
    else:
      logs.append("Quick attack failed")
      return Combat.TARGET_ALIVE

class Blind(Skill):
  def get_name(self):
    return "Blind"
  def get_attack_multiple(self):
    return 1.0 + 0.1 * self.level
  def blind_chance(self):
    return 1.0 - (0.5 ** self.level)
  def get_description(self):
    desc = "Physical attack with %.2f multiplier, %d%% chance to blind."
    desc = desc % (self.get_attack_multiple(), (self.blind_chance() * 100))
    return desc
  def sp_cost(self):
    return self.level * 4
  def apply_skill(self, actor, opponent, logs):
    result = Combat.action_attack(None, actor, opponent, logs, "Physical",
                                  self.get_attack_multiple())
    if random.random() < self.blind_chance():
      if opponent.boss:
        logs.append("Blind resisted")
      else:
        logs.append("%s is blinded" % opponent.name)
        opponent.add_debuff(effect.Blinded(10))
    return result

class Bash(Skill):
  def get_name(self):
    return "Bash"
  def get_attack_multiple(self):
    return 1.0 + 0.1 * self.level
  def stun_chance(self):
    return 1.0 - (0.8 ** self.level)
  def get_description(self):
    desc = "Physical attack with %.2f multiplier, %d%% chance to stun."
    desc = desc % (self.get_attack_multiple(), (self.stun_chance() * 100))
    return desc
  def sp_cost(self):
    return self.level * 5
  def apply_skill(self, actor, opponent, logs):
    result = Combat.action_attack(None, actor, opponent, logs, "Physical",
                                  self.get_attack_multiple())
    if random.random() < self.stun_chance():
      if opponent.boss:
        logs.append("Stun resisted")
      else:
        logs.append("%s is stunned" % opponent.name)
        opponent.add_debuff(effect.Stunned(3))
    return result

class Protection(Skill):
  def get_name(self):
    return "Protection"
  def buff_duration(self):
    return 5 + (5 * self.level)
  def get_description(self):
    return "Increase def/mdef by 100%% for %d time units" % self.buff_duration()
  def sp_cost(self):
    return self.level * 2
  def apply_skill(self, actor, opponent, logs):
    actor.add_buff(effect.Protection(self.buff_duration()))
    return Combat.TARGET_ALIVE

class HeavySwing(Skill):
  def get_name(self):
    return "Heavy Swing"
  def get_attack_multiple(self):
    return 2.0 + 0.3 * self.level
  def miss_chance(self):
    return 0.2 - (0.01 * self.level)
  def get_description(self):
    desc = "Physical attack with %.2f multiplier, %d%% chance to miss."
    desc = desc % (self.get_attack_multiple(), (self.miss_chance() * 100))
    return desc
  def sp_cost(self):
    return self.level * 4
  def apply_skill(self, actor, opponent, logs):
    if random.random() < self.miss_chance():
      logs.append("Heavy Swing missed")
      return Combat.TARGET_ALIVE
    else:
      result = Combat.action_attack(None, actor, opponent, logs, "Physical",
                                    self.get_attack_multiple())
      return result

class LastStand(Skill):
  def get_name(self):
    return "Last Stand"
  def duration(self):
    return 2 + self.level
  def get_description(self):
    return "Cannot die for %d time units." % self.duration()
  def sp_cost(self):
    return 50 + 10 * self.level
  def once_per_battle(self):
    return True
  def apply_skill(self, actor, opponent, logs):
    logs.append("%s takes a Last Stand" % actor.name)
    actor.add_buff(effect.LastStand(self.duration()))
          
class Surge(Skill):
  def get_name(self):
    return "Surge"
  def buff_duration(self):
    return 5 + (5 * self.level)
  def get_description(self):
    return "Strength up by 100%% for %d time" % self.buff_duration()
  def sp_cost(self):
    return self.level * 3
  def apply_skill(self, actor, opponent, logs):
    actor.add_buff(effect.Surge(self.buff_duration()))
    return Combat.TARGET_ALIVE
    
class Concentrate(Skill):
  def get_name(self):
    return "Concentrate"
  def buff_duration(self):
    return 5 + (5 * self.level)
  def get_description(self):
    return "Intelligence up by 100%% for %d time" % self.buff_duration()
  def sp_cost(self):
    return self.level * 3
  def apply_skill(self, actor, opponent, logs):
    actor.add_buff(effect.Concentrate(self.buff_duration()))
    return Combat.TARGET_ALIVE

SKILLS = [QuickAttack, Blind, Bash, Protection, HeavySwing, LastStand, Surge]
