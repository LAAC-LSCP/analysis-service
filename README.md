# Analysis Service
The analysis service is a micro-service for Echolalia. It launches long-running tasks, including:

1. The voice type classifier (VTC) [[1]](#1)[[2]](#2) - note that different major versions are available, but at present (Dec 29, 2025) we use version 1
2. ChildProject's acoustics pipeline [[3]](#3)

# Setting Up
Note that we use Swarm as our orchestrator, but that Swarm is quite opinionated in how you use Docker and Docker Compose. The deployment workflow is therefore a little different from the Docker Compose (development) workflow.

## Deployment

Please install the [NVIDIA container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installing-the-nvidia-container-toolkit)

Initialise Docker Swarm (only need to do this once)
```bash
docker swarm init
```

Check your node name
```bash
docker node ls
```

And update
```bash
docker node update --label-add gpu=true <node-name>
```

Fill in the `.env` file and export into the shell
```bash
export $(cat .env | xargs)
```

Add the required images (TODO: add automated deployment to this repo)
```bash
docker build -t me/echoswarm-alice:latest ./alice-worker
docker build -t me/echoswarm-vtc:latest ./vtc-worker
docker build -t me/echoswarm-vtc-2:latest ./vtc-2-worker
docker build -t me/echoswarm-w2v2:latest ./w2v2-worker
docker build -t me/echoswarm-acoustics:latest ./acoustics-worker
docker build -t me/echoswarm-daemon:latest ./daemon
```

Then start with
```bash
docker stack deploy -c docker-compose.yml swarm-service
```

### Useful Swarm Tips
```
# check status
docker service ls

# tasks (containers)
docker service ps echoswarm-alice

# logs
docker service logs -f echoswarm-alice

# shutdown
docker stack rm swarm-service
```

## Development
For development, the `.env.test` file has already been filled in. Development may be hindered by not using a x86_64 architecture, or not being on Linux, and I suggest getting your hands on a VM if possible. This is a limitation of many of the models we run.

For development Docker Compose is the right tool. The main difference with Docker Swarm is that containers are not restarted automatically once they're brought down. Docker Swarm-compatible compose files are quite restrictive, and so we use `docker-compose.dev.yml` for development. Note that a model runner always shuts down after running a task to completion.

To run all the test containers
```bash
docker compose --env-file .env.test --profile test -f docker-compose.dev.yml up
```

## References

<a id="1">[1]</a>
T. Charlot, T. Kunze, M. Poli, A. Cristia, E. Dupoux, and M. Lavechin, ‘BabyHuBERT: Multilingual Self-Supervised Learning for Segmenting Speakers in Child-Centered Long-Form Recordings’, arXiv [eess.AS]. 2025.

<a id="2">[2]</a>
M. Lavechin, R. Bousbib, H. Bredin, E. Dupoux, and A. Cristia, ‘An open-source voice type classifier for child-centered daylong recordings’, in Interspeech, 2020.

<a id="3">[3]</a>
L. Gautheron, N. Rochat, and A. Cristia, ‘Managing, storing, and sharing long-form recordings and their annotations’, Language Resources and Evaluation, Feb. 2022.