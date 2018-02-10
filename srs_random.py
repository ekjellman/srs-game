from math import log as _log, pi as _pi, sqrt as _sqrt, cos as _cos, sin as _sin
import time

# An xorshift* random number generator.
# https://en.wikipedia.org/wiki/Xorshift

BPF = 53        # Number of bits in a float
RECIP_BPF = 2**-BPF
TWOPI = 2.0*_pi
MAXINT = 0x7fffffffffffffff

class Dice(object):
  def __init__(self, seed=None):
    if seed is None:
      seed = int(time.time() * 1000)
    self.seed = self.x = seed
    self.gauss_next = None

  def _randint(self):
    assert self.x != 0, "RNG state corrupted"
    self.x = self.x ^ (self.x >> 12)
    self.x = self.x ^ (self.x << 25)
    self.x = self.x ^ (self.x >> 27)
    self.x = self.x & MAXINT
    return (self.x * 0x2545F4914F6CDD1D) & MAXINT

  def random(self):
    return (self._randint() >> 10) * RECIP_BPF

  def gauss(self, mu, sigma):
    # Adapted from CPython's random.gauss function.

    # When x and y are two variables from [0, 1), uniformly
    # distributed, then
    #
    #    cos(2*pi*x)*sqrt(-2*log(1-y))
    #    sin(2*pi*x)*sqrt(-2*log(1-y))
    #
    # are two *independent* variables with normal distribution
    # (mu = 0, sigma = 1).
    # (Lambert Meertens)
    # (corrected version; bug discovered by Mike Miller, fixed by LM)

    z = self.gauss_next
    self.gauss_next = None
    if z is None:
      x2pi = self.random() * TWOPI
      g2rad = _sqrt(-2.0 * _log(1.0 - self.random()))
      z = _cos(x2pi) * g2rad
      self.gauss_next = _sin(x2pi) * g2rad
    return mu + z*sigma

  def randint(self, a, b):
    width = b - a + 1
    return int(width * self.random()) + a

  def choice(self, seq):
    i = self.randint(0, len(seq) - 1)
    return seq[i]
