FROM python:3.10
EXPOSE 80
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cahe-dir --upgrade -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:create_app()"]