
Название: `Коридоры замка`
Описание: 
```
Из странных писем складывается различимое послание. Кажется, я могу прочитать. «Странник! Пишет тебе князь Ксеритха. Много лет назад, на охоте, я подстрелил черную птицу. Она оказалась подручной ведьмы, и та прокляла город. С тех пор мы не можем разговаривать, не способны покинуть Ксеритх и живем во тьме. Многие пытались спасти меня – приглашенные маги, инженеры, рыцари. Но ведьма сказала, что лишь тот, кто придет из другого мира, сможет снять проклятие. Если справишься, сделаю для тебя что угодно. Чтобы начать, найди придворного мага. Он подскажет путь». Не могу поверить. Что еще за Ксеритх? Посмотреть бы в поисковике, но мой телефон не работает. Странный сбой. Серый экран, дата и время: 17 февраля 2024 года 14:12. И больше ничего. Осматриваю себя. Я как-то изменился… Меч, высокие сапоги, перчатки. Ладно… Допустим… Я – и спасение целого города? Вот к такому повороту событий привыкнуть сложнее. Я, может быть, и не хочу никого спасать. Я этот Ксеритх впервые вижу! Сдался он мне. Как до этого мага дойти-то вообще? У меня даже карты нет.
```

Дан файл:
![[easy_chipher.exe]]

Запустим его:
![[neoquest_01_run_program.png]]
Видно, что сообщение шифруется с динамичным ключом, так как на один ввод разные ответы.

Посмотрим его в DetectItEasy:
![[neoquest_DIE.png]]
exe'шник упакован с помощью Pyinstaller, значит язык - Python.

### Достаем исходный код
Попробуем достать .pyc файл из exe.
Можно использовать [pyinstxtractor](https://github.com/extremecoders-re/pyinstxtractor), но я декомпилировал [онлайн](https://pyinstxtractor-web.netlify.app/):
![[neoquest_01_exe2python.png]]
Скачиваем архив. Нам нужен файл `easy_chipher.pyc`. Если его запустить, то мы получим тот же самый функционал, как и в exe.
Открыть в редакторе его не получится, так как `.pyc` файлы - это скомпилированный байткод скрипта.

Попробуем декомпилировать в `.py` файл с помощью `decompyle3`:
![[neoquest_decompyle3.png]]
Видим ошибку, так как `decompyle3` не работает с версией `python 3.12`
Путем проб и ошибок стало ясно, что, так как 3.12 - это новая версия Python, то большинство декомпиляторов её ещё не поддерживают.
К счастью я наткнулся на [статью](https://idafchev.github.io/blog/Decompile_python/), в которой описывается подобный случай.

Для декомпиляции будем использовать [pycdc](https://github.com/zrax/pycdc), которая активно поддерживается сообществом. Для использования надо скомпилировать `pycdc.exe` из исходников.
1.  Создаем папку, например "another";
2. Копируем в него репозиторий: `git clone https://github.com/zrax/pycdc.git`;
3.  Компилируем: `cmake pycdc`;
4. Выходим из папки "another": `cd ..`;
5. Ещё раз компилируем: `cmake --build another;`
6. В папке  `.\another\Debug\` лежит `pycdc.exe`.

Запускаем: `.\pycdc.exe .\easy_chipher.pyc`:
![[neoquest_01_pycdc_error.png]]
Уже лучше! Получаем исходный код программы, правда не полный.
Видны 2 ошибки: `Unsupported opcode: BINARY_SLICE` и `Unsupported opcode: JUMP_BACKWARD`.
Ошибки в байткоде обрабатываются pycdc в файле `ASTree.cpp`, строки 2466-2471:
```
default:
	fprintf(stderr, "Unsupported opcode: %s\n", Pyc::OpcodeName(opcode & 0xFF));
	cleanBuild = false;
	return new ASTNodeList(defblock->nodes());
```
Вставим break в обработчик, тем самым продолжив декомпиляцию несмотря на ошибки:
```
default:
	fprintf(stderr, "Unsupported opcode: %s\n", Pyc::OpcodeName(opcode & 0xFF));
	break; // <----------------
	cleanBuild = false;
	return new ASTNodeList(defblock->nodes());
```
Теперь заново компилируем `pycdc.exe` и запускаем.
Получаем сий код:
```
import random
import time

def encoding(string, key):
Unsupported opcode: BINARY_SLICE
Unsupported opcode: JUMP_BACKWARD
Unsupported opcode: END_FOR
Unsupported opcode: JUMP_BACKWARD
Unsupported opcode: END_FOR
Warning: block stack is not empty!
    str_encode = ''
    for i in range(0, len(string), 6):
        block = i + 6
        encode_block = ''
        for j in range(len(block)):
            temp = ord(block[j]) ^ key[j]
            encode_block += chr(temp)
            str_encode += encode_block
            return str_encode.encode()


def getkey():
Unsupported opcode: JUMP_BACKWARD
Unsupported opcode: END_FOR
Warning: block stack is not empty!
    random.seed(int(time.time()))
    key = []
    for i in range(0, 6):
        temp = random.randint(0, 256)
        key.append(temp)
        return key

print('[*] Hey guys! This is cipher program')
print('[*] Write the message:')
message = str(input())
if message.encode() == b'\r\xc2\xa9\xc3\xae\xc3\x97\xc2\x85~t\xc2\x9d\xc2\xb9\xc3\x95\xc3\x93/u\xc3\x8f\xc2\xb9\xc3\x9f\xc2\x84xt\xc2\x9a\xc2\xb9\xc3\x97\xc3\x93+\'\xc3\x8f\xc2\xbe\xc3\x92\xc2\x8f+%\xc2\x9a\xc3\xad\xc3\x9f\xc2\x80ru\xc3\x8b\xc2\xb9\xc2\x83\xc2\x80,w\xc2\x9d\xc3\xaa\xc3\x95\xc3\x96,{\xc3\x8d\xc3\xaf\xc3\x9f\xc2\x87}!\xc3\x88\xc2\xb9\xc2\x84\xc3\x93{%\xc3\x8a\xc3\xaf\xc2\x84\xc3\x96r"\xc3\x81\xc3\xac\xc3\x9e':
    print('[ERORR] You want to hack me!? Nope.')
else:
    encode = encoding(message, getkey())
    print('[*] Encoding message: ', encode)
print('[*] Press enter to exit')
input()
```
Отлично, теперь функции `encoding()` и` getkey()` обработались до конца.
### Анализируем код
Первым делом приведем код в нормальный вид (исправим паддинги и ):
```
import random
import time

def encoding(string, key):
    str_encode = ''
    for i in range(0, len(string), 6):
        # block = i + 6 # <--- неправильная декомпиляция
        block = string[i:i + 6] # <--- правильный вариант
        encode_block = ''
        for j in range(len(block)):
            temp = ord(block[j]) ^ key[j]
            encode_block += chr(temp)
            str_encode += encode_block
    return str_encode.encode() # <--- return вернул из циклов for


def getkey():
	random.seed(int(time.time()))
    key = []
    for i in range(0, 6):
        temp = random.randint(0, 256)
        key.append(temp)
    return key # <--- return вернул из цикла for

print('[*] Hey guys! This is cipher program')
print('[*] Write the message:')
message = str(input())
if message.encode() == b'\r\xc2\xa9\xc3\xae\xc3\x97\xc2\x85~t\xc2\x9d\xc2\xb9\xc3\x95\xc3\x93/u\xc3\x8f\xc2\xb9\xc3\x9f\xc2\x84xt\xc2\x9a\xc2\xb9\xc3\x97\xc3\x93+\'\xc3\x8f\xc2\xbe\xc3\x92\xc2\x8f+%\xc2\x9a\xc3\xad\xc3\x9f\xc2\x80ru\xc3\x8b\xc2\xb9\xc2\x83\xc2\x80,w\xc2\x9d\xc3\xaa\xc3\x95\xc3\x96,{\xc3\x8d\xc3\xaf\xc3\x9f\xc2\x87}!\xc3\x88\xc2\xb9\xc2\x84\xc3\x93{%\xc3\x8a\xc3\xaf\xc2\x84\xc3\x96r"\xc3\x81\xc3\xac\xc3\x9e':
    print('[ERORR] You want to hack me!? Nope.')
else:
    encode = encoding(message, getkey())
    print('[*] Encoding message: ', encode)
print('[*] Press enter to exit')
input()
```

Теперь перед нами программа, реализующая шифрование XOR с ключом в 6 чисел.
Шифрованным сообщением, естественно, является строка, которая проверяется `if message.encode()`.
Обратим внимание на способ генерации ключа: используется `random.seed(int(time.time()))`.
`int(time.time())` в данном случае возвращает UNIX-time время, т.е. каждую секунду будет уникальный ключ.
Переведём время `17.02.2024 14:12:00` в UNIX вид: получим `1708179120`
Из описания таска мы знаем, что дата и время - 17 февраля 2024 года 14:12, секунды нам неизвестны. Благо в минуте их всего 60, мы можем пробрутить XOR с каждым из них.

Напишем программу:
```
import random
import time
current_time = 1708179120
  
def encoding(string, key):
    str_encode = ''
    for i in range(0, len(string), 6):
        block = string[i:i + 6]
        # print(block)
        encode_block = ''
        for j in range(len(block)):
            temp = ord(block[j]) ^ key[j]
            encode_block += chr(temp)
        str_encode += encode_block
    return str_encode.encode()
  
def getkey():
    # 1708179178
    random.seed(current_time)
    key = []
    for i in range(0, 6):
        temp = random.randint(0, 256)
        key.append(temp)
    return key
  
print('[*] Hey guys! This is cipher program')
print('[*] Write the message:')
message = b'\r\xc2\xa9\xc3\xae\xc3\x97\xc2\x85~t\xc2\x9d\xc2\xb9\xc3\x95\xc3\x93/u\xc3\x8f\xc2\xb9\xc3\x9f\xc2\x84xt\xc2\x9a\xc2\xb9\xc3\x97\xc3\x93+\'\xc3\x8f\xc2\xbe\xc3\x92\xc2\x8f+%\xc2\x9a\xc3\xad\xc3\x9f\xc2\x80ru\xc3\x8b\xc2\xb9\xc2\x83\xc2\x80,w\xc2\x9d\xc3\xaa\xc3\x95\xc3\x96,{\xc3\x8d\xc3\xaf\xc3\x9f\xc2\x87}!\xc3\x88\xc2\xb9\xc2\x84\xc3\x93{%\xc3\x8a\xc3\xaf\xc2\x84\xc3\x96r"\xc3\x81\xc3\xac\xc3\x9e'
message = message.decode()
for i in range(60):
    encode = encoding(message, getkey())
    print('[*] Encoding message: ', encode.decode())
    current_time+=1
```
Запускаем. На 58 секунде (`1708179178`) получаем верный флаг.
Ответ: `NQ20247ee2de67e8327be0dad7b58afb187863ed7f4e62af853807b0ecd1f23ca8a909`

## Спасибо за прочтение!
