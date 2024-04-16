# Bereikbaarheid Backend Django

## About this project

This is the back-end for the [Bereikbaarheid (Reachability) application of the City of Amsterdam](https://bereikbaarheid.amsterdam.nl/).

The front-end can be found at https://github.com/Amsterdam/bereikbaarheid-frontend.

## Getting Started

### Local development

Docker Compose is used to develop locally.

- Rename the `docker-compose.override-example.yml` to `docker-compose.override.yml` (git ignored).
- Run `make dev` to start the development container locally.
- The project is now available at http://localhost:8000

### Running the app on any environment

- Run the command `make build` this will build the docker containers.
- Run the `make migrations` to build the database schema.
- Run `make app` to run the app.
