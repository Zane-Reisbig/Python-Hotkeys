from abc import ABCMeta, abstractmethod
from keyboard import add_hotkey, wait, parse_hotkey, is_pressed, unregister_hotkey
from time import sleep
from threading import Thread

HK_Wait = wait


class HK_Behaviors:
    # Config for hotkeys

    def __init__(self) -> None:
        self.wait_for_release = False
        self.output_log = False
        self.timeout = False

    def get_set(self):
        "Gets all non Falsey attributes of self"
        out = {}

        # fmt: off
        for key in dir(self):
            found = getattr(self, key, None)
            if (
                found != None and
                "__" not in key and
                key != "get_set"
                ):
                out.update({key: found})
        # fmt: on

        return out


class HK_State:
    @staticmethod
    def invert(state: "HK_State"):
        if state == HK_State.ACTIVATING:
            return HK_State.DEACTIVATING

        return HK_State.ACTIVATING

    ACTIVATING = 1
    DEACTIVATING = 2


class Hotkey(metaclass=ABCMeta):

    @property
    @abstractmethod
    def binding() -> str:
        pass

    @abstractmethod
    def toggle(self, state: HK_State):
        """
        Implement this to control your hotkey

        ex:

        ```
        if(state == HK_State.ACTIVATING):
            myFuncHere()
        else:
            altBehavior()
        ```
        """
        pass

    def __init__(self):
        # inital state
        self.state: HK_State = HK_State.DEACTIVATING

        # set inital hotkey to config options
        add_hotkey(self.binding, self.__get_config__)

    def __get_config__(self):
        self.__behaviors__: dict | None = getattr(self, "behavior", None)
        if self.__behaviors__:
            # behaviors found
            self.__behaviors__ = self.__behaviors__.get_set()
        else:
            # if no behaviors, so dict lookups still work
            self.__behaviors__ = dict()

        # remove original hotkey with config call
        unregister_hotkey(self.binding)
        add_hotkey(self.binding, self.invoke)

        # invoke the hotkey when settings are loaded
        self.invoke()

    def __block_until_released__(self, binding=None):
        """
        Blocks until all keys are released
        """
        binding = binding or self.binding

        # steps [0] is the list of keys we need
        steps = parse_hotkey(self.binding)[0]
        # pressed = len(steps)
        # pressed[n] is whether the key is pressed
        pressed = [True for _ in range(len(steps))]

        # syntax for this is a fun little thing
        while any(pressed):
            for i, tuple in enumerate(steps):
                if is_pressed(tuple[0]):
                    pressed[i] = True
                    continue

                pressed[i] = False

    def invoke(self):
        self.state = HK_State.invert(self.state)

        # cheeky little check
        if self.__behaviors__.get("wait_for_release"):
            self.__block_until_released__()

        timeout = self.__behaviors__.get("timeout")

        if timeout:
            # literally do 'invoke' but we cant call invoke otherwise
            #   it just keeps calling itself
            def set_timeout():
                sleep(timeout)
                self.state = HK_State.invert(self.state)
                self.toggle(self.state)

            Thread(target=set_timeout, daemon=True).start()

        # finally run the user implemented toggle
        self.toggle(self.state)
