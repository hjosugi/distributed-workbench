FROM python:3.12-slim
WORKDIR /app
RUN useradd --uid 10001 --create-home app && mkdir /data && chown app:app /data
COPY architect_lab ./architect_lab
USER 10001
ENV BIND_HOST=0.0.0.0 ORDER_DB=/data/orders.db PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
EXPOSE 8080
CMD ["python", "-m", "architect_lab.server"]
