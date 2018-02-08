import unittest
import srs_random

class TestRandom(unittest.TestCase):
  def test_init(self):
    seed = srs_random.init()
    assert seed > 0

  def test_random(self):
    srs_random.seed(1248)
    expected = [
      0.18123209611107516,
      0.4835357922971334,
      0.5823983723903442,
      0.9727856702015698,
      0.6614749676932676,
      0.632901508040328,
      0.6047620139037617,
      0.9386117697169615,
      0.5321717912477563,
      0.24780457066956219,
      0.24919355624928652,
      0.34943757408355614,
      0.8258911077824963,
      0.09761401796435931,
      0.4650767231172983,
      0.6867830279441302
    ]
    actual = [srs_random.random() for i in range(len(expected))]
    self.assertEqual(expected, actual)

  def test_gauss(self):
    srs_random.seed(12345)
    actual = [
      srs_random.gauss(.5, 1),
      srs_random.gauss(0, 1),
      srs_random.gauss(0, 3),
      srs_random.gauss(1, .05),
      srs_random.gauss(1, .2),
      srs_random.gauss(1, 1)
    ]
    expected = [
      0.9361013880612667,
      1.1052175415166217,
      -3.5149387007807764,
      0.9963576216668021,
      0.9831245768135517,
      2.273494456580683
    ]
    self.assertEqual(expected, actual)

  def test_randint(self):
    srs_random.seed(653)
    actual = [
      srs_random.randint(0, 1),
      srs_random.randint(0, 1),
      srs_random.randint(0, 1),
      srs_random.randint(0, 1),
      srs_random.randint(0, 3),
      srs_random.randint(0, 4),
      srs_random.randint(1, 10),
      srs_random.randint(1, 3),
      srs_random.randint(1, 4),
      srs_random.randint(1, 5),
      srs_random.randint(2, 4),
      srs_random.randint(3, 10),
      srs_random.randint(5, 10),
      srs_random.randint(5, 8),
      srs_random.randint(8, 12),
      srs_random.randint(10, 20)
    ]
    expected = [0, 1, 1, 0, 3, 4, 10, 3, 1, 3, 4, 4, 9, 6, 11, 20]
    self.assertEqual(expected, actual)

  def test_choice(self):
    srs_random.seed(98765)
    seq = ['quick', 'brown', 'fox', 'lazy', 'dogs']
    expected = ['dogs', 'brown', 'brown', 'quick', 'fox']
    actual = [srs_random.choice(seq) for i in range(len(expected))]
    self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
