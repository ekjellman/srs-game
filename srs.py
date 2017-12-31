import time
from game_state import GameState

class Game:
  def __init__(self):
    # grab DOM elements
    self.encounter_panel = document.getElementById('encounterPanel')
    self.buttons = [
        document.getElementById('buttonU'),
        document.getElementById('buttonL'),
        document.getElementById('buttonR'),
        document.getElementById('buttonD')
    ]
    self.char_panel = document.getElementById('charPanel')
    self.log_panel = document.getElementById('logPanel')
    self.status_bar = document.getElementById('statusBar')

    # listen to events
    window.addEventListener('keydown', self.keydown)
    self.buttons[0].onclick = self.button_press_u
    self.buttons[1].onclick = self.button_press_l
    self.buttons[2].onclick = self.button_press_r
    self.buttons[3].onclick = self.button_press_u

    #self.encounter_panel.innerHTML = "<span style='color: brown'>Hello world</span>"
    #self.encounter_panel.innerHTML += "<br>Weapon &#x1F5E1"
    #self.encounter_panel.innerHTML += "<br>Helm &#x26D1"
    #self.encounter_panel.innerHTML += "<br>Chest &#x1f455"
    #self.encounter_panel.innerHTML += "<br>Legs &#x1f456"
    #self.encounter_panel.innerHTML += "<br>Accessory &#x1f48d"

    self.game_state = GameState()
    self.update_ui()

  def update_ui(self, character=True):
    # update encounter panel
    self.encounter_panel.innerHTML = self.game_state.panel_text()

    # update character panel
    if character:
      self.char_panel.innerHTML = str(self.game_state.character)
    else:
      self.char_panel.innerHTML = ''

    # update button labels
    labels = self.game_state.get_choices()
    for i in range(len(self.buttons)):
      if i >= len(labels):
        self.buttons[i].innerHTML = ''
        self.buttons[i].enabled = False
      else:
        self.buttons[i].innerHTML = labels[i]
        self.buttons[i].enabled = labels[i] != ''

    # update status bar
    time_spent = self.game_state.time_spent
    time_left = self.game_state.time_to_refresh()
    update_ready = "*" if self.game_state.tower_update_ready else ""
    self.status_bar.innerHTML = \
        "State: " + str(self.game_state.state) + " &nbsp;&nbsp;&nbsp; " + \
        "Energy: " + str(self.game_state.energy) + " &nbsp;&nbsp;&nbsp; " + \
        "GP: " + self.game_state.character.gold + " &nbsp;&nbsp;&nbsp; " + \
        "Time: " + time_spent + " (" + update_ready + str(time_left) + ")"

  def button_press_u(self): self.button_press(0)
  def button_press_l(self): self.button_press(1)
  def button_press_r(self): self.button_press(2)
  def button_press_d(self): self.button_press(3)

  def button_press(self, number):
    if not self.buttons[number].enabled:
      return
    logs = self.game_state.apply_choice(number)
    for log in logs:
      line = time.strftime("%m/%d/%y %H:%M:%S: ", time.localtime()) + str(log)
      self.log_panel.innerHTML += line + "<br>"
    self.update_ui()

  def keydown(self, event):
    if event.keyCode == 38: # UP
      self.button_press(0)
    elif event.keyCode == 37: # LEFT
      self.button_press(1)
    elif event.keyCode == 39: # RIGHT
      self.button_press(2)
    elif event.keyCode == 40: # DOWN
      self.button_press(3)
        
game = Game()  # Create and run game

