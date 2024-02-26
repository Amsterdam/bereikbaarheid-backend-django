
## Bereikbaarheid backend django
Dit is de backend voor de bereikbaarheid website (https://bereikbaarheid.amsterdam.nl/). 
De frontend is te vinden op https://github.com/Amsterdam/bereikbaarheid-frontend.

## Getting Started
Om lokaal te kunnen ontwikkelen wordt gebruik gemaakt van Docker-compose. 

- Run the command `make build` this will build the docker containers. 
- Run the `make migrations` to build the database schema.
- Make a docker-compose.override.yml if needed.
- Run `make dev` to start the development container locally.
- The project is now available at http://localhost:8000
