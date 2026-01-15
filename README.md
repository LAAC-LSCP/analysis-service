# Analysis Service
The analysis service is a micro-service for Echolalia. It launches long-running tasks, including:

1. The voice type classifier (VTC) [[1]](#1)[[2]](#2) - note that different major versions are available, but at present (Dec 29, 2025) we use version 1
2. ChildProject's acoustics pipeline [[3]](#3)

# Setting Up
Fill in the `.env.prod` file and use
```bash
docker compose --env-file .env.prod --profile prod -f docker-compose.yml up
```

To start up the services

## References

<a id="1">[1]</a>
T. Charlot, T. Kunze, M. Poli, A. Cristia, E. Dupoux, and M. Lavechin, ‘BabyHuBERT: Multilingual Self-Supervised Learning for Segmenting Speakers in Child-Centered Long-Form Recordings’, arXiv [eess.AS]. 2025.

<a id="2">[2]</a>
M. Lavechin, R. Bousbib, H. Bredin, E. Dupoux, and A. Cristia, ‘An open-source voice type classifier for child-centered daylong recordings’, in Interspeech, 2020.

<a id="3">[3]</a>
L. Gautheron, N. Rochat, and A. Cristia, ‘Managing, storing, and sharing long-form recordings and their annotations’, Language Resources and Evaluation, Feb. 2022.