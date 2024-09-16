# Trivia Generation System

## Overview

This project consists of three main components:

1. **FastAPI Application**: A Python-based API using FastAPI that leverages LLaMA 3 to generate trivia questions.
2. **Python CLI**: A command-line interface (CLI) developed with Typer that serves as the entry point for the application. It invokes the Python API to generate trivia questions and then sends them to a Go-based API.
3. **Go Fiber API**: An API written in Go using the Fiber framework, which receives trivia questions and stores them in a PostgreSQL database.

## Components

### 1. FastAPI Application

- **Description**: A FastAPI-based API in Python that uses LLaMA 3 to generate trivia questions.
- **Features**:
  - Generates trivia questions based on LLaMA 3.
  - Provides an endpoint for retrieving trivia questions.
- **Setup**:
  - Install dependencies: `pip install -r requirements.txt`
  - Run the FastAPI server: `uvicorn app:app --reload`

### 2. Python CLI

- **Description**: A CLI application built with Typer that serves as the entry point for the system.
- **Features**:
  - Calls the FastAPI service to generate trivia questions.
  - Sends generated trivia questions to the Go API.
- **Setup**:
  - Run the CLI command: `python cli.py`

### 3. Go Fiber API

- **Description**: A Go-based API using the Fiber framework that receives trivia questions and saves them to a PostgreSQL database.
- **Features**:
  - Receives trivia questions from the Python CLI.
  - Saves trivia questions to a PostgreSQL database.
- **Setup**:
  - Install dependencies: `go mod download`
  - Run the Go server: `go run main.go`

## To Do

1. **Connecting All Scripts**:
   - Ensure seamless communication between the Python CLI, FastAPI, and Go Fiber API.
   - Test the complete workflow from trivia generation to database storage.

2. **Finishing Documentation**:
   - Expand on each component's setup instructions.
   - Document API endpoints, CLI commands, and database schema.
   - Provide examples of usage and troubleshooting tips.

3. **Optimizing**:
   - Review and improve code performance and efficiency.
   - Optimize data handling between services.
   - Consider scaling strategies and error handling.

## Running the Project

To run the project one has to as of now:

1. **Install Ollama and pull Llama3**:
   ```bash
    ollama pull llama3
   ```

3. **Start the trivia generator API**:
    ```bash
   python trivia_generator_api.py
   ```
4. **Start the database connection API**:
   ```bash
   go run main.go
   ```
5. **Run the CLI script**:
   ```bash
   python trivia_generator.py <category> --question-number <number>
   ```