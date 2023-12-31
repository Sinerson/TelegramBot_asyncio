FROM python:3.11
MAINTAINER Bogdan Tabolin <tbp@sv-tel.ru>
ADD entrypoint.sh /tmp
RUN chmod +x /tmp/entrypoint.sh
RUN chmod 766 /etc/passwd

WORKDIR /opt/telegram_bot

COPY . /opt/telegram_bot

RUN apt-get install gcc
RUN apt-get install make
ENV HOME_TDS /usr/src
RUN wget https://www.freetds.org/files/stable/freetds-1.4.6.tar.gz -P $HOME_TDS
RUN wget ftp://ftp.unixodbc.org/pub/unixODBC/unixODBC-2.3.1.tar.gz -P $HOME_TDS
WORKDIR $HOME_TDS
RUN tar zxvf freetds-1.4.6.tar.gz
RUN tar zxfv unixODBC-2.3.1.tar.gz
WORKDIR $HOME_TDS/unixODBC-2.3.1
RUN ./configure
RUN make && make install
WORKDIR $HOME_TDS/freetds-1.4.6
RUN ./configure --with-tdsver=5.0 --with-unixodbc=/usr/local
RUN make && make install
WORKDIR /usr/local/etc
COPY odbc.ini ./odbcinst.ini
COPY ./odbcinst.ini ./odbc.ini
COPY freetds.conf .
RUN apt-get update
RUN apt-get -y install redis
RUN mv /etc/redis/redis.conf /etc/redis/redis.conf.old
COPY redis.conf /etc/redis
RUN apt-get install -y unixodbc unixodbc-dev
RUN odbcinst -i -d 'Adaptive Server Enterprise' -f odbcinst.ini
WORKDIR /opt/telegram_bot

RUN pip install --upgrade pip
RUN pip install aiofiles==23.2.1
RUN pip install aiogram==3.1.1
RUN pip install aiohttp==3.8.6
RUN pip install aioredis==2.0.1
RUN pip install aiosignal==1.3.1
RUN pip install annotated-types==0.6.0
RUN pip install asttokens==2.4.1
RUN pip install async-timeout==4.0.3
RUN pip install attrs==23.1.0
RUN pip install certifi==2023.7.22
RUN pip install charset-normalizer==3.3.1
RUN pip install colorama==0.4.6
RUN pip install et-xmlfile==1.1.0
RUN pip install executing==2.0.1
RUN pip install frozenlist==1.4.0
RUN pip install icecream==2.1.3
RUN pip install idna==3.4
RUN pip install magic-filter==1.0.12
RUN pip install marshmallow==3.20.1
RUN pip install multidict==6.0.4
RUN pip install numpy==1.26.2
RUN pip install openpyxl==3.1.2
RUN pip install packaging==23.2
RUN pip install pandas==2.1.3
RUN pip install pydantic==2.4.2
RUN pip install pydantic-settings==2.0.3
RUN pip install pydantic_core==2.11.0
RUN pip install Pygments==2.16.1
RUN pip install pyodbc==5.0.1
RUN pip install python-dateutil==2.8.2
RUN pip install python-dotenv==1.0.0
RUN pip install pytz==2023.3.post1
RUN pip install redis==5.0.1
RUN pip install six==1.16.0
RUN pip install typing_extensions==4.8.0
RUN pip install tzdata==2023.3
RUN pip install XlsxWriter==3.1.9
RUN pip install yarl==1.9.2

ENTRYPOINT /tmp/entrypoint.sh