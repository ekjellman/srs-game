import unittest
import srs_random

class TestRandom(unittest.TestCase):
  def test_init(self):
    seed = srs_random.init()
    assert seed > 0

  def test_random(self):
    srs_random.seed(12345)
    expected = [
      0.19018498755791735,
      0.9451315374195004,
      0.4111855034540688,
      0.1077103963926298,
      0.39181641816648183
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
      1.3843872364356706,
      2.241314862141383,
      -1.2149778823272777,
      1.0126402170140905,
      0.8821746293982146,
      1.4761484036066532
    ]
    self.assertEqual(expected, actual)

  def test_randint(self):
    srs_random.seed(12345)
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
    expected = [0, 1, 0, 0, 1, 1, 8, 2, 4, 3, 2, 6, 9, 6, 9, 20]
    self.assertEqual(expected, actual)

  def test_choice(self):
    srs_random.seed(12345)
    seq = ['quick', 'brown', 'fox', 'lazy', 'dogs']
    expected = ['quick', 'dogs', 'fox', 'quick', 'brown']
    actual = [srs_random.choice(seq) for i in range(len(expected))]
    self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
