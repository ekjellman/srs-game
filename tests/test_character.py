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

    # TODO: Test colored_hp()
    # TODO: Test add_item with no items
    #       Test add_item with 3 items
    # TODO: Test use_item with no item
    #       Test use_item with bento in combat
    #       Test use_item with normal item
    # TODO: Test add_buff with no buffs on
    #       Test add_buff with same buff already on
    # TODO: Test add_debuff

    # TODO: Test that buffs fall off when they should
    #       Test that debuffs fall off when they should
    #       Test Effect.get_combined_impact separately
    #       Test buffs individually (pass_time, active, turn_by_turn)
    #       Test recalculate_maxes()
    #       Test restored_hp with Regeneration
    #       Test restored_sp with Clarity of Mind
    #       Test that buff.pass_time, restore_hp, restore_sp don't break with non-positive time_passed
    def test_pass_time_no_buffs_no_traits_full_hp(self):
        # No Regeneration or Clarity of Mind
        c = character.Character()
        prev_hp = c.current_hp
        prev_sp = c.current_sp
        c.pass_time(1)
        self.assertEqual(c.current_hp, prev_hp)
        self.assertEqual(c.current_sp, prev_sp)

    def test_pass_time_no_buffs_regeneration_partial_hp(self):
        c = character.Character()
        c.traits["Regeneration"] = 1
        c.current_hp = int(c.max_hp * 0.75)
        assert c.current_hp < c.max_hp
        prev_hp = c.current_hp
        c.pass_time(1)
        assert c.current_hp > prev_hp

    def test_pass_time_no_buffs_regeneration_full_hp(self):
        c = character.Character()
        c.traits["Regeneration"] = 1
        assert c.current_hp == c.max_hp
        prev_hp = c.current_hp
        c.pass_time(1)
        self.assertEqual(c.current_hp, prev_hp)

    def test_pass_time_no_buffs_clarity_partial_sp(self):
        c = character.Character()
        c.traits["Clarity of Mind"] = 1
        c.current_sp = int(c.max_sp * 0.75)
        assert c.current_sp < c.max_sp
        prev_sp = c.current_sp
        c.pass_time(1)
        assert c.current_sp > prev_sp

    def test_pass_time_no_buffs_clarity_full_sp(self):
        c = character.Character()
        c.traits["Clarity of Mind"] = 1
        assert c.current_sp == c.max_sp
        prev_sp = c.current_sp
        c.pass_time(1)
        self.assertEqual(c.current_sp, prev_sp)

    def test_gain_gold_zero_not_merchant_warrior(self):
        c = character.Character() 
        c.gold = 0
        gained = c.gain_gold(0)
        self.assertEqual(c.gold, 0)
        self.assertEqual(gained, 0)

    def test_gain_gold_nonzero_not_merchant_warrior(self):
        c = character.Character() 
        c.gold = 0
        gained = c.gain_gold(100)
        self.assertEqual(c.gold, 100)
        self.assertEqual(gained, 100)

# TODO: Test make_initial_equipment
# TODO: Test restore_hp with full HP, partial HP, some restored, none restored