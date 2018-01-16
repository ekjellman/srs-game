import srs_random
from monster import Monster
from equipment import Equipment

TREASURE_CHANCES = [1.0, 1.0, 0.500, 0.080, 0.015]

class Quest(object):
  def __init__(self, game, level):
    self.game = game
    self.monsters = []
    self.treasures = 0
    for _ in range(srs_random.randint(3, 10)):
      self.monsters.append(Monster(game, level, False))
      self.treasures += 1
    for _ in range(srs_random.randint(0, 1)):
      self.monsters.append(Monster(game, level, True))
      self.treasures += 5
    self.gp_reward = 0
    self.xp_reward = 0
    self.treasure_reward = 0
    self.level = level
    self.generate_rewards()

  def complete(self):
    return len(self.monsters) == 0

  def generate_rewards(self):
    self.treasure_reward = 1
    self.gp_reward = 5 * self.level
    self.xp_reward = 5 * self.level
    for _ in range(self.treasures):
      self.xp_reward += srs_random.randint(2 * self.level, 5 * self.level)
      if srs_random.random() < .2:
        self.treasure_reward += 1
      else:
        self.gp_reward += srs_random.randint(2 * self.level, 5 * self.level)

  def get_monster(self):
    return self.monsters[0]

  def defeat_monster(self):
    self.monsters.pop(0)

  def __str__(self):
    pieces = []
    pieces.append("Quest status:")
    pieces.append("Remaining monsters:")
    for monster in self.monsters:
      pieces.append(monster.name)
    pieces.append("Reward: {} GP, {} XP, {} treasures".format(self.gp_reward,
                                                          self.xp_reward,
                                                          self.treasure_reward))
    return "\n".join(pieces)

  def get_treasure(self):
    treasure = []
    while len(treasure) < self.treasure_reward:
      for rarity in range(4, -1, -1):
        if srs_random.random() < TREASURE_CHANCES[rarity]:
          treasure.append(Equipment.get_new_armor(self.game, self.level, None, None, rarity))
          break
    return treasure
