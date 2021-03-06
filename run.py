"""
Accepts input commands and runs scripts accordingly
"""

import sys

from controller import Controller

def run(mode):
    # Create a new controller instance
    controller = Controller()

    # Run the specified mode
    if mode == 'full':
        return controller.run_full()
    else:
        return print('Please enter a valid mode')


if __name__ == '__main__':
    mode = sys.argv[1]
    run(mode)
