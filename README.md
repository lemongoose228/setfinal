## 1. Установка пакетов: ##

   Cледующая команда установит пакеты `python3`, `python3-pip`, `nginx` и `gunicorn`:
   ```
   sudo apt install python3 python3-pip nginx gunicorn
   ```
   А затем можно установить еще пакет `flask`, используя команду `pip install`:
   ```
   pip install flask
   ```

## 2. Клонирование git-репозитория: ##

   Для клонирования git-репозитория в домашнюю директорию можно использовать команды `cd` и `git clone`. Сначала переходим в домашнюю директорию с помощью команды `cd`:
   ```
   cd
   ```
   Затем клонируем проект с помощью команды `git clone`, указав URL репозитория:
   ```
   git clone https://github.com/lemongoose228/setfinal.git
   ```

## 3. Создание сервиса для проекта: ##

   Для создания сервиса необходимо создать файл сервиса с помощью команды `sudo nano`, указав путь к файлу. Например, так можно создать файл сервиса `set.service`:
   ```
   sudo nano /etc/systemd/system/ set.service
   ```
   В открывшемся редакторе вставьте следующий текст, заменив `имя_пользователя` на имя вашего пользователя:
   ```
   [Unit]
   Description=Service set for game Set server.
   After=network.target

   [Service]
   User=имя_пользователя
   Group=имя_пользователя
   WorkingDirectory=/home/имя_пользователя/set
   ExecStart=/usr/bin/gunicorn --workers 1 --bind unix:/home/имя_пользователя/set/set.sock run:app

   [Install]
   WantedBy=multi-user.target
   ```
## Настройка nginx: ##
   Для настройки nginx открываем файл `/etc/nginx/sites-available/default` с помощью команды `sudo nano`. В двух строках, начинающихся с `listen`, удаляем инструкцию `default_server`. Затем создаем файл `set` в папке `/etc/nginx/sites-available`:
   ```
   sudo nano /etc/nginx/sites-available/set
   ```
   Вставляем в файл следующий конфигурационный код, заменив `имя_пользователя` на имя вашего пользователя:
   ```
   server {
           listen 80 default_server;
           listen [::]:80 default_server;

           root /var/www/html;
           index _;
           server_name _;

           location / {
                   proxy_pass http://unix:/home/имя_пользователя/set/set.sock;
           }
   }
   ```
   Создаем символическую ссылку на созданный файл в папке `/etc/nginx/sites-enabled` с помощью команды `sudo ln -s`:
   ```
   sudo ln -s /etc/nginx/sites-available/set /etc/nginx/sites-enabled/
   ```
   После этого можно перезапустить nginx для применения настроек:
   ```
   sudo systemctl restart nginx
   ```
