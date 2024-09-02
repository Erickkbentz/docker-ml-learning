from typing import List, Optional
import subprocess

import os
os.environ['PATH'] += ':/usr/local/bin' # I need to add this to the PATH to use docker-compose

DOCKER_COMPOSE_FILE_NAME = "docker-compose.yml"

DOCKER_COMPOSE_FILE_TEMPLATE = """
version: '3.8'
services:
  {services}
"""

DOCKER_COMPOSE_SERVICE_TEMPLATE = """
{service_name}:
{image}
{build}
{ports}
{volumes}
{working_dir}
{environment}
{command}
{entrypoint}
{networks}
{depends_on}
{restart}
{healthcheck}
"""


def format_list(items, indent=4):
        if not items:
            return ""
        return "\n" + "\n".join(f"{' ' * indent}- {item}" for item in items)

def add_indent(text, indent=4):
    return "\n".join(f"{' ' * indent}{line}" for line in text.split("\n"))

def remove_empty_lines(text):
    return "\n".join(line for line in text.split("\n") if line.strip())

def format_healthcheck(health_check):
        if not health_check:
            return ""
        
        healthcheck_str = "  healthcheck:\n"
        healthcheck_str += f"    test: {health_check.test}\n"
        healthcheck_str += f"    interval: {health_check.interval}\n"
        healthcheck_str += f"    timeout: {health_check.timeout}\n"
        healthcheck_str += f"    retries: {health_check.retries}\n"
        
        return healthcheck_str 


class HealthCheck:

    def __init__(self, test: str, interval: str, timeout: str, retries: int):
        self.test = test
        self.interval = interval
        self.timeout = timeout
        self.retries = retries


class DockerComposeService:

    def __init__(
            self, 
            service_name: str, 
            image: Optional[str] = None, 
            build: Optional[str] = None,
            ports: Optional[List[str]] = None,
            volumes: Optional[List[str]] = None, 
            working_dir: Optional[str] = None, 
            environment: Optional[List[str]] = None, 
            command: Optional[str] = None,
            entrypoint: Optional[str] = None,
            networks: Optional[List[str]] = None,
            depends_on: Optional[List[str]] = None,
            restart: Optional[str] = None,
            health_check: Optional[HealthCheck] = None,
            detach_on_build: Optional[bool] = False,
    ):
        self.service_name = service_name
        self.image = image
        self.build = build
        self.ports = ports
        self.volumes = volumes
        self.working_dir = working_dir
        self.environment = environment
        self.command = command
        self.entrypoint = entrypoint
        self.networks = networks
        self.depends_on = depends_on
        self.restart = restart
        self.health_check = health_check
        self.detach_on_build = detach_on_build


    def to_dict(self):
        service_dict = {
            "image": self.image,
            "build": self.build,
            "ports": self.ports,
            "volumes": self.volumes,
            "working_dir": self.working_dir,
            "environment": self.environment,
            "command": self.command,
            "entrypoint": self.entrypoint,
            "networks": self.networks,
            "depends_on": self.depends_on,
            "restart": self.restart,
            "healthcheck": None
        }
        if self.health_check:
            service_dict["healthcheck"] = {
                "test": self.health_check.test,
                "interval": self.health_check.interval,
                "timeout": self.health_check.timeout,
                "retries": self.health_check.retries,
            }
        return service_dict

    
    def to_yaml(self):
        formatted_build = f"  build: {self.build}" if self.build else ""
        formatted_ports = f"  ports:{format_list(self.ports)}" if self.ports else ""
        formatted_image = f"  image: {self.image}" if self.image else ""
        formatted_volumes = f"  volumes:{format_list(self.volumes)}" if self.volumes else ""
        formatted_working_dir = f"  working_dir: {self.working_dir}" if self.working_dir else ""
        formatted_environment = f"  environment:{format_list(self.environment)}" if self.environment else ""
        formatted_command = f"  command: {self.command}" if self.command else ""
        formatted_entrypoint = f"  entrypoint: {self.entrypoint}" if self.entrypoint else ""
        formatted_networks = f"  networks:{format_list(self.networks)}" if self.networks else ""
        formatted_depends_on = f"  depends_on:{format_list(self.depends_on)}" if self.depends_on else ""
        formatted_restart = f"  restart: {self.restart}" if self.restart else ""
        formatted_healthcheck = format_healthcheck(self.health_check)

        return DOCKER_COMPOSE_SERVICE_TEMPLATE.format(
            service_name=self.service_name,
            build=formatted_build,
            ports=formatted_ports,
            image=formatted_image,
            volumes=formatted_volumes,
            working_dir=formatted_working_dir,
            environment=formatted_environment,
            command=formatted_command,
            entrypoint=formatted_entrypoint,
            networks=formatted_networks,
            depends_on=formatted_depends_on,
            restart=formatted_restart,
            healthcheck=formatted_healthcheck
        )


class DockerComposeClient:
    def __init__(self, services: List[DockerComposeService]):
        self.services = services


    def add_service(self, service: DockerComposeService):
        self.services.append(service)


    def create_compose_file(self, file_name: str = DOCKER_COMPOSE_FILE_NAME):
        with open(file_name, "w") as f:
            yaml_str = self.to_yaml()
            print(f"Writing Docker Compose file:\n{yaml_str}")
            f.write(yaml_str)


    def to_yaml(self):

        services = ""
        for service in self.services:
            services += add_indent(service.to_yaml(), 2)

        compose_file = DOCKER_COMPOSE_FILE_TEMPLATE.format(services=services)

        return remove_empty_lines(compose_file)


    def compose_up(self, compose_file: str = DOCKER_COMPOSE_FILE_NAME, args: str = "", services: List[str] = []):
        self.create_compose_file()

        command = ["docker-compose", "-f", compose_file, "up"]
        if args:
            command.extend(args.split())
        if services:
            command.extend(services)
        print(f"Running command: {command}")
        
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        else:
            print(result.stdout)
        return result.returncode

    def follow_logs(self, services: List[str]):
        command = ["docker-compose", "-f", DOCKER_COMPOSE_FILE_NAME, "logs", "-f"]
        command.extend(services)
        print(f"Running command: {command}")
        subprocess.run(command)