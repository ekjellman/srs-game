from math import log as _log, pi as _pi, sqrt as _sqrt, cos as _cos, sin as _sin
import time

# An xorshift* random number generator.
# https://en.wikipedia.org/wiki/Xorshift

BPF = 53        # Number of bits in a float
RECIP_BPF = 2**-BPF
TWOPI = 2.0*_pi

def init():
  rng_seed = int(time.time() * 1000)
  seed(rng_seed)
  return rng_seed

x = 0
maxint = 0x7fffffffffffffff

def seed(number):
  global x
  x = number

def _randint():
  global x
  x = x ^ (x >> 12)
  x = x ^ (x << 25)
  x = x ^ (x >> 27)
  x = x % maxint
  return (x * 0x2545F4914F6CDD1D) % maxint;

def random():
  return (_randint() >> 10) * RECIP_BPF

gauss_next = None
def gauss(mu, sigma):
  global gauss_next

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

  z = gauss_next
  gauss_next = None
  if z is None:
    x2pi = random() * TWOPI
    g2rad = _sqrt(-2.0 * _log(1.0 - random()))
    z = _cos(x2pi) * g2rad
    gauss_next = _sin(x2pi) * g2rad
  return mu + z*sigma

def randint(a, b):
  range = b - a + 1
  return int(range * random()) + a

def choice(seq):
  i = randint(0, len(seq) - 1)
  return seq[i]
