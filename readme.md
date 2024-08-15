# Python Hotkeys

### Example Usage

```python
if __name__ == "__main__":
    from lib.Hotkey import HK_Controller, Hotkey

    print("--")
    print()

    controller = HK_Controller()
    controller.get_behavior().log_debug = True

    walk = Hotkey("alt+1", lambda: print("Hello, "), lambda: print("World!"))
    walk.get_behavior()

    controller.register(walk)
    controller.start_listeners()

    controller.wait()
```

#### That's all there is to it!

<br>
<br>
<br>

requirements:

-   keyboard
