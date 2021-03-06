# TODO: Get rid of pylint disables in pylintrc and fix

import time
from game_state import GameState
import wx
import wx.richtext
import sys
import re
import subprocess

# TODO: Change "insufficient payment" and "gold or materials" to give
#       the actual reason. Possibly snarky if you have neither
# TODO: Have a confirm screen on levelling up skills
# TODO: Make inn bento restore 1 hp as an fu
# TODO: In shops "Which item would you like to look at?"
# TODO: Make sure in-game docs note that some attacks don't work on elites
# TODO: Consider making everything work against elites instead
# TODO: Skill "Flee", (high) chance of fleeing, higher on level, xp gain on level
# TODO: Bug, something broke replays, I think in the adding a trader to the inn.
#            I haven't figured out what yet, but even the full srs_random fix
#            does not fix it
#            But: It is inconsistent even with the same log. If you have a
#                 victory log, and you pass it several times, it seems to work
#                 eventually?
# TODO: Add time reduction item to mysteries trader? Or a time slow buff
# TODO: Make a "has_buff" method on character and get rid of a lot of the
#       combined_impact stuff
# TODO: Toz said she found whether up or down is "cancelling" to be confusing
#       given leave shop is down and leave town is up. Consider adjusting this

def write_color_text(rtc, string):
  # Parses CSS-styled colors and writes them to a wx.richtext.RichTextCtrl.
  # Colors are specified in the text as '<span style=\"color: asdf\">...</span>'

  # Normalize the formatting of <span> tags so splitting is easier.
  norm_spans = string.replace('</span>', '<span style="color: rgb(0,0,0)">')

  # Parse HTML with regex; nothing can possibly go wrong.
  tokens = re.split('<span +style="color: *([^"]*)" *>', norm_spans)

  # Ensure even number of tokens, for upcoming split+zip loop.
  if len(tokens) % 2 == 1: tokens.append('')

  # Prime our area.
  rtc.SetInsertionPoint(rtc.GetLastPosition())
  rtc.BeginTextColour((0, 0, 0))
  rtc.BeginParagraphSpacing(0, 0)

  # Iterate over (string, color) pairs.
  for string, color in zip(tokens[0:][::2], tokens[1:][::2]):
    if string:
      rtc.WriteText(string)
    if color:
      r, g, b = map(int, re.findall('\d+', color))  # pylint: disable=invalid-name
      rtc.BeginTextColour((r, g, b))

  # Navigate to bottom of area.
  rtc.ShowPosition(rtc.GetLastPosition())

class ButtonPanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent, wx.NewId())
    # Buttons
    self.button_sizer = wx.GridSizer(rows=3, cols=3, hgap=5, vgap=5)
    self.button_names = ["a" * 30 for _ in range(4)]
    self.buttons = []
    for i in range(4):
      self.button_sizer.Add(wx.StaticText(self))
      self.buttons.append(wx.Button(self, -1, self.button_names[i]))
      self.button_sizer.Add(self.buttons[i], 1, wx.EXPAND)

    self.SetSizer(self.button_sizer)
    self.SetAutoLayout(1)
    self.button_sizer.Fit(self)

  def set_labels(self, labels):
    for i in range(4):
      self.buttons[i].SetLabel(labels[i])
      if labels[i] == "":
        self.buttons[i].Enable(False)
      else:
        self.buttons[i].Enable(True)

# TODO: Aren't these three panels all similar? We should be able to clean that
#       up
class CharacterPanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent, wx.NewId())
    style = wx.TE_READONLY | wx.TE_MULTILINE | wx.BORDER
    self.text_field = wx.richtext.RichTextCtrl(self, value="", style=style)
    bsizer = wx.BoxSizer(wx.VERTICAL)
    bsizer.Add(self.text_field, 1, wx.EXPAND)
    self.SetSizerAndFit(bsizer)

  def update(self, game_state):
    self.text_field.SetValue("")
    write_color_text(self.text_field, str(game_state.character))
    write_color_text(self.text_field, "\n_______\n\n")
    write_color_text(self.text_field,
                     "GP: {}\n".format(game_state.character.gold))
    if game_state.character.line_of_credit():
      write_color_text(self.text_field, "(Line of credit available)\n")
    update = "(Tower update ready)" if game_state.tower_update_ready else ""
    write_color_text(self.text_field,
                     "Time: {} {}\n".format(game_state.time_spent, update))
    write_color_text(self.text_field,
                     "(Next tower refresh in {})\n".format(game_state.time_to_refresh()))

class LastTurnPanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent, wx.NewId())
    style = wx.TE_READONLY | wx.TE_MULTILINE | wx.BORDER
    self.text_field = wx.richtext.RichTextCtrl(self, value="", style=style)
    bsizer = wx.BoxSizer(wx.VERTICAL)
    bsizer.Add(self.text_field, 1, wx.EXPAND)
    self.SetSizerAndFit(bsizer)

  def update(self, game_state):
    self.text_field.SetValue("")
    for log in game_state.last_turn_logs:
      if log.startswith("-----"):
        continue
      if log == "\n":
        continue
      write_color_text(self.text_field, str(log))
      if not (log.endswith("\n")):
        write_color_text(self.text_field, "\n")
    #write_color_text(self.text_field, "Energy: {}".format(self.game_state.energy))

class LogPanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent, wx.NewId())
    style = wx.TE_READONLY | wx.TE_MULTILINE | wx.BORDER
    self.text_field = wx.richtext.RichTextCtrl(self, value="", style=style)
    bsizer = wx.BoxSizer()
    bsizer.Add(self.text_field, 1, wx.EXPAND)
    self.SetSizerAndFit(bsizer)
    time_string = time.strftime("%m%d%y_%H%M%S", time.localtime())
    self.filename = "srs_game_%s.log" % time_string
    self.filehandle = open(self.filename, "w")
    self.max_length = 16384

  def add_entry(self, text, time_spent=0):
    time_string = time.strftime("%m/%d/%y %H:%M:%S", time.localtime())
    line = "{} ({}): {}\n".format(time_string, time_spent, text)
    write_color_text(self.text_field, line)
    self.filehandle.write(line)
    self.filehandle.flush()
    length = self.text_field.GetLastPosition()
    if length > self.max_length:
      # The text field lags on add if there is too much text. Keep it to a
      # reasonable size
      position = self.text_field.GetLastPosition() - (self.max_length // 2)
      new_line_position = self.text_field.GetValue().find("\n", position)
      if new_line_position == -1:
        new_line_position = position
      self.text_field.Remove(0, new_line_position + 1)


class EncounterPanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent, wx.NewId())
    style = wx.TE_READONLY | wx.TE_MULTILINE | wx.BORDER
    self.text_field = wx.richtext.RichTextCtrl(self, value="", style=style)
    bsizer = wx.BoxSizer()
    bsizer.Add(self.text_field, 1, wx.EXPAND)
    self.SetSizerAndFit(bsizer)

  def update(self, game_state):
    self.text_field.SetValue("")
    write_color_text(self.text_field, str(game_state.panel_text()))

class MainWindow(wx.Frame):
  # pylint: disable=too-many-instance-attributes
  def __init__(self, parent, title):
    wx.Frame.__init__(self, parent, title=title, size=(1200, 750))

    # Make menus
    menu_bar = wx.MenuBar()
    file_menu = wx.Menu()
    menu_exit = file_menu.Append(wx.NewId(), "E&xit", "Game over!")
    restart = file_menu.Append(wx.NewId(), "&Restart\tCtrl+R",
                               "Restart the game")
    menu_bar.Append(file_menu, "&File")
    self.Bind(wx.EVT_MENU, self.on_exit, menu_exit)
    self.Bind(wx.EVT_MENU, self.on_restart, restart)
    self.SetMenuBar(menu_bar)

    self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)   # Top level

    # Left side, containing the encounter panel and the button panel
    self.left_sizer = wx.BoxSizer(wx.VERTICAL)
    self.button_panel = ButtonPanel(self)
    self.encounter_panel = EncounterPanel(self)
    self.last_turn_panel = LastTurnPanel(self)
    self.left_sizer.Add(self.last_turn_panel, 3, wx.EXPAND)
    self.left_sizer.Add(self.encounter_panel, 2, wx.EXPAND)
    self.left_sizer.Add(self.button_panel, 1, wx.EXPAND)

    self.right_sizer = wx.BoxSizer(wx.VERTICAL)
    self.char_panel = CharacterPanel(self)
    self.log_panel = LogPanel(self)
    self.right_sizer.Add(self.char_panel, 2, wx.EXPAND)
    self.right_sizer.Add(self.log_panel, 1, wx.EXPAND)

    self.top_sizer.Add(self.left_sizer, 2, wx.EXPAND)
    self.top_sizer.Add(self.right_sizer, 3, wx.EXPAND)
    #self.SetSizerAndFit(self.top_sizer)
    self.SetSizer(self.top_sizer)

    # Events
    # Bind the four buttons to the button_press method
    self.Bind(wx.EVT_MENU, self.on_exit, menu_exit)
    for i in range(len(self.button_panel.buttons)):
      button = self.button_panel.buttons[i]
      button.Bind(wx.EVT_BUTTON,
                  lambda evt, number=i: self.button_press(evt, number))

    # Bind u/d/l/r for our four buttons
    bindings = [(wx.ACCEL_NORMAL, wx.WXK_UP, 0),
                (wx.ACCEL_NORMAL, wx.WXK_DOWN, 3),
                (wx.ACCEL_NORMAL, wx.WXK_LEFT, 1),
                (wx.ACCEL_NORMAL, wx.WXK_RIGHT, 2)]
    entries = []
    for binding in bindings:
      event_id = wx.NewId()
      entries.append((binding[0], binding[1], event_id))
      self.Bind(wx.EVT_BUTTON,
                lambda evt, temp=binding[2]:
                self.button_press(evt, temp), id=event_id)
    # Accelerators for menu items
    entries.append((wx.ACCEL_CTRL, ord("R"), restart.GetId()))

    accel_table = wx.AcceleratorTable(entries)
    self.SetAcceleratorTable(accel_table)

    # Update UI with initial game state
    self.initialize()

    self.Show()

  def initialize(self):
    self.game_state = GameState()
    self.log_panel.add_entry("Game initialized [Seed: {}]".format(self.game_state.rng.seed))
    self.update_ui(character=False)

  def update_ui(self, character=True):
    if character:
      self.char_panel.update(self.game_state)
    else:
      self.char_panel.text_field.Clear()
    self.set_labels(self.game_state.get_choices())
    self.encounter_panel.update(self.game_state)
    self.last_turn_panel.update(self.game_state)

  def button_press(self, evt, number):  # pylint: disable=unused-argument
    if not self.button_panel.buttons[number].IsEnabled():
      return
    logs = self.game_state.apply_choice(number)
    for log in logs:
      # TODO: We should add more logging to just the file
      self.log_panel.add_entry(log, self.game_state.time_spent)
    self.update_ui()

  def on_exit(self, evt):  # pylint: disable=unused-argument
    self.log_panel.filehandle.close()
    self.Close(True)

  def on_restart(self, evt):  # pylint: disable=unused-argument
    self.initialize()

  def set_labels(self, labels):
    self.button_panel.set_labels(labels)

def run_app():
  wx_app = wx.App(False)
  wx_frame = MainWindow(None, "SRS Game")  # pylint: disable=unused-variable
  wx_app.MainLoop()

def verify_log(filename):
  action_counter = 0
  game_state = None
  # Compiled patterns
  action = re.compile("Action selected: \[(.*)\]")
  init = re.compile("Game initialized \[Seed: (\d+)\]")
  victory = re.compile("Victory! \[(.*)\]")
  with open(filename, "r") as log_file:
    for log_line in log_file:
      if "[" not in log_line:
        continue
      if re.search(action, log_line):
        print("Action found: {}".format(m.group(1)))
        if not game_state:
          raise ValueError("Action found before game initialized")
        game_state.verification_apply_choice(m.group(1))
        action_counter += 1
        continue
      if re.search(init, log_line):
        seed = int(m.group(1))
        print("Game found")
        game_state = GameState(seed)
        continue
      if re.search(victory, log_line):
        log_time = int(m.group(1))
        game_state_time = game_state.time_spent
        if log_time != game_state_time:
          raise ValueError("Victory time does not match (log: {} game: {})".format(log_time, game_state_time))
        print("Victory: {}".format(log_time))
        continue
      raise ValueError("Unhandled line: " + log_line)

if __name__ == "__main__":
  if len(sys.argv) > 1:
    log_file = sys.argv[1]
    verify_log(log_file)
  else:
    run_app()
