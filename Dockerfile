# Используем официальный образ Python
FROM python:3.11-slim-bookworm

# Устанавливаем рабочую директорию
WORKDIR /tmp

RUN apt-get update &&  apt-get install -y curl wget gcc make unixodbc unixodbc-dev odbcinst tdsodbc freetds-bin freetds-common freetds-dev procps mc htop
RUN wget https://www.freetds.org/files/stable/freetds-0.95.95.tar.gz && tar -zxf freetds-0.95.95.tar.gz
WORKDIR freetds-0.95.95
RUN ./configure --with-tdsver=7.4 --with-unixodbc=/usr --disable-static --disable-threadsafe --enable-msdblib --enable-sybase-compat --disable-sspi --with-gnu  && make && make install

COPY odbc/freetds.conf /etc/freetds.conf
COPY odbc/odbcinst.ini /etc/odbcinst.ini
COPY odbc/odbc.ini /etc/odbc.ini

# Копируем исходный код
WORKDIR /opt/telegram_bot
COPY . .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get update && apt install mc htop

RUN ["python3.11", "/opt/telegram_bot/main.py", "&"]