import time
from src.UI import UI
from src.util.Constants import *
import src.util.HelperFunctions as HF
class Processor:
    """
    Standlone class that handles the state machine and the logic for each state.
    """
    def __init__(self, UIObj:UI = None) -> None:
        self.UIObj = UIObj
        self.stateTable = {
            "start": ["travel_to_water"],
            "travel_to_water": ["find_battle"],
            "find_battle": ["meowth_battle"],
            "meowth_battle": ["meowth_evolution", "find_battle", "meowth_death"],
            "meowth_evolution": ["find_battle"],
            "meowth_death": ["switch_pokemon"],
            "switch_pokemon": ["heal_meowth"],
            "heal_meowth": ["travel_to_water"],
            "pause": ["pause"],
            "end": ["end"],
            "reset": ["reset"]
        }
        self.currentState = "start"

    def state_machine(self, initialState:str="start") -> None:
        """
            State machine that controls the bot and moves between states.
        """
        self.currentState = initialState
        while self.currentState != "end":
            time.sleep(WAITTIME)
            previousState = self.currentState
            eval(f"self.{self.currentState}()")
            if previousState != self.currentState:
                self.print_console(f"State changed from {previousState} to {self.currentState}", "INFO")

    def start(self) -> None:
        """
            Start state. Waits for the start condition to be met.
            Start condition is where the player is infront of the pokecentre.
        """
        messageOutput = False
        # Wait for start condition
        while not HF.check_for_image("images/pokecentre_day.jpg", confidence=0.9):
            if not messageOutput:
                self.print_console("Waiting for start condition...", "INFO")
                messageOutput = True
            time.sleep(WAITTIME)
        # Start condition met
        self.print_console("Start condition met!", "GOOD")
        self.currentState = self.stateTable[self.currentState][0]

    def travel_to_water(self) -> None:
        """
        Travel to the water from the pokecentre.
        """
        time.sleep(LAGTIME)
        HF.left_click(*SCREENCOORDS)
        time.sleep(LAGTIME)
        HF.input_sequence_hold([
            ("d", 1),
            ("w", 2),
            ("a", 4),
            ("w", 1),
            ("d", 1.4),
            ("w", 2),
            ("a", 1.2),
            ("w", 3)
        ])
        #Enter water and use surf
        if not HF.check_for_image("images/nearwater_day.jpg", confidence=0.8):
            self.print_console("Failed to enter water. Resetting!", "ERROR")
            self.currentState = "reset"
            return
        time.sleep(LAGTIME)
        HF.input_sequence([
            ("z", 3),
        ], delayBetweenKeys=4)
        self.currentState = self.stateTable[self.currentState][0]

    def find_battle(self) -> None:
        """
        Find a battle by constantly moving left and right.
        """
        # Wait for battle
        while not HF.check_for_image("images/battle.jpg", confidence=0.8, grayscale=True):
            time.sleep(WAITTIME)
            HF.input_sequence_hold([
                ("a", 0.8),
                ("d", 0.8)
            ], delayBetweenKeys=0.1)
        # Battle found
        self.print_console("Battle found!", "GOOD")
        self.currentState = self.stateTable[self.currentState][0]
        return

    def meowth_battle(self) -> None:
        """
        Battle using meowth, pay day and slash.
        2 exit conditions:
            - Meowth faints
            - Meowth wins
        """
        meowthWin = False
        meowthFaint = False
        payDayUsed = False
        while not meowthWin and not meowthFaint:
            time.sleep(BATTLETIME)
            # Check if meowth fainted
            if HF.check_for_image("images/meowth_faint.jpg", confidence=0.8):
                meowthFaint = True
                self.print_console("Meowth fainted!", "INFO")
            # Check if meowth won
            elif HF.check_for_image("images/battle_won.jpg", confidence=0.5):
                meowthWin = True
                self.currentState = self.stateTable[self.currentState][1]
                self.print_console("Meowth won!", "INFO")
            #Before using a move, verify that we are on the fight screen
            elif HF.check_for_image("images/battle.jpg", confidence=0.8, grayscale=True):
                self.print_console("Battle screen found!", "INFO")
                HF.input_sequence([
                    ("w", 2),
                    ("a", 2),
                    ("z", 1),
                ], delayBetweenKeys=1)
                time.sleep(LAGTIME)
                # Use pay day
                if payDayUsed is False:
                    HF.input_sequence([
                        ("a", 2),
                        ("w", 2),
                        ("z", 1),
                    ])
                    payDayUsed = True
                else:
                    # Use slash
                    HF.input_sequence([
                        ("a", 2),
                        ("s", 2),
                        ("z", 1),
                    ])
        #Meowth fainted, need to switch pokemon, wipe and then reset
        if meowthFaint:
            # Switch to Typhlosion
            HF.input_sequence([
                ("a", 3),
                ("w", 3),
                ("d", 1),
                ("z", 1),
            ])
            self.wait_for_fight_screen()
            # Use Swift
            HF.input_sequence([
                ("z", 1),
                ("d", 2),
                ("w", 2),
                ("z", 1),
            ])
            # Wait for battle to end
            while not HF.check_for_image("images/battle_won.jpg", confidence=0.8):
                time.sleep(WAITTIME)
            self.currentState = self.stateTable[self.currentState][2]
            return

    def meowth_death(self) -> None:
        """
        Handle meowth fainting.
        """
        self.reset()
        self.heal_meowth()
        return

    def heal_meowth(self) -> None:
        """
        Enters the pokecentre to heal. Assumes you start from outside the door.
        """
        time.sleep(LAGTIME)
        # Enter pokecentre
        time.sleep(LAGTIME)
        HF.input_sequence_hold([
            ("w", 8),
        ])
        # Heal pokemon
        HF.input_sequence([
            ("z", 4),
            ("z", 2),
            ("z", 1),
        ], delayBetweenKeys=3)
        time.sleep(LAGTIME)
        # Exit pokecentre
        HF.input_sequence([
            ("s", 7)
        ])
        self.currentState = "start"
        return

    def reset(self) -> None:
        """
        Reset state by flying back to the pokecentre and changing the state to start.
        """
        time.sleep(LAGTIME)
        # Open map
        HF.input_sequence([
            ("1", 1),
        ])
        # Click on pokecentre
        tries = 0
        success = False
        while tries < 5 and success is False:
            time.sleep(LAGTIME)
            success = HF.click_on_image_location("images/playermap.jpg", confidence=0.8, clicks=2)
            tries += 1
        if not success:
            self.print_console("Failed to reset! Terminating.", "ERROR")
            self.currentState = "end"
            return
        self.currentState = "start"
        return

    def end(self) -> None:
        """
        End state. Terminates the program.
        """
        self.print_console("End state reached. Terminating.", "INFO")
        exit()

    def wait_for_fight_screen(self) -> None:
        """
        Waits for the fight screen to appear.
        """
        while not HF.check_for_image("images/battle.jpg", confidence=0.8, grayscale=True):
            time.sleep(WAITTIME)

    def print_console(self, message:str, code:str) -> None:
        """
        Prints to the console if available. If not, print to the terminal.
        """
        if self.UIObj is not None:
            self.UIObj.print_console(message, code)
        else:
            print(message)
