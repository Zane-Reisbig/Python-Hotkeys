import keyboard
import mouse
from lib.Hotkey import Hotkey, HK_Behaviors, HK_State, HK_Wait


class ClickAndHold(Hotkey):
    behavior = HK_Behaviors()
    behavior.wait_for_release = True

    binding = "alt+c"

    def toggle(self, state: HK_State):
        match (state):
            case HK_State.ACTIVE:
                mouse.hold("left")

            case HK_State.DISABLED:
                mouse.release("left")


class AutoRun(Hotkey):
    behavior = HK_Behaviors()
    behavior.wait_for_release = True

    binding = "alt+w"

    def toggle(self, state: HK_State):
        match (state):
            case HK_State.ACTIVE:
                keyboard.press("w")
                keyboard.press("shift")

            case HK_State.DISABLED:
                keyboard.release("w")
                keyboard.release("shift")


if __name__ == "__main__":
    ClickAndHold()
    AutoRun()
    HK_Wait()
