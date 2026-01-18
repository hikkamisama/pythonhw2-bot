FROM python:3.13

WORKDIR ./

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app/bot.py"]