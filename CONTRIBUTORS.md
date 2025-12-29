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

## References

<a id="1">[1]</a>
G. N. Schenker, *The ultimate Docker container book: build, test, ship, and run containers with Docker and Kubernetes*, 3rd ed. Birmingham, UK: Packt Publishing Ltd., 2023.
