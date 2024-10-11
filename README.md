# SmartShelfDBProject

## Getting started

This project assumes the baseline installation of:
- Node v21.3.0
- Python3
- SQLite3

## Dev Quickstart

Would recommend creating an alias for the command `npx nx` because that is the command to run everything in this repository

Eventually we will implement additional commands to build for Docker

### Commands For Flask Server
- `nx serve api` - Starts server
- `nx setup-venv api` - Installs requirements from pip and sets up venv (if it doesnt exist)

### Commands For Vue Server
- `nx build frontend` - Builds frontend for prod
- `nx serve frontend` - Starts server