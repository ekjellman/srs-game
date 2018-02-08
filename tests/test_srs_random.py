import unittest
import srs_random

class TestRandom(unittest.TestCase):
  def test_init(self):
    seed = srs_random.init()
    assert seed > 0

  def test_random(self):
    srs_random.seed(12345)
    expected = [
      0.41661987254534116,
      0.010169169457068361,
      0.8252065092537432,
      0.2986398551995928,
      0.3684116894884757
    ]
    actual = [srs_random.random() for i in xrange(len(expected))]
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
      0.37619920441114607,
      0.07152496347566478,
      1.1501075829514789,
      0.9625001469556529,
      0.9111291054702578,
      1.4827546241363072
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
    expected = [0, 0, 1, 0, 1, 0, 6, 1, 1, 3, 3, 4, 8, 6, 12, 11]
    self.assertEqual(expected, actual)

  def test_choice(self):
    srs_random.seed(12345)
    seq = ['quick', 'brown', 'fox', 'lazy', 'dogs']
    expected = ['fox', 'quick', 'dogs', 'brown', 'brown']
    actual = [srs_random.choice(seq) for i in xrange(len(expected))]
    self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
