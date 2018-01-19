import unittest
#from nose.tools import assert_equals
import game_state
import rooms

# Run tests from the game directory with the following command:
#   python -m unittest discover tests "test*.py" -v

class TestGameState(unittest.TestCase):
    # This test should fail if any of the debug statements are active or changed
    def test_debug_off(self):
        self.assertEqual(game_state.DEBUG_FLOOR, None)
        self.assertEqual(game_state.DEBUG_BUILDING, None)
        self.assertEqual(game_state.DEBUG_GOLD, None)
        self.assertEqual(game_state.DEBUG_MATERIALS, None)
        self.assertEqual(game_state.DEBUG_CHARACTER, None)
        self.assertEqual(game_state.DEBUG_TOWER_START, None)

    def test_game_state_constructor(self):
        s = game_state.GameState()
        self.assertEqual(s.state, ["CHAR_CREATE"])
        # TODO: Test Character constructor
        assert s.character # checking for non-None
        # Frontier, floor, and tower_lock will fail if DEBUG_TOWER_START is set
        self.assertEqual(s.floor, 1)
        self.assertEqual(s.frontier, 1)
        self.assertEqual(s.time_spent, 0)
        self.assertEqual(s.energy, 200)
        # TODO: Test generate_towns
        assert s.towns
        # Only first level should be unlocked
        assert not s.tower_lock[1]
        for level in range(game_state.TOWER_LEVELS + 1):
            if level > 1:
                assert s.tower_lock[level]
            self.assertEqual(s.tower_faction[level], 1.0)
        assert not s.tower_update_ready
        assert s.tower_quests # generate_quests is tested separately
        self.assertEqual(s.ascension_encounters, 0)
        self.assertEqual(s.ascension_encounters_required, 0)
        self.assertEqual(s.current_shop, None)
        self.assertEqual(s.monster, None)
        self.assertEqual(s.quest, None)
        self.assertEqual(s.treasure_queue, [])
        self.assertEqual(s.equipment_choice, None)
        self.assertEqual(s.rune_level, -1)
        self.assertEqual(s.levelups, 0)
        self.assertEqual(s.skillups, 0)
        self.assertEqual(s.skills_used, set())
        self.assertEqual(s.skill_choices, [])
        self.assertEqual(s.trait_choices, [])
        assert not s.infinity_dungeon
        self.assertEqual(s.stronghold_room, 0)
        self.assertEqual(s.last_turn_logs, [])

    def test_generate_quests(self):
        quests = game_state.GameState.generate_quests()
        self.assertEqual(quests[0], None)
        for i in range(1, game_state.TOWER_LEVELS + 1):
            # Test specifics of quest separately
            assert quests[i] is not None 

    # TODO: Combine these two functions?
    # TODO: Replace type checks with mocks of Room classes
    def generate_towns_first_floor(self, shop_number, shop):
        self.assertEqual(shop.level, 1)
        types = {0: rooms.Inn, 1: rooms.Temple, 2: rooms.Alchemist}
        # Each Room() object is unique, so they can't be compared directly.
        # It's possible to implement __eq__ or __cmp__ for some Rooms with constant
        #     choices (Inn, Temple), but others (Alchemist) have random options.
        self.assertEqual(type(shop), types[shop_number])

    def generate_towns_summit(self, shop_number, shop):
        self.assertEqual(shop.level, game_state.TOWER_LEVELS)
        types = {0: rooms.Inn, 1: rooms.Temple, 2: rooms.Crafthall}
        self.assertEqual(type(shop), types[shop_number])

    def test_generate_towns(self):
        towns = game_state.GameState.generate_towns()
        levels = game_state.TOWER_LEVELS
        self.assertEqual(towns[0], None)
        # Base floor (1) shops are always the same
        for index, shop in enumerate(towns[1]):
            self.generate_towns_first_floor(index, shop)
            self.assertEqual(len(towns[1]), 3)
        # No extra shops
        self.assertEqual(len(towns[1]), 3)
        # Every town in the tower should have 3 different shops
        for level in range(2, levels):
            self.assertEqual(len(towns[level]), 3)
            self.assertEqual(len(set(towns[level])), 3)
        # Does not test debug code
        # Summit shops are always the same
        for index, shop in enumerate(towns[levels]):
            self.generate_towns_summit(index, shop)
        self.assertEqual(len(towns[levels]), 3)

if __name__ == '__main__':
    unittest.main()