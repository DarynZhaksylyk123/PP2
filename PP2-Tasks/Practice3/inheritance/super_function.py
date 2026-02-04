#1
class Person:
    def __init__(self, fname, lname):
        self.firstname = fname
        self.lastname = lname

    def printname(self):
        print(self.firstname, self.lastname)

#2
class Student(Person):
    def __init__(self, fname, lname, year):
        self.graduationyear = year
        Person.__init__(self, fname, lname)


s = Student("Mike", "Olsen", 2024)
s.printname()
print(s.graduationyear)

#3
class Student2(Person):
    def __init__(self, fname, lname, year):
        super().__init__(fname, lname)
        self.graduationyear = year


s2 = Student2("Anna", "Smith", 2025)
s2.printname()
print(s2.graduationyear)
