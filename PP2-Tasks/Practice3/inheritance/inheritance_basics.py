#1
class Person:
    def __init__(self, fname):
        self.firstname = fname

    def printname(self):
        print(self.firstname)


#2
class Student(Person):
    pass


x = Student("John")
x.printname()

#3
class Student2(Person):
    pass


s2 = Student2("Bob")
s2.printname()
