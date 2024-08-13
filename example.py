from lib.Hotkey import Hotkey, HK_Behaviors, HK_State, wait


class TestHotkey(Hotkey):
    behavior = HK_Behaviors()
    behavior.wait_for_release = True
    # behavior.timeout = 1

    binding = "alt+1"

    def toggle(self, state: HK_State):
        match (state):
            case HK_State.ACTIVATING:
                print("Aloha!")

            case HK_State.DEACTIVATING:
                print("Goodbye- but in Hawaiian")


if __name__ == "__main__":
    TestHotkey()
    wait()
