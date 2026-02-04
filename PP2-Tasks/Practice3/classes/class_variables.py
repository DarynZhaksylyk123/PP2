#1
class Car:
    wheels = 4  # class variable
    def __init__(self, brand):
        self.brand = brand  # instance variable
car1 = Car("Toyota")
car2 = Car("BMW")
print("Example 1")
print(car1.brand, car1.wheels)
print(car2.brand, car2.wheels)
print("-" * 40)

#2
class Laptop:
    operating_system = "Windows"
    def __init__(self, model):
        self.model = model
l1 = Laptop("Dell")
l2 = Laptop("HP")
Laptop.operating_system = "Linux"
print("Example 2")
print(l1.model, l1.operating_system)
print(l2.model, l2.operating_system)
print("-" * 40)

#3
class User:
    role = "User"
    def __init__(self, username):
        self.username = username
u1 = User("admin")
u2 = User("guest")
u1.role = "Admin"
print("Example 3")
print(u1.username, u1.role)
print(u2.username, u2.role)
print("-" * 40)

#4
class Counter:
    count = 0  
    def __init__(self):
        Counter.count += 1
c1 = Counter()
c2 = Counter()
c3 = Counter()
print("Example 4")
print("Total objects created:", Counter.count)
print("-" * 40)

#5
class AppConfig:
    debug_mode = False
    def __init__(self, app_name):
        self.app_name = app_name
    def show_config(self):
        print(f"App: {self.app_name}, Debug: {AppConfig.debug_mode}")
app1 = AppConfig("Website")
app2 = AppConfig("MobileApp")
AppConfig.debug_mode = True
print("Example 5")
app1.show_config()
app2.show_config()
print("-" * 40)
