"""

"""


def my_function(var):
    if var == 7:
        print('var was 7')
    else:
        var = get_var_value()
    return 2 * var


def get_var_value():
    return 10


class TopClass:

    class InnerClass:
        def __init__(self):
            self.b = 77

        def get_b(self):
            return self.b

    def __init__(self):
        self.a = True
        self.inner_b = TopClass.InnerClass()
    
    def get_inner_b(self):
        return self.inner_b.get_b()


def mult_by_two(number):
    return 2 * number
