# 1. Create a generator that generates the squares of numbers up to some number N.
def square_generator(n):
    for i in range(n + 1):
        yield i * i

for value in square_generator(5):
    print(value)


# 2. Write a program using generator to print the even numbers between 0 and n in comma separated form where n is input from console.
def even_numbers(n):
    for i in range(n + 1):
        if i % 2 == 0:
            yield i

n = int(input("Enter a number: "))
print(",".join(str(num) for num in even_numbers(n)))


# 3. Define a function with a generator which can iterate the numbers, which are divisible by 3 and 4, between a given range 0 and n.
def divisible_by_3_and_4(n):
    for i in range(n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

for num in divisible_by_3_and_4(50):
    print(num)


# 4. Implement a generator called squares to yield the square of all numbers from (a) to (b). Test it with a "for" loop and print each of the yielded values.
def squares(a, b):
    for i in range(a, b + 1):
        yield i * i

for value in squares(3, 7):
    print(value)
    

# 5. Implement a generator that returns all numbers from (n) down to 0.
def countdown(n):
    while n >= 0:
        yield n
        n -= 1

for number in countdown(5):
    print(number)

