from dataclasses import dataclass
from typing import Optional, Literal, List
import os
import subprocess
import constants
import textwrap

import os
os.environ['PATH'] += ':/usr/local/bin' # I need to add this to the PATH to use docker-compose

class DataChannel:
    """
    DataChannel class to store the data channel configuration.

        DataChannels can be referenced within the training container at:
            - "/opt/ml/input/{channel_name}/"
            - os.environ["INPUT_DATA_{channel_name.upper()}"]


    Attributes:
        channel_name (str): The name of the data channel.
        path (str): The local or S3 path to the data.
    """
    channel_name: str
    path: str

    def __init__(self, channel_name: str, path: str):
        self.channel_name = channel_name
        self.path = path

        if self.path.startswith("s3://"):
            self.type = "s3"
        else:
            self.type = "local"
            if not os.path.exists(self.path):
                raise ValueError(f"Path {self.path} does not exist")
        
@dataclass   
class SourceCodeConfig:
    """
    SourceCodeConfig class to store the source code configuration.

    Attributes:
        source_code_dir (str): The path to the source code directory.
        command (str): The command used to initiate training in the container within the source code directory.
            Outputs artifacts from your training scripts should be saved to the following:
                - "/opt/ml/model/" or os.enviorn["MODEL_OUTPUT_PATH"] for model artifacts
                - "/opt/ml/data/" or os.enviorn["DATA_OUTPUT_PATH"] for other artifacts

    """
    source_code_dir: Optional[str] = None
    command: Optional[str] = None

@dataclass
class ImageSpec:
    """
    Image class to store the image configuration.

    Attributes:
        image (str): The URI of the Docker image.
        image_host (Literal["ecr", "dockerhub", "local"]): The host of the Docker image. Defaults to "ecr".
        username (Optional[str]): The username to use for authentication. Defaults to None.
        password (Optional[str]): The password to use for authentication. Defaults to None.
    """
    image: str
    image_host: Literal["ecr", "dockerhub", "local"] = "ecr"
    username: Optional[str] = None
    password: Optional[str] = None


class LocalTrainer:
    def __init__(self, image: str | ImageSpec, output_path: str):
        """LocalTrainer class to train a model locally.

        Args:
            image (str | ImageSpec): The image to be used for training. This can be a URI or an ImageSpec object.
            output_path (str): The output path where the output training artifacts and data will be stored. Can be a local or S3 path.
        """
        self.image = image
        self.output_path = output_path


    def _create_docker_compose_file(self, image: str, output_path: str, input_data_channels: Optional[List[DataChannel]], source_code_config: Optional[SourceCodeConfig]):
        volumes = ""

        # Convert output_path to absolute path
        abs_output_path = os.path.abspath(output_path)
        os.makedirs(os.path.join(abs_output_path, "model"), exist_ok=True)
        os.makedirs(os.path.join(abs_output_path, "data"), exist_ok=True)

        # Add the output paths as a volume
        volumes += f"- {abs_output_path}/model:/opt/ml/model\n"
        volumes += f"- {abs_output_path}/data:/opt/ml/data\n"

        # Add the input data channels as volumes
        if input_data_channels:
            for channel in input_data_channels:
                abs_channel_path = os.path.abspath(channel.path)
                volumes += f"- {abs_channel_path}:/opt/ml/input/{channel.channel_name}\n"
        
        # Add the source code configs
        if source_code_config:
            abs_source_code_dir = os.path.abspath(source_code_config.source_code_dir)
            volumes += f"- {abs_source_code_dir}:/opt/ml/code\n"
            
            command = ""
            if source_code_config.command:
                command += source_code_config.command
        
        # Create the environment variables
        environment = f"- MODEL_OUTPUT_PATH=/opt/ml/model\n"
        environment += f"- DATA_OUTPUT_PATH=/opt/ml/data\n"

        if input_data_channels:
            for channel in input_data_channels:
                environment += f"- INPUT_DATA_{channel.channel_name.upper()}=/opt/ml/input/{channel.channel_name}\n"

        # Create the Docker Compose file
        docker_compose_file = constants.DOCKER_COMPOSE_FILE_TEMPLATE.format(
            image=image,
            volumes=textwrap.indent(volumes, " " * 6),
            command=command,
            environment=textwrap.indent(environment, " " * 6)
        )
        print(f"Docker Compose file:\n{docker_compose_file}")

        # Write the Docker Compose file
        with open(constants.DOCKER_COMPOSE_FILE_NAME, "w") as f:
            f.write(docker_compose_file)

    def run(
            self, 
            source_code_config: Optional[SourceCodeConfig] = None,
            input_data_channels: Optional[List[DataChannel]] = None
    ):
        """
        Run the training job.
        
        Args:
            source_code_config (Optional[SourceCodeConfig]): The source code configuration.
            data_channels (Optional[List[DataChannel]]): The input data channels to be mounted in the Docker container. Defaults to None. 
                To reference the data for a DataChannel with name "validation", use path "/opt/ml/input/validation/" within the container.
        """

        # Create the Dockerfile for training
        self._create_docker_compose_file(image=self.image, output_path=self.output_path, input_data_channels=input_data_channels, source_code_config=source_code_config)

        # Run the Docker container and trace the output
        process = subprocess.Popen(
            ["docker", "compose", "-f", "docker-compose.yml", "up", "--build"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Print the output in real-time
        print("Docker Compose Output:")
        for line in process.stdout:
            print(line, end='')
        for line in process.stderr:
            print(line, end='')
