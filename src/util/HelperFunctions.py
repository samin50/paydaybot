import time
import random
import keyboard
import pyautogui as pg
from src.util.Constants import *
import win32api
import win32con

def left_click(x:int, y:int, randomness:int=0) -> None:
    """
    Uses win32api to left click at the given coordinates.
    """
    if randomness != 0:
        x += random.randint(-randomness, randomness)
        y += random.randint(-randomness, randomness)
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

def check_for_image(imagePath:str, confidence:float=0.8, **kwargs:dict) -> bool:
    """
    Checks for the given image on the screen.
    """
    return pg.locateOnScreen(imagePath, confidence=confidence, **kwargs) is not None

def input_sequence(sequence:list, pressLength:float=0.2, delayBetweenKeys:float=0.15) -> None:
    """
    Given a list of (key, no.times), press the keys the specified number of times.
    """
    for key, value in sequence:
        for _ in range(value):
            keyboard.press(key)
            time.sleep(pressLength)
            keyboard.release(key)
            time.sleep(delayBetweenKeys)

def input_sequence_hold(sequence:list, delayBetweenKeys:float=0.15) -> None:
    """
    Given a list of (key, time), press the key for the specified time.
    """
    for key, value in sequence:
        keyboard.press(key)
        time.sleep(value)
        keyboard.release(key)
        time.sleep(delayBetweenKeys)

def click_screen() -> None:
    """
    Clicks the screen.
    """
    left_click(*SCREENCOORDS)
    time.sleep(LAGTIME)

def click_on_image_location(imagePath:str, confidence:float=0.8, clicks:int=1, **kwargs:dict) -> None:
    """
    Clicks on the center of the image location.
    """
    location = pg.locateOnScreen(imagePath, confidence=confidence, **kwargs)
    if location is not None:
        for _ in range(clicks):
            left_click(int(location.left + location.width/2), int(location.top + location.height/2))
            time.sleep(0.1)
        return True
    else:
        print(f"Failed to find {imagePath}")
        return False
