FROM python:3.11

COPY . /telegram_bot

WORKDIR /telegram_bot

RUN apt-get install gcc

ADD odbcinst.ini /etc/odbcinst.ini
RUN apt-get update
RUN apt-get install -y tdsodbc unixodbc-dev
RUN apt install unixodbc -y
RUN apt-get clean -y

RUN pip install --upgrade pip
RUN pip install aiofiles~=23.2.1
RUN pip install aiogram~=3.1.1
RUN pip install aiohttp==3.8.6
RUN pip install aiosignal==1.3.1
RUN pip install annotated-types==0.6.0
RUN pip install asttokens==2.4.1
RUN pip install async-timeout==4.0.3
RUN pip install attrs==23.1.0
RUN pip install certifi==2023.7.22
RUN pip install charset-normalizer==3.3.1
RUN pip install colorama==0.4.6
RUN pip install executing==2.0.1
RUN pip install frozenlist==1.4.0
RUN pip install icecream~=2.1.3
RUN pip install idna==3.4
RUN pip install magic-filter==1.0.12
RUN pip install multidict==6.0.4
RUN pip install numpy==1.26.2
RUN pip install pandas==2.1.3
RUN pip install pip==23.3.1
RUN pip install pydantic==2.4.2
RUN pip install pydantic_core==2.11.0
RUN pip install Pygments==2.16.1
RUN pip install pyodbc~=5.0.1
RUN pip install python-dotenv~=1.0.0
RUN pip install setuptools==68.2.2
RUN pip install six==1.16.0
RUN pip install typing_extensions==4.8.0
RUN pip install wheel==0.41.2
RUN pip install yarl==1.9.2

CMD ["python", "main.py"]
