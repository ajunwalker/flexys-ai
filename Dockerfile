FROM python:3.7.3
MAINTAINER Andrew Walker
ADD . /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
CMD exec python manage.py collectstatic
CMD exec gunicorn flexys.wsgi:application --bind 0.0.0.0:8000 --workers 3
