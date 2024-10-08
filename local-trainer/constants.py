DOCKER_COMPOSE_FILE_NAME = 'docker-compose.yml'

DOCKER_COMPOSE_FILE_TEMPLATE = """
services:
  training:
    image: {image}
    volumes:
{volumes}
    working_dir: /opt/ml/code
    environment:
{environment}
    command: 
      - /bin/bash
      - -c
      - {command}
"""