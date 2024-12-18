def type5times(string):
    str2 = ""
    for i in range(5):
        str2 += string
    return str2

new_message = type5times("Hi :)\n")

print(new_message)