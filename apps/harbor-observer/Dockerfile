FROM golang:1.25-alpine AS build
WORKDIR /src
COPY go.mod ./
COPY . .
RUN CGO_ENABLED=0 go build -trimpath -ldflags='-s -w' -o /out/harbor-observer ./cmd/harbor-observer

FROM alpine:3.22
RUN addgroup -S app && adduser -S -G app app
WORKDIR /app
COPY --from=build /out/harbor-observer /usr/local/bin/harbor-observer
RUN mkdir -p /data && chown app:app /data
USER app
EXPOSE 8081
ENTRYPOINT ["harbor-observer"]
