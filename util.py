# Utility functions facilitating Transcrypt support.

def last(seq):
  # Transcrypt-friendly version of seq[-1]
  return seq[len(seq) - 1]

def capwords(s, sep=None):
  # Transcript-friendly version of string.capwords, stolen from CPython source.
  return (sep or ' ').join(x.capitalize() for x in s.split(sep))

def pd(number):
  # Transcrypt-friendly '{:+d}' string formatting.
  symbol = '+' if number >= 0 else '-'
  return symbol + str(abs(number))

def f1(number):
  # Transcrypt-friendly '{:.1f}' string formatting.
  return f(number, 1, False)

def f2(number):
  # Transcrypt-friendly '{:.2f}' string formatting.
  return f(number, 2, False)

def pf1(number):
  # Transcrypt-friendly '{:+.1f}' string formatting.
  return f(number, 1, True)

def pf2(number):
  # Transcrypt-friendly '{:+.2f}' string formatting.
  return f(number, 2, True)

def f(number, places, prefix=False):
  # Compute the scaling factor for cutoff/rounding.
  # NB: Transcrypt uses Math.pow, not pow. Easier to do it manually.
  factor = 1
  for _ in range(places):
    factor *= 10
  # Round to specified number of decimal places.
  v = int(factor * number + 0.5) / factor
  # Glean the prefix symbol.
  plus = '+' if prefix else ''
  symbol = plus if v >= 0 else '-'
  # Append trailing zeros as needed.
  s = str(abs(v))
  if s.rfind('.') < 0:
    s += '.'
  while len(s) - s.rfind('.') <= places:
    s += '0'
  # Put it all together.
  return symbol + s
