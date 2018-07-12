# NB: Using try/except in this way does not seem to work in Transcrypt.
# Fortunately, in Transcrypt mode, this variable is defined in srs.html.
# Whereas in Python mode, this variable is not, and the try/except works.
try:
  transcrypt_mode
except NameError:
  is_browser = False
  NL = '\n'
else:
  is_browser = True
  NL = '<br>'

def nl(s = ""):
    return s + NL
