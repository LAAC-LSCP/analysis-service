# Analysis Service
The analysis service is a micro-service for Echolalia. It launches long-running tasks, including:

1. The voice type classifier (VTC) [[1]](#1)[[2]](#2) - note that different major versions are available, but at present (Dec 29, 2025) we use version 1
2. ChildProject's acoustics pipeline [[3]](#3)

# Configuration
The service outputs files in `$DATASETS_DIR/{dataset_uid}/outputs/{task_id}`. Configuration is looked for under `$ECHOLALIA_DIR/config.toml` and must look like the following:

```toml
[http]
base_url = "https://echolalia.com"
client_id = "service"
client_secret = "5y2CAKrLLD1iGRCrpALm1dkR9"
```

The service is designed to run on a single machine together with the Echolalia software. The server environment for which it was designed is a Linux machine with `x86_64` processors, and Nvidia GPUs available, and enough space to hold the datasets as well as additional space to run the container images and running containers.

# Installation
NOTE: This will soon change

Make sure `git` is installed and configured, and configure an ssh key if not already done. Make sure `docker` and `docker-compose` are installed on the machine.

To install the software pull the repository on a clean machine
`git clone git@github.com:LAAC-LSCP/analysis-service.git`

TODO: explain configuration

In the root of the project, run `docker-compose -f docker-compose.yml build` to build the containers, and `docker-compose -f docker-compose.yml up -d`, to start them.

## References
<a id="1">[1]</a>
T. Charlot, T. Kunze, M. Poli, A. Cristia, E. Dupoux, and M. Lavechin, ‘BabyHuBERT: Multilingual Self-Supervised Learning for Segmenting Speakers in Child-Centered Long-Form Recordings’, arXiv [eess.AS]. 2025.

<a id="2">[2]</a>
M. Lavechin, R. Bousbib, H. Bredin, E. Dupoux, and A. Cristia, ‘An open-source voice type classifier for child-centered daylong recordings’, in Interspeech, 2020.

<a id="3">[3]</a>
L. Gautheron, N. Rochat, and A. Cristia, ‘Managing, storing, and sharing long-form recordings and their annotations’, Language Resources and Evaluation, Feb. 2022.