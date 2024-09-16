# Stage 1: Build the Go application
FROM golang:1.19-alpine AS build

# Set the Current Working Directory inside the container
WORKDIR /app

# Copy go.mod and go.sum files to the workspace
COPY go.mod go.sum ./

# Download all the dependencies. Dependencies will be cached if the go.mod and go.sum files are not changed
RUN go mod download

# Copy the source code and config files into the container
COPY . .

# Build the Go application
RUN go build -o fiber-app ./main.go

# Stage 2: Run the Go application in a lightweight container
FROM alpine:latest

# Install SSL certificates (required if your API uses HTTPS)
RUN apk --no-cache add ca-certificates

# Install necessary dependencies for Postgres
RUN apk add --no-cache postgresql-client

# Set the Current Working Directory inside the container
WORKDIR /app

# Copy the built application from the build stage
COPY --from=build /app/fiber-app /app/fiber-app

# Copy the configuration files
COPY database_api_config.yaml /app/config.yaml

# Expose the port that Fiber is using (you can customize this)
EXPOSE 7000

# Command to run the application with the config file
CMD ["/app/fiber-app", "--config", "/app/config.yaml"]
