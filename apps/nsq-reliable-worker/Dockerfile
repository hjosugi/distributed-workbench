FROM golang:1.25-alpine AS build
ARG TARGET=api
WORKDIR /src
COPY go.mod ./
COPY . .
RUN CGO_ENABLED=0 go build -trimpath -ldflags='-s -w' -o /out/app ./cmd/${TARGET}

FROM alpine:3.22
RUN addgroup -S app && adduser -S -G app app
WORKDIR /app
COPY --from=build /out/app /usr/local/bin/app
RUN mkdir -p /data && chown app:app /data
USER app
EXPOSE 8082 8083
ENTRYPOINT ["app"]
