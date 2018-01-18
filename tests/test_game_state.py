from nose.tools import assert_equals
import game_state

# This test should fail if any of the debug statements are active
# TODO: Currently, only DEBUG_TOWER_START changes are caught by this test
def test_game_state_constructor():
    s = game_state.GameState()
    assert_equals(s.state, ["CHAR_CREATE"])
    # TODO: Test Character constructor
    assert s.character # checking for non-None
    assert_equals(s.floor, 1)
    assert_equals(s.frontier, 1)
    assert_equals(s.time_spent, 0)
    assert_equals(s.energy, 200)
    # TODO: Test generate_towns
    assert s.towns
    # Only first level should be unlocked
    assert not s.tower_lock[1]
    for level in range(game_state.TOWER_LEVELS + 1):
        if level > 1:
            assert s.tower_lock[level]
        assert_equals(s.tower_faction[level], 1.0)
    assert not s.tower_update_ready
    assert s.tower_quests # generate_quests is tested separately
    assert_equals(s.ascension_encounters, 0)
    assert_equals(s.ascension_encounters_required, 0)
    assert_equals(s.current_shop, None)
    assert_equals(s.monster, None)
    assert_equals(s.quest, None)
    assert_equals(s.treasure_queue, [])
    assert_equals(s.equipment_choice, None)
    assert_equals(s.rune_level, -1)
    assert_equals(s.levelups, 0)
    assert_equals(s.skillups, 0)
    assert_equals(s.skills_used, set())
    assert_equals(s.skill_choices, [])
    assert_equals(s.trait_choices, [])
    assert not s.infinity_dungeon
    assert_equals(s.stronghold_room, 0)
    assert_equals(s.last_turn_logs, [])

def test_generate_quests():
    quests = game_state.GameState.generate_quests()
    assert_equals(quests[0], None)
    for i in range(1, game_state.TOWER_LEVELS + 1):
        # Test specifics of quest separately
        assert quests[i] is not None 