#1
numbers = [1, 2, 3, 4, 5, 6, 7, 8]
odd_numbers = list(filter(lambda x: x % 2 != 0, numbers))
print(odd_numbers)

#2
names = ["Anna", "Bob", "Christopher", "Eve"]
long_names = list(filter(lambda name: len(name) > 4, names))
print(long_names)

#3
values = ["Python", "", None, "Lambda", ""]
non_empty = list(filter(lambda v: v, values))
print(non_empty)

#4
greater_than_20 = list(filter(lambda x: x > 20, numbers))
print(greater_than_20)
