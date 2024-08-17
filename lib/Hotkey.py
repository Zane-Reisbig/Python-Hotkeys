from keyboard import add_hotkey, remove_hotkey
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, fields
from typing import Callable
from threading import Thread, Event
from time import sleep


@dataclass
class HK_Behavior:
    wait_for_release: bool = False
    log_debug: bool = False
    one_state = False
    repeat: bool = False
    repeat_delay: int = 0.2


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
        self.stop_event = self.__generate_stop__()
        self.state = HK_State.DISABLED
        self.behavior = HK_Behavior()

        self.__active_threads__: list[Thread] = []

    def __repr__(self) -> str:
        return f"HotkeyInterface(binding='{self.binding}', on='{self.on.__name__}()', off='{self.off.__name__}()')"

    def __generate_stop__(self):
        return Event()

    def __start_repeat_thread__(self):

        def repeat_thread():
            while True and not self.stop_event.is_set():
                if self.behavior.log_debug:
                    print(f"\t\t- Calling user 'on()'")

                self.on()
                if self.behavior.log_debug:
                    print(f"\t\t- Done...")
                    print(f"\t\t- Waiting: {self.behavior.repeat_delay}s")

                sleep(self.behavior.repeat_delay)

        if self.behavior.log_debug:
            print(f"\t\t- Starting thread")

        t = Thread(target=repeat_thread)
        t.start()

        self.__active_threads__.append(t)

        if self.behavior.log_debug:
            print(f"\t\t- Thread Starter done...")

    def get_behavior(self):
        return self.behavior

    def toggle(self):
        if self.behavior.log_debug:
            print(f"Toggling {repr(self.binding)} with {HK_State.to_str(self.state)}")

        match (self.state):
            case HK_State.ACTIVE:
                if self.behavior.log_debug:
                    print(f"\t- Calling 'off()' state")

                if self.behavior.repeat:
                    if self.behavior.log_debug:
                        print(f"\t- Stoping all threads")

                    self.stop_event.set()
                    for t in self.__active_threads__:
                        t.join()

                    if self.behavior.log_debug:
                        print(f"\t\t- All threads stopped...")
                        print(f"\t- Generating new stop event...")

                    self.stop_event = self.__generate_stop__()

                    if self.behavior.log_debug:
                        print(f"\t\t- Done")
                else:
                    self.off()

                if self.behavior.log_debug:
                    print(f"\t\t--Success")

                pass

            case HK_State.DISABLED:
                if self.behavior.log_debug:
                    print(f"\t- Calling 'on()' state")

                if self.behavior.repeat:
                    if self.behavior.log_debug:
                        print(f"\t- Starting repeat thread")

                    self.__start_repeat_thread__()

                    if self.behavior.log_debug:
                        print(f"\t- Started...")
                else:
                    self.on()

                if self.behavior.log_debug:
                    print(f"\t\t-- Success")

                pass

        if not self.behavior.one_state:
            if self.behavior.log_debug:
                print(f"\t- Inverting State from '{HK_State.to_str(self.state)}'")

            self.state = HK_State.invert(self.state)

        if self.behavior.log_debug:
            if self.behavior.one_state:
                print("\t- Single state Hotkey, state unchanged")
            else:
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
    """
    Quick HK_Interface macro

    Implement HK_Interface to adhere to the 'Hotkey' Protocall
    """

    on = None
    off = None
    binding = None

    def __init__(
        self,
        binding: str,
        on: Callable[[], None],
        off: Callable[[], None] = lambda: None,
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
            print(f"Registered: {repr(key)}")

        self.key_list.update({key.binding: key})

    def get_behavior(self):
        return self.behavior

    def start_listener(self, for_key):
        hotkey = self.key_list.get(for_key)

        if self.behavior.log_debug:
            print(f"Starting listener for: {repr(hotkey)}")

        add_hotkey(for_key, hotkey.toggle)

        self.active_keys.update({for_key: hotkey})

        if self.behavior.log_debug:
            print(f"\t-Success")

    def start_all_listeners(self):
        if self.behavior.log_debug:
            print(f"Starting all hotkey listeners")

        active_keys_cache = self.active_keys.keys()
        for key in filter(lambda i: i not in active_keys_cache, self.key_list.keys()):
            self.start_listener(key)

        if self.behavior.log_debug:
            print(f"Started all hotkey listeners")

    def register(self, key: HK_Interface, start_listener: bool = False):
        """
        Registers a hotkey for activation

        !! Does not start the hotkey listener !!

        !! flip 'start_listener' or call 'start_all_listeners' !!
        """

        if self.behavior.log_debug:
            print(f"Mapping key: {repr(key.binding)} thru 'HK_Controller.register()'")

        self.__map_hotkey__(key)
        if start_listener:
            self.start_listener(key.binding)

    def cleanup(self):
        if self.behavior.log_debug:
            print(f"Starting cleanup")

        for key in self.active_keys.keys():
            hotkey = self.active_keys.get(key)

            if self.behavior.log_debug:
                print(f"\t- Removing hotkey: {repr(hotkey)}")

            remove_hotkey(key)

            if self.behavior.log_debug:
                print(f"\t\t--Success")

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
    from mouse import click

    print("--")
    print()

    controller = HK_Controller()
    controller.behavior.log_debug = True

    # walk = Hotkey("alt+1", lambda: print("Hello, "), lambda: print("World!"))
    # walk.behavior.log_debug = True
    # walk.behavior.one_state = True

    click_lots = Hotkey("alt+c", lambda: click("left"))
    click_lots.behavior.repeat = True
    click_lots.behavior.repeat_delay = 0.09
    click_lots.behavior.log_debug = False

    controller.register(click_lots, True)
    controller.wait()
