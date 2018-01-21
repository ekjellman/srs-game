import random as python_random
import time

# Trivial implementation of the random functions we need for srs_game.
# Should be replaced with ctrueden's implementation when appropriate

def init():
  rng_seed = int(time.time() * 1000)
  python_random.seed(rng_seed)
  return rng_seed

def seed(number):
  # Will differ from Python's implementation in that the input is assumed
  # to be a number
  python_random.seed(number)

def random():
  return python_random.random()

def gauss(mu, sigma):
  return python_random.gauss(mu, sigma)

def randint(a, b):
  return python_random.randint(a, b)

def choice(seq):
  return python_random.choice(seq)
