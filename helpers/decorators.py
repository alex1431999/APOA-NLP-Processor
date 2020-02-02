"""
This file hanldes all decorators used in this project
"""

from controller import Controller

def inject_controller(func):
    """
    This function is a decorator wrapper to inject a controller to a function
    and close the controller and connection after function execution

    :param func func: The function the decorator is applied to
    """
    def inject(*args, **kwargs):
        controller = Controller()

        func(*args, **kwargs, controller=controller)

        return controller.neo_controller.session.close()
    return inject
        
