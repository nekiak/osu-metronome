from time import sleep

import utils
from gui import MetronomeApp
import os
import sys



if __name__ == "__main__":
    try:
        utils.start_tosu()
        app = MetronomeApp()
        app.mainloop()

    finally:
        utils.kill_tosu()
