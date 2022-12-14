FROM python:3.11
COPY requirements.txt .
COPY collect.py /
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "/collect.py"]


