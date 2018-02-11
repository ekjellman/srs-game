import unittest
from srs_random import Dice

class TestRandom(unittest.TestCase):
  def test_init(self):
    rng = Dice()
    assert rng.seed > 0

  def test_random(self):
    rng = Dice(8421)
    expected = [
      0.609379768371582,
      0.7931511402130127,
      0.05381131172180176,
      0.6512428522109985,
      0.9651315212249756,
      0.3705257177352905,
      0.6148815155029297,
      0.0711895227432251,
      0.8699692487716675,
      0.6136062145233154,
      0.5560871362686157
    ]
    actual = [rng.random() for i in range(len(expected))]
    self.assertEqual(expected, actual)

  def test_gauss(self):
    rng = Dice(12345)
    actual = [
      rng.gauss(.5, 1),
      rng.gauss(0, 1),
      rng.gauss(0, 3),
      rng.gauss(1, .05),
      rng.gauss(1, .2),
      rng.gauss(1, 1)
    ]
    expected = [
      0.77939701361899,
      -0.18666895427036528,
      -3.8315715975338014,
      1.0167345321217482,
      1.1363730167341564,
      -0.4553519284739609
    ]
    self.assertEqual(expected, actual)

  def test_randint(self):
    rng = Dice(653)
    actual = [
      rng.randint(0, 1),
      rng.randint(0, 1),
      rng.randint(0, 1),
      rng.randint(0, 1),
      rng.randint(0, 3),
      rng.randint(0, 4),
      rng.randint(1, 10),
      rng.randint(1, 3),
      rng.randint(1, 4),
      rng.randint(1, 5),
      rng.randint(2, 4),
      rng.randint(3, 10),
      rng.randint(5, 10),
      rng.randint(5, 8),
      rng.randint(8, 12),
      rng.randint(10, 20)
    ]
    expected = [0, 1, 0, 0, 3, 3, 2, 2, 1, 3, 4, 7, 6, 5, 10, 19]
    self.assertEqual(expected, actual)

  def test_choice(self):
    rng = Dice(737171737)
    seq = ['quick', 'brown', 'fox', 'lazy', 'dogs']
    expected = ['quick', 'dogs', 'fox', 'lazy', 'dogs']
    actual = [rng.choice(seq) for i in range(len(expected))]
    self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
