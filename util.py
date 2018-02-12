# Utility functions facilitating Transcrypt support.

def last(seq):
  # Transcrypt-friendly version of seq[-1]
  return seq[len(seq) - 1]

def capwords(s, sep=None):
  # Transcript-friendly version of string.capwords, stolen from CPython source.
  return (sep or ' ').join(x.capitalize() for x in s.split(sep))
