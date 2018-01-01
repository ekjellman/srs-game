# TODO: Get rid of pylint disables in pylintrc and fix

import time
from game_state import GameState
import wx
import wx.richtext

# TODO: Look into using unicode graphics for some of this stuff
# TODO: Consider making the log stuff be in the encounter panel
#       Alternate: Put last turn of logs in there
# TODO: Either show current time or time passed in the log
# TODO: Add text describing skills to level up dialog
# TODO: Disable rest if HP/SP full? But Infinity Dungeon...
# TODO: Rename chest armor to torso/shirt/something
#       Hat / Shirt / Pants
# TODO: Change "insufficient payment" and "gold or materials" to give
#       the actual reason. Possibly snarky if you have neither
# TODO: If you have three skills, don't activate scholar (if it does)
# TODO: AutoLife seems very strong early. Could remove buffs on trigger?
# TODO: Implement a swear word filter on names
# TODO: Have a confirm screen on levelling up skills
# TODO: Make inn bento restore 1 hp as an fu
# TODO: Buff perserverance
# TODO: Get rid of status bar
# TODO: Add "time to tower reset" text
# TODO: In shops "Which item would you like to look at?"
# TODO: Make sure in-game docs note that some attacks don't work on elites
# TODO: Add a "encounters defeated" counter to Ascend Tower
# TODO: Consider making everything work against elites instead
# TODO: Consider allowing replacing skills

def write_color_text(rtc, string):
  # Takes a wx.richtext.RichTextCtrl and writes my wacky custom color-coded
  # text out to it.
  # Colors are specified via `r,g,b` in the text
  # Note: Assumes there are no "`" in the text.
  tokens = string.split("`")
  rtc.SetInsertionPoint(rtc.GetLastPosition())
  rtc.BeginTextColour((0, 0, 0))
  rtc.BeginParagraphSpacing(0, 0)
  rtc.WriteText(tokens.pop(0))
  while tokens:
    color_string = tokens.pop(0)
    r, g, b = map(int, color_string.split(","))  # pylint: disable=invalid-name
    rtc.BeginTextColour((r, g, b))
    rtc.WriteText(tokens.pop(0))
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

  def add_entry(self, text):
    line = time.strftime("%m/%d/%y %H:%M:%S: ", time.localtime()) + text + "\n"
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
    wx.Frame.__init__(self, parent, title=title, size=(1200, 600))
    self.status_bar = self.CreateStatusBar(4)
    self.status_bar.SetStatusText("Welcome to SRS Game")
    self.status_bar.SetStatusText("Energy: 0", 1)
    self.status_bar.SetStatusText("GP: 0", 2)
    self.status_bar.SetStatusText("Time: 0", 3)

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
    self.left_sizer.Add(self.encounter_panel, 4, wx.EXPAND)
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

    # TODO: This accepts multiple key presses from one key press when held,
    #       which is not great.
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
    self.update_ui(character=False)

  def update_ui(self, character=True):
    if character:
      self.char_panel.update(self.game_state)
    else:
      self.char_panel.text_field.Clear()
    self.set_labels(self.game_state.get_choices())
    self.status_bar.SetStatusText(self.game_state.current_state(), 0)
    self.encounter_panel.update(self.game_state)
    self.update_status_bars()

  def update_status_bars(self):
    #self.status_bar.SetStatusText(self.game_state.current_state(), 0)
    # TODO: Revert to above
    self.status_bar.SetStatusText(str(self.game_state.state), 0)
    self.status_bar.SetStatusText("Energy: %d" % self.game_state.energy, 1)
    self.status_bar.SetStatusText("GP: %d" % self.game_state.character.gold, 2)
    time_spent = self.game_state.time_spent
    time_left = self.game_state.time_to_refresh()
    update_ready = "*" if self.game_state.tower_update_ready else ""
    self.status_bar.SetStatusText("Time: %d (%s%d)" % (time_spent,
                                                       update_ready,
                                                       time_left), 3)

  def button_press(self, evt, number):  # pylint: disable=unused-argument
    if not self.button_panel.buttons[number].IsEnabled():
      return
    logs = self.game_state.apply_choice(number)
    for log in logs:
      # TODO: We should add more logging to just the file
      self.log_panel.add_entry(log)
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

if __name__ == "__main__":
  run_app()
