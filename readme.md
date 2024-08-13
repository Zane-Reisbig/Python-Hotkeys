# Python Hotkeys

### Example Usage

```python
from lib.Hotkey import Hotkey, HK_State, HK_Behavior
from keyboard import press, release

class PressW(Hotkey):
    behavior = HK_Behavior()
    behavior.wait_for_release = True

    binding = "alt+w"

    def toggle(state: HK_Behavior):
        if state == HK_Behavior.ACTIVATING:
            press("w")

        else:
            release("w")

def main():
    PressW()
    wait()

main()

```

#### That's all there is to it!

<br>
<br>
<br>

requirements:

-   keyboard
