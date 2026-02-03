FROM golang:1.22-alpine AS builder

WORKDIR /app
COPY go.mod ./
RUN go mod download || true

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o server main.go

FROM alpine:latest

RUN apk add --no-cache docker-cli

WORKDIR /app
COPY --from=builder /app/server .
COPY static ./static

RUN chmod +x server

EXPOSE 8080

CMD ["./server"]
