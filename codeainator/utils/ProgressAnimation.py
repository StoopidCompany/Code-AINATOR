import sys
import time
import threading

class ProgressAnimation:
    def __init__(self, message='Processing'):
        self.message = message
        self.done = False

    def animate(self):
        dots = ''
        while not self.done:
            print(f'\r{self.message}{dots}', end='')
            dots += '.'
            if len(dots) > 3:
                dots = ''
            sys.stdout.flush()
            time.sleep(0.5)
        print('\r', end='')  # Clear the line when done

    def __enter__(self):
        self.thread = threading.Thread(target=self.animate)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.done = True
        self.thread.join()