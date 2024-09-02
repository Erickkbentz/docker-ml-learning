from typing import List, Optional
from docker_utils import DockerComposeService, DockerComposeClient, HealthCheck
import os

class DockerMLPipelineBuilder:
    def __init__(
            self, 
            image: Optional[str], 
            source_code_dir: Optional[str],
            compose_client: Optional[DockerComposeClient] = None
        ):
        self.image = image
        self.source_code_dir = source_code_dir
        self.services = []
        self.compose_client = compose_client or DockerComposeClient(self.services)


    def add_preprocessing_stage(
            self, 
            image: Optional[str] = None, 
            command: Optional[str] = None, 
            source_code_dir: Optional[str] = None,
            volumes: Optional[List[str]] = [], 
            environment: Optional[List[str]] = None,
            depends_on: Optional[List[str]] = None
        ):
        self.add_stage(
            stage_name="preprocessing",
            image=image,
            command=command,
            source_code_dir=source_code_dir,
            volumes=volumes,
            environment=environment,
            depends_on=depends_on
        )


    def add_training_stage(
            self, 
            image: Optional[str] = None, 
            command: Optional[str] = None, 
            source_code_dir: Optional[str] = None,
            volumes: Optional[List[str]] = [], 
            environment: Optional[List[str]] = None,
            depends_on: Optional[List[str]] = None
        ):
        self.add_stage(
            stage_name="training",
            image=image,
            command=command,
            source_code_dir=source_code_dir,
            volumes=volumes,
            environment=environment,
            depends_on=depends_on
        )


    def add_serving_stage(
            self,
            image: Optional[str] = None, 
            command: Optional[str] = None,
            source_code_dir: Optional[str] = None,
            volumes: Optional[List[str]] = [], 
            environment: Optional[List[str]] = None,
            ports: Optional[List[str]] = ["8080:8080"],
            networks: Optional[List[str]] = None,
            depends_on: Optional[List[str]] = None
    ):
        self.add_stage(
            stage_name="serving",
            image=image,
            command=command,
            source_code_dir=source_code_dir,
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
            build: Optional[str] = None,
            ports: Optional[List[str]] = None,
            command: Optional[str] = None,
            volumes: Optional[List[str]] = [],
            environment: Optional[List[str]] = None,
            working_dir: Optional[str] = None,
            entrypoint: Optional[str] = None,
            networks: Optional[List[str]] = None,
            depends_on: Optional[List[str]] = None,
            restart: Optional[str] = None,
            health_check: Optional[HealthCheck] = None,
            source_code_dir: Optional[str] = None,
            detach_on_build: Optional[bool] = False
    ):
        image = image or self.image

        source_code_dir = source_code_dir or self.source_code_dir
        if source_code_dir:
            absolute_path = os.path.abspath(source_code_dir)
            volumes.append(f"{absolute_path}:/opt/ml/code")      
            if not working_dir:
                working_dir = "/opt/ml/code"
            
        
        if not depends_on:
            depends_on = []
            if self.compose_client.services:
                depends_on.append(self.compose_client.services[-1].service_name)
                

        service = DockerComposeService(
            service_name=stage_name,
            image=image,
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

        self.compose_client.compose_up(args="--build --abort-on-container-exit", services=transient_services)

        self.compose_client.compose_up(args="--build --detach", services=detatched_services)

        self.compose_client.follow_logs(services=detatched_services)