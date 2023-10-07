FROM python:3.11-alpine
LABEL likelion.web.backendauthor="Ivan kim <xormrdlsrks2@gmail.com>"

ARG APP_HOME=/app

ENV PYTHONUNBUFFERED 1

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR ${APP_HOME}

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ${APP_HOME}

COPY ./scripts/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./scripts/entrypoint /entrypoint
# entrypoint 파일 실행
RUN sed -i 's/\r$//g' /entrypoint
# \r : 캐리지 리턴
RUN chmod +x /entrypoint

ENTRYPOINT [ "/entrypoint" ]
CMD [ "/start" ]