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

    def __str__(self):
        return f'Student z imieniem {self.name} i średnią ocen {self.marks}.'