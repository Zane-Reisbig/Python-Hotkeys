# Python Hotkeys

### Example Usage

```python
if __name__ == "__main__":
    from lib.Hotkey import HK_Controller, Hotkey

    print("--")
    print()

    controller = HK_Controller()
 
    walk = Hotkey("alt+1", lambda: print("Hello, "), lambda: print("World!"))
    #                      ^ On State                ^ Off State

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
