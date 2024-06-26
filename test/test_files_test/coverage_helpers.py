def coverage_decorator(func):
    """
    This is an empty decorator that does nothing to the decorated function.
    """
    return func


def coverage_scope(*args, **kwargs):
    """
    This is an empty decorator that does nothing to the decorated function.

    N.B. It takes input parameters
    """

    def inner(func):
        '''
        do operations with func
        '''
        return func

    return inner  # this is the fun_obj
