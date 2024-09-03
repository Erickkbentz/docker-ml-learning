import os

from typing import List, Optional, Tuple
from dataclasses import dataclass

from docker_utils import DockerComposeService, DockerComposeClient, HealthCheck, DependsOnService

CONTAINER_REQUIREMENTS_FILE_PATH = f"/opt/ml/code/requirements.txt"


def get_command_and_entrypoint(
    entrypoint: Optional[str], 
    command: Optional[str],
    arguments: Optional[List[str]],
    requirements: Optional[str],
    shell_command: Optional[str] = "/bin/bash"
) -> Tuple[str, str]:
    """
    Get the command and entrypoint for the Docker service.

    This function constructs the appropriate Docker entrypoint and command based on the provided arguments.
    It handles the installation of requirements if a requirements file is provided and ensures that the 
    command is properly formatted and escaped to avoid issues with special characters.

    Args:
        entrypoint (Optional[str]): The entrypoint for the Docker service. This is the initial command that 
                                    will be run inside the container.
        command (Optional[str]): The command for the Docker service. This is the main command that will be 
                                 executed after the entrypoint.
        arguments (Optional[List[str]]): The arguments for the command. These are additional parameters that 
                                         will be passed to the command.
        requirements (Optional[str]): The path to the requirements file. If provided, the function will 
                                      install the requirements before executing the command/entrypoint.
        shell_command (Optional[str]): The shell command override. Default is "/bin/bash". This is used to 
                                       specify the shell that will be used to run the commands inside the container.
    
                                       
    Returns:
        Tuple[str, str]: A tuple containing the entrypoint and command for the Docker service. The entrypoint 
                         is the initial command that will be run inside the container, and the command is the 
                         main command that will be executed after the entrypoint.

    Raises:
        ValueError: If a requirements file is specified without a command or entrypoint.

    Example:
        >>> entrypoint, command = get_command_and_entrypoint(
        ...     entrypoint="/app/start.sh",
        ...     command="python app.py",
        ...     arguments=["--debug"],
        ...     requirements="requirements.txt"
        ... )
        >>> print(entrypoint)
        /bin/bash
        >>> print(command)
        -c 'pip install --no-cache-dir -r /opt/ml/code/requirements.txt && exec /app/start.sh python app.py --debug'
    """
    docker_entrypoint = ""
    docker_command = ""
    install_requirements = ""

    # If requirements file is provided, we need to set the shell command as the entry point to install the requirements 
    # and defer the execution of the command/entrypoint until after the requirements are installed.
    if (command or entrypoint) and requirements:
        docker_entrypoint = shell_command
        install_requirements = f"pip install --no-cache-dir -r {CONTAINER_REQUIREMENTS_FILE_PATH}"

    elif (not command and not entrypoint) and requirements:
        # This case assumes the image has a default ENTRYPOINT in which case we cannot install a requirements file
        raise ValueError("Cannot specify a requirements file without a command or entrypoint.")


    if install_requirements:
        # Merge the command and arguments
        command = command + " " + " ".join(arguments) if command else " ".join(arguments)

        # If entrypoint is provided, we need to execute the command after the requirements are installed.
        entrypoint_exec = ""
        if entrypoint:
            entrypoint_exec = "exec " + entrypoint
        
        sub_command = f"{install_requirements} && {entrypoint_exec} {command}"
        
         # Escape single quotes
        sub_command = sub_command.replace("'", "\\'")
        
        docker_command = f"-c '{sub_command}'"
        
        # remove double spaces
        docker_command = " ".join(docker_command.split())

    else:

        # Merge the command and arguments
        command = command + " " + " ".join(arguments) if command else " ".join(arguments)

        # remove double spaces
        docker_command = " ".join(docker_command.split())

        docker_entrypoint = entrypoint or docker_command.split(" ")[0] 
    
    return docker_entrypoint, docker_command


class DockerMLPipelineBuilder:
    def __init__(
            self, 
            image: Optional[str],
            platform: Optional[str] = None,
            runtime: Optional[str] = None,
            source_code_dir: Optional[str] = None,
            requirements_file: Optional[str] = None,
            environment: Optional[List[str]] = None,
            compose_client: Optional[DockerComposeClient] = None
        ):
        """
        DockerMLPipelineBuilder class to build a machine learning pipeline using Docker Compose.
        
        Attributes:
            image (str): The URI of the Docker image.
            platform (str): The platform to run the Docker image on.
            source_code_dir (str): The path to the source code directory.
            requirements_file (str): The path to the requirements file within the source code directory.
            compose_client (DockerComposeClient): The DockerComposeClient instance.
        """
        self.image = image
        self.platform = platform
        self.runtime = runtime
        self.source_code_dir = source_code_dir
        self.requirements_file = requirements_file
        self.environment = environment
        self.services = []
        self.compose_client = compose_client or DockerComposeClient(self.services)


    def add_preprocessing_stage(
            self, 
            image: Optional[str] = None, 
            platform: Optional[str] = None,
            runtime: Optional[str] = None,
            command: Optional[str] = None, 
            source_code_dir: Optional[str] = None,
            requirements_file: Optional[str] = None,
            arguments: Optional[List[str]] = None,
            volumes: Optional[List[str]] = [], 
            environment: Optional[List[str]] = None,
            depends_on: Optional[List[DependsOnService]] = None
        ):
        self.add_stage(
            stage_name="preprocessing",
            image=image,
            platform=platform,
            runtime=runtime,
            command=command,
            source_code_dir=source_code_dir,
            requirements_file=requirements_file,
            arguments=arguments,
            volumes=volumes,
            environment=environment,
            depends_on=depends_on
        )


    def add_training_stage(
            self, 
            image: Optional[str] = None, 
            platform: Optional[str] = None,
            runtime: Optional[str] = None,
            command: Optional[str] = None, 
            source_code_dir: Optional[str] = None,
            requirements_file: Optional[str] = None,
            arguments: Optional[List[str]] = None,
            volumes: Optional[List[str]] = [], 
            environment: Optional[List[str]] = None,
            depends_on: Optional[List[DependsOnService]] = None
        ):
        self.add_stage(
            stage_name="training",
            image=image,
            platform=platform,
            runtime=runtime,
            command=command,
            source_code_dir=source_code_dir,
            requirements_file=requirements_file,
            arguments=arguments,
            volumes=volumes,
            environment=environment,
            depends_on=depends_on
        )


    def add_serving_stage(
            self,
            image: Optional[str] = None,
            platform: Optional[str] = None,
            runtime: Optional[str] = None,
            command: Optional[str] = None,
            source_code_dir: Optional[str] = None,
            requirements_file: Optional[str] = None,
            arguments: Optional[List[str]] = None,
            volumes: Optional[List[str]] = [], 
            environment: Optional[List[str]] = None,
            ports: Optional[List[str]] = ["8080:8080"],
            networks: Optional[List[str]] = None,
            depends_on: Optional[List[DependsOnService]] = None
    ):
        self.add_stage(
            stage_name="serving",
            image=image,
            platform=platform,
            runtime=runtime,
            command=command,
            source_code_dir=source_code_dir,
            requirements_file=requirements_file,
            arguments=arguments,
            volumes=volumes,
            environment=environment,
            ports=ports,
            networks=networks,
            depends_on=depends_on,
            detach_on_build=True
        )


    def add_stage(
            self,
            stage_name: str,
            image: Optional[str] = None,
            platform: Optional[str] = None,
            runtime: Optional[str] = None,
            build: Optional[str] = None,
            ports: Optional[List[str]] = None,
            command: Optional[str] = None,
            requirements_file: Optional[str] = None,
            arguments: Optional[List[str]] = None,
            volumes: Optional[List[str]] = [],
            environment: Optional[List[str]] = None,
            working_dir: Optional[str] = None,
            entrypoint: Optional[str] = None,
            networks: Optional[List[str]] = None,
            depends_on: Optional[List[DependsOnService]] = None,
            restart: Optional[str] = None,
            health_check: Optional[HealthCheck] = None,
            source_code_dir: Optional[str] = None,
            detach_on_build: Optional[bool] = False
    ):
        image = image or self.image
        platform = platform or self.platform
        environment = environment or self.environment
        runtime = runtime or self.runtime

        source_code_dir = source_code_dir or self.source_code_dir
        if source_code_dir:
            absolute_path = os.path.abspath(source_code_dir)
            volumes.append(f"{absolute_path}:/opt/ml/code")      
            if not working_dir:
                working_dir = "/opt/ml/code"
        
        if not depends_on:
            depends_on = []
            if self.compose_client.services:
                dependent_service = DependsOnService(
                    services=self.compose_client.services[-1].service_name,
                    condition="service_completed_successfully"
                )
                depends_on.append(dependent_service)


        entrypoint, command = get_command_and_entrypoint(
            entrypoint=entrypoint, 
            command=command, 
            arguments=arguments, 
            requirements=requirements_file or self.requirements_file
        )

        service = DockerComposeService(
            service_name=stage_name,
            image=image,
            platform=platform,
            runtime=runtime,
            build=build,
            ports=ports,
            command=command,
            working_dir=working_dir,
            volumes=volumes,
            environment=environment,
            entrypoint=entrypoint,
            networks=networks,
            depends_on=depends_on,
            restart=restart,
            health_check=health_check,
            detach_on_build=detach_on_build
        )
        self.compose_client.add_service(service)


    def build_and_run_pipeline(self):
        detatched_services = [service.service_name for service in self.compose_client.services if service.detach_on_build]
        transient_services = [service.service_name for service in self.compose_client.services if not service.detach_on_build]

        return_code = self.compose_client.compose_up(args="--build --detach", services=transient_services)

        return_code = self.compose_client.follow_logs(services=transient_services)

        if return_code != 0:
            raise Exception("Error starting the pipeline")

        return_code = self.compose_client.compose_up(args="--build --detach", services=detatched_services)

        return_code = self.compose_client.follow_logs(services=detatched_services)

        if return_code != 0:
            raise Exception("Error starting the pipeline")
