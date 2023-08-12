# CONTRIBUTING

## DOCKER FILE CONFIGURATIONS FOR LOCAL ENV

```
FROM python:3.10
EXPOSE 5000
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["flask", "run", "--host", "0.0.0.0"]
```

## HOW TO RUN DOCKERFILE LOCALLY

```
docker build -t IMAGE_NAME
```

```
docker run -dp 5000:5000 -w /app -v "$(pwd):/app" IMAGE_NAME sh -c "flask run --host 0.0.0.0"
```