from keyboard import add_hotkey, remove_hotkey
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, fields
from typing import Callable
from threading import Thread, Event


@dataclass
class HK_Behavior:
    wait_for_release: bool = False
    log_debug: bool = False


@dataclass
class HK_Controller_Behavior:
    allow_key_overwrite: bool = False
    log_debug: bool = False


@dataclass
class HK_State:
    ACTIVE: int = 0
    DISABLED: int = 1

    @staticmethod
    def invert(state):
        if state == 0:
            return 1

        return 0

    @staticmethod
    def to_str(state):
        if state == 0:
            return "ACTIVE"

        return "DISABLED"


class HK_Interface(metaclass=ABCMeta):

    def __init__(self, *args, **kwargs):
        self.state = HK_State.DISABLED
        self.behavior = HK_Behavior()

    def get_behavior(self):
        return self.behavior

    def __repr__(self) -> str:
        return f"HotkeyInterface(binding='{self.binding}', on='{self.on.__name__}()', off='{self.off.__name__}()')"

    def toggle(self):
        if self.behavior.log_debug:
            print(f"Toggling {repr(self.binding)} with {repr(self.state)}")

        match (self.state):
            case HK_State.ACTIVE:
                if self.behavior.log_debug:
                    print(f"\t- Calling 'on()' state")

                self.off()

                if self.behavior.log_debug:
                    print(f"\t\t--Success")

                pass

            case HK_State.DISABLED:
                if self.behavior.log_debug:
                    print(f"\t- Calling 'off()' state")

                self.on()

                if self.behavior.log_debug:
                    print(f"\t\t-- Success")

                pass

        if self.behavior.log_debug:
            print(f"\t- Inverting State from '{HK_State.to_str(self.state)}'")

        self.state = HK_State.invert(self.state)

        if self.behavior.log_debug:
            print(f"\t- State set to '{HK_State.to_str(self.state)}'")

    @property
    @abstractmethod
    def binding() -> str:
        pass

    @abstractmethod
    def on():
        pass

    @abstractmethod
    def off():
        pass


class Hotkey(HK_Interface):
    on = None
    off = None
    binding = None

    def __init__(
        self, binding: str, on: Callable[[], None], off: Callable[[], None]
    ) -> None:
        super().__init__()

        self.binding = binding
        self.on = on
        self.off = off


class HK_Controller:
    def __init__(self, initial: list[HK_Interface] = []) -> None:
        self.behavior = HK_Controller_Behavior()
        self.active_keys: dict[str, HK_Interface] = {}
        self.key_list: dict[str, HK_Interface] = {}
        self.stop_keybind = None
        self.stop_event = self.__generate_stop__()

        [self.register(init) for init in initial]

    def __generate_stop__(self):
        return Event()

    def __map_hotkey__(self, key: HK_Interface):
        if self.behavior.log_debug:
            print(f"Adding key: {repr(key.binding)}")

        if self.key_list.get(key.binding) and not self.behavior.allow_key_overwrite:
            raise AssertionError(
                f"Bind: {key.binding} is already in use.\nBound to {key.on.__name__}"
            )

        if self.behavior.log_debug:
            print(f"{repr(key)} -> Registered")

        self.key_list.update({key.binding: key})

    def get_behavior(self):
        return self.behavior

    def start_listeners(self):
        if self.behavior.log_debug:
            print(f"Starting hotkey listeners")

        for key in self.key_list.keys():

            hotkey = self.key_list.get(key)

            if self.behavior.log_debug:
                print(f"\t- Adding hotkey: {repr(hotkey)}")

            add_hotkey(key, hotkey.toggle)

            self.active_keys.update({key: hotkey})

            if self.behavior.log_debug:
                print(f"\t\t-Success")

    def register(self, key: HK_Interface):
        if self.behavior.log_debug:
            print(f"Mapping key: {repr(key.binding)} thru 'HK_Controller.register()'")

        self.__map_hotkey__(key)

    def cleanup(self):
        if self.behavior.log_debug:
            print(f"Starting cleanup")

        for key in self.active_keys.keys():
            hotkey = self.active_keys.get(key)

            if self.behavior.log_debug:
                print(f"\t- Removing hotkey: {repr(hotkey)}")

            remove_hotkey(key)

            if self.behavior.log_debug:
                print(f"\t\t-Success")

        self.active_keys = {}

        if self.behavior.log_debug:
            print(f"Setting stop Event...")

        self.stop_event.set()

    def wait(self, stop_keybind="ctrl+f12"):
        self.stop_keybind = stop_keybind
        add_hotkey(stop_keybind, self.cleanup)

        if self.behavior.log_debug:
            print(f"Waiting for stop Event...")

        self.stop_event.wait()

        if self.behavior.log_debug:
            print(f"Stop Event received!")
            print(f"Removing stop hotkey: {repr(stop_keybind)}")

        remove_hotkey(stop_keybind)

        if self.behavior.log_debug:
            print(f"Finished Cleaning")

        return True


if __name__ == "__main__":
    print("--")
    print()

    controller = HK_Controller()
    controller.get_behavior().log_debug = True

    walk = Hotkey("alt+1", lambda: print("Hello, "), lambda: print("World!"))
    walk.get_behavior().log_debug = True

    controller.register(walk)
    controller.start_listeners()

    controller.wait()
