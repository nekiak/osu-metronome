import utils
from gui import MetronomeApp

if __name__ == "__main__":
    try:
        utils.set_ffmpeg()
        utils.start_tosu()
        app = MetronomeApp()
        app.mainloop()
    finally:
        utils.kill_tosu()
