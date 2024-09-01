
This repository will be used for learning about how docker is used in the AI world. Below are a list of TODOs to help track progress. (Thank you ChatGPT!):

TODO:
- [x] Task 1 -  Set up a basic Python environment in Docker. Create a Dockerfile that installs Python and some common ML libraries like numpy, pandas, and scikit-learn.
- [x] Task 2 - Build a Docker image that runs a basic ML script to train a model on a dataset like Iris. Use scikit-learn to train and evaluate a simple classification model.
- [x] Personal Task - Create a basic image and training script to take in variable hyperparamters and input data
- [x] Task 3 - Modify your previous project to save the trained model and logs to a volume so that data is retained even after the container stops.
- [x] Personal Task - Create some abstractions to help with doing training from a notebook
- [x] Task 4 -  Create a simple ML pipeline with multiple services. For example, one container for data preprocessing, another for model training, and a third for serving the model.
- [] Task 5 - Use Docker Swarm or Kubernetes to set up a distributed training environment for a more complex model like ResNet on a dataset like CIFAR-10. Experiment with frameworks like TensorFlow or PyTorch that support distributed training.
- [] Task 6 - Set up a CI/CD pipeline using tools like Jenkins, GitHub Actions, or GitLab CI to automatically build, test, and deploy your Docker containers containing trained models to a cloud platform like AWS, GCP, or Azure.
- [] Task 7 - Build a Docker-based application that routes inputs to different models based on the domain of the question. Experiment with model ensembling techniques to combine outputs from multiple models.
- [] Task 8 -  Identify an open-source project related to ML or Docker, and start by fixing bugs, improving documentation, or adding small features.