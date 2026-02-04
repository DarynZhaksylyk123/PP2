#1
class Person:
    def message(self):
        print("This is a person")


p = Person()
p.message()

#2
class Student(Person):
    def message(self):
        print("This is a student")


s = Student()
s.message()

#3
people = [Person(), Student()]

for person in people:
    person.message()
