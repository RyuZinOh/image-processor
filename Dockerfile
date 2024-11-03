FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

RUN useradd -m flaskuser
USER flaskuser

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=flaskuser:flaskuser . .

EXPOSE 5000

CMD ["python", "-m", "flask", "run"]