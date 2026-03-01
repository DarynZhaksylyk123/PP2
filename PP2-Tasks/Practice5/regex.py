import re

# 1. 'a' followed by zero or more 'b's

print("1. 'a' followed by zero or more 'b's")
text1 = "a ab abb abbb ac"
pattern1 = r"ab*"
print(re.findall(pattern1, text1))  # ['a', 'ab', 'abb', 'abbb']


# 2. 'a' followed by 2 to 3 'b's

print("\n2. 'a' followed by 2 to 3 'b's")
text2 = "ab abb abbb abbbb"
pattern2 = r"ab{2,3}"
print(re.findall(pattern2, text2))  # ['abb', 'abbb']


# 3. Lowercase letters joined with underscore

print("\n3. Lowercase letters joined with underscore")
text3 = "hello_world foo_bar abc_def GHI_JKL"
pattern3 = r"[a-z]+_[a-z]+"
print(re.findall(pattern3, text3))  


# 4. Uppercase letter followed by lowercase letters

print("\n4. Uppercase letter followed by lowercase letters")
text4 = "Hello World Python RegEx"
pattern4 = r"[A-Z][a-z]+"
print(re.findall(pattern4, text4))  # ['Hello', 'World', 'Python', 'Reg']


# 5. 'a' followed by anything ending with 'b'

print("\n5. 'a' followed by anything ending with 'b'")
text5 = "ab acb aXYZb a123b a_b"
pattern5 = r"a.*b"
print(re.findall(pattern5, text5))  # ['ab', 'acb', 'aXYZb', 'a123b', 'a_b']


# 6. Replace space, comma, or dot with colon

print("\n6. Replace space, comma, or dot with colon")
text6 = "Hello, world. This is Python"
pattern6 = r"[ ,.]"
print(re.sub(pattern6, ":", text6))  # "Hello:world:This:is:Python"


# 7. Convert snake_case to camelCase

print("\n7. Convert snake_case to camelCase")
text7 = "this_is_snake_case"
camel_case = re.sub(r"_([a-z])", lambda m: m.group(1).upper(), text7)
print(camel_case)  # "thisIsSnakeCase"


# 8. Split string at uppercase letters

print("\n8. Split string at uppercase letters")
text8 = "HelloWorldPython"
parts = re.split(r"(?=[A-Z])", text8)
print(parts)  # ['', 'Hello', 'World', 'Python']


# 9. Insert spaces before capital letters

print("\n9. Insert spaces before capital letters")
spaced = re.sub(r"(?<!^)(?=[A-Z])", " ", text8)
print(spaced)  # "Hello World Python"


# 10. Convert camelCase to snake_case

print("\n10. Convert camelCase to snake_case")
text10 = "thisIsCamelCase"
snake_case = re.sub(r"([A-Z])", r"_\1", text10).lower()
print(snake_case)  # "this_is_camel_case"