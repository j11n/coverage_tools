"""
    This file is used as python source code when testing 
    improved coverage calculation
"""
import dataclasses


class MyClass:
    def __init__(self):
        self.data = 5
        self.text = 'hello'
        self._number = 7

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        self._number = value

    @number.deleter
    def number(self):
        self._number = value

@dataclasses.dataclass
class MyDataClass:
    data: int = 5

    def __post_init__(self):
        #
        #
        if self.data == 5:
            print('Default value')


def main():
    my_inst = MyClass()
    my_data_inst = MyDataClass(data=7)


if __name__ == '__main__':
    main()
