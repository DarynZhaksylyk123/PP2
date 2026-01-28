#1
fruits = ["apple", "banana", "cherry"]
for x in fruits:
    if x == "banana":
        continue
    print(x)
    
#2
# Example 2
for i in range(1, 6):
    if i % 2 == 0:
        continue
    print(i)