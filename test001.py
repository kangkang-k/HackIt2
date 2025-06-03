def simple_hash(input_string):
    hash_value = 0
    for char in input_string:
        hash_value = (hash_value * 31 + ord(char)) % (2 ** 32)
    return hash_value


print(simple_hash('helloworld'))
