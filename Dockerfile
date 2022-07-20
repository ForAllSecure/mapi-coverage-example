FROM python:3.9
LABEL maintainer="ForAllSecure, Inc"
LABEL description="Starts a FastAPI server to demonstrate coverage \
                   guided fuzzing"

WORKDIR /server

COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./src/*.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]