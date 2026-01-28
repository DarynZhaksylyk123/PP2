#1
fruits = ["apple", "banana", "cherry"]
for x in fruits:
    print(x)
    if x == "banana":
        break
    
#2
fruits = ["apple", "banana", "cherry"]
for x in fruits:
    if x == "banana":
        break
    print(x)
    
#3
# Example 3
for i in range(1, 6):
    if i == 3:
        break
    print(i)