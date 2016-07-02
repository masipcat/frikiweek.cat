FROM python:2.7

WORKDIR /src
ADD requirements.txt /src
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "frikiweek.py"]
