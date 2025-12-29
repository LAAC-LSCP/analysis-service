# Contributing to the Analysis Service
Thank you in advance for contributing to the analysis service.

## Note on the old service
This is an improvement over the original analysis service, found at https://github.com/laac-LSCP/analysis-service

Why a new service repository? The original analysis service was built with complex and unrefined requirements, in particular:

1. Tasks could be sub-tasked by the service
2. The service should be a simple Python app
3. The service might not be running on the same machine as Echolalia itself
4. We would use Slurm

Here subtasking is understood as taking a task that runs over many files–like a model over .wav files–and splitting it up. Subtasking is complex and requires extensive architectural boilerplate to implement cleanly.

However, much of the sub-tasking logic–if ever it were implemented–would be handled by Echolalia itself, as the API has changed to receive a list of file paths on which to run a model. This change removes the need for an analysis-service database and all the code patterns that come with databases or stateful applications in general.

The second requirement was reconsidered, and we adopted a multi-service approach that better decouples system components. This approach is more elegant and straightforward once set up, though it requires some expertise to develop and debug multi-service applications. For those interested in learning more, I recommend G. N. Schenker's introductory book on Docker and multi-service applications [[1]](#1).

The third requirement turned out to be incorrect, and the fourth was changed when Slurm was deemed unsuitable for load balancing and job scheduling.

Initially, I planned to avoid a more complex multi-service approach, since it's easier to understand and debug a single Python application. The benefits, however, of leveraging Docker containers, Redis as a message queue, and potentially Kubernetes are significant.

## Analysis Daemon
The `daemon` subfolder contains the analysis daemon code, that is, the Python application that does the following:

1. Periodically check for new tasks via Echolalia's REST API, and if needed spawns new runners and publish Redis events
2. Respond to published Redis events from runners, typically by sending POST requests to update task statuses

### Setup
#### Poetry
We use `poetry` for package management. `cd` into the daemon folder and run `poetry env activate` to print the full `source` bash command needed to activate the Python virtual environment. Then activate the environment with, for example

```bash
eval $(poetry env activate)
```

To install packages use `poetry add [package name]` and to update the lock file use `poetry lock`.

Note the following
1. If a suitable Python version cannot be found, it's recommended to use `pyenv` to install it, e.g., `pyenv install 3.13.0`.
2. Conda–which we too often use–does not always play well with other package managers simultaneously in the same shell, so conda may need to be deactivated (not only the conda environment) during development or, more simply, a fresh shell can be used.
3. Activating doesn't spawn a subshell, so `exit` will close your shell entirely. You could use the poetry shell plugin for more control. Finally, it is important to enter the virtual environment before installing dependencies.

To build the project just run

```bash
poetry build
```

And the source and binary distributions will appear in the `dist/` folder.

#### Testing
Run pytest as usual. In the root of the project run
```bash
pytest
```

To run the tests in various fresh virtual environments you can use tox. You can install tox via pipx `pipx install tox`.

And tox tests in python 3.13 can be run with, say
```bash
tox -e py313 -- --randomly-seed=1234
```
The seed is optional, and will shuffle the order of the tests and is good practice.
To run the full suite with linting, formatting and type-checking, you will need to install black, isort, autoflake, flake8 and mypy with pipx, and run `tox`.

#### Lint and Typecheck Locally
Install `black`, `isort`, `autoflake`, `flake8`, `mypy`, system-wide with `pipx`. Go to the repository root and run `black .`, `isort .`, `autoflake .`, `flake8 .` and `mypy .` to lint, format or type-check.

#### Commits and Semantic Versioning
We bump our releases and update our changelog automatically, but this requires commits to follow the [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) scheme. We use a combination of [release-please](https://github.com/googleapis/release-please) and [commitlint](https://commitlint.js.org/).

We recommend using squash-merge for pull requests for many reasons. Rebase-merge works too, but if you're doing something like red/green development, or did not validate all your individual commits against the actions, the main branch may not be clean after a rebase-merge (in the sense that every snapshot be clean).

```note
Note: if squashing or rebasing, the commit message must conform to commitlint's rules, otherwise release-please will not create a PR.
```

## References

<a id="1">[1]</a>
G. N. Schenker, *The ultimate Docker container book: build, test, ship, and run containers with Docker and Kubernetes*, 3rd ed. Birmingham, UK: Packt Publishing Ltd., 2023.
