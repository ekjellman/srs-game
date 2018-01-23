import unittest
import mock
import character
import equipment

class TestCharacter(unittest.TestCase):
    def test_character_constructor(self):
        c = character.Character()
        assert not any(c.equipment) # Should be 5 empty slots
        assert not c.items
        assert not c.skills
        for stat in ("Strength", "Stamina", "Defense", "Speed", "Intellect", "Magic Defense"):
            assert c.stats[stat] # All stats should exist and be non-zero
        assert c.gold > 0
        # TODO: Currently name is assigned, but may be removed soon
        assert c.name
        assert c.base_hp > 0
        assert c.max_hp > 0
        assert c.base_sp > 0
        assert c.max_sp > 0
        self.assertEqual(c.current_hp, c.max_hp)
        self.assertEqual(c.current_sp, c.max_sp)
        self.assertEqual(c.level, 1)
        assert not c.exp
        self.assertEqual(len(c.materials), len(character.RARITY))
        assert not any(c.materials)
        assert not c.buffs
        assert not c.debuffs
        assert c.runes # Currently set to 1
        assert not c.traits