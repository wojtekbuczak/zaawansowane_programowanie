class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    @property
    def is_passed(self) -> bool:
        if self.marks > 50:
            return True
        else:
            return False