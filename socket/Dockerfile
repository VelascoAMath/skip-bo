FROM python:3.12

WORKDIR /usr/src/app/

COPY . .

ENV FLASK_APP=Skip_Bo.py

ENV FLASK_ENV=development

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD [ "python", "./Skip_Bo.py" ]

