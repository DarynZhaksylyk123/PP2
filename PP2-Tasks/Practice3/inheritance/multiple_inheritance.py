#1
class Father:
    def skill1(self):
        print("Driving")

#2
class Mother:
    def skill2(self):
        print("Cooking")

#3
class Child(Father, Mother):
    pass


c = Child()
c.skill1()
c.skill2()
