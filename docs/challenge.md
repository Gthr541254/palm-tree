# Challenge

## Notebook

Chose XGBoost, the factors are marginally better and it seemed to have better results with less training. It is also supposed to degrade less as more features are added, and despite the research results, I feel the currently selected features could change at any time and maybe start increasing. Install is big but I will have the files preinstalled.

## Repository

I do not use github at a personal level, only enterprise, so my first complaint will be the lack of credentials given, for both github and the cloud providers. Especially given both have potentially a cost assigned to them, it is the company the one that should take on the costs of their process, and the privacy breach of forcing the assignees to give away personal data to third parties unnecessarily (github and the cloud provider, through 2FA and/or payment auth operations). Hope this is improved. In any case, a dummy account holds the code:

https://github.com/Gthr541254/palm-tree

The second complaint will be a recurring one, given a public repository, the problem and solution are public, and therefore the integrity of the selection is void. Also solved by using enterprise (private) credentials. The repository is called palm-tree as a low effort to obfuscate the public solution.

## Workflow

Skipped, as I am the only developer pushing to the repository, I am used to a different although similar workflow, and can adapt to the required workflow once I have to deal with automations or other developers that require me to be strict, main is being used however.

## Folder structure

Unchanged, although Mac OS files were added to the default python gitignore.

## Challenge submission

Unsure about this, an email is far more reliable. I hope the api allows null values.

## Part I

The required file was finished, fixed minor bugs on the notebook, forced the logic to match the requirements of the test even though I felt the tests could have been modified. Use diff to review the individual changes.

Added all the helper functions from the notebook, but noticed only the one that creates the delay column is needed for the prediction.

Added a function to save the processed model to file and load it back. It seems one of the tests ended up using it.

## Part II

The required file was finished, used Pydantic to validate the input, as the OPERA column has a very limited pool of airline names at the moment, and I assume it may increase, I only validate string on the field. For the others I am more strict.

Forced the code to match the tests and not otherwise, Pydantic returns 422 on invalid request parameters, made it return 400.

Upgraded the requirement versions as there were issues on my build machine.

## Part III

Used AWS, as I don't have access to a GCP account. Aimed at a serverless architecture so I wouldn't have to bother about setup and scaling. However, AWS Lambda has a hard limit of 250MB storage, and scipy alone eats that, xgboost nearly doubles it. There are workarounds, like creating an image or hosting data on separate storage and loading it at runtime, but they have limits of their own, like price.

The best solution would probably be to use SageMaker to host the model, as it would be aligned to ML, but that service does have cost as a malus. A solution more aligned to the project files would be a load balanced swarm, but besides cost there is complexity on management.

As the stress test, which is the most difficult test on the set, runs successfully on a single worker decided to go with EC2's free tier option, it has more storage available, and would be able to pass all tests even without load balancing.

In order to deploy and not couple the github account to the cloud account I decided to use Jenkins for deployment, it can run on the same EC2 instance and avoid extra costs. Testing is done via Github Actions as originally desired.

Back to the requirements, I find it difficult to push the API url to the build files as that would create a push, which would trigger Part IV's desired CICD and generate a new API url (were it a complete CICD implementation). I must assume the goal is to setup the api skeleton manually and use CICD to push new (only) code versions to the same api. All of this is avoided with the single EC2 solution, but that is a solution I wouldn't usually use.

## Part IV

The workflow I devised is main holds the current code, and features/bugfixes go to branches that include the JIRA ticket that tracks them. They merge into main through a pull request (no develop). Releases go into release branches and may receive hotfixes that way. In the case of epics, branches similar to develop, but focused on the epic may be created and receive PRs from individual tickets.

Given this, main needed to run tests on pull requests that would come from features, and run artifact creation + deployment on merge. Github actions worked well enough for tests, applied them to pull requests. As workflows are public I cannot have cloud provider data in them, and the github account being personal I can't add cloud credentials to it. Using hosted runners didn't seem like a good idea to me, they also couple the github account to the cloud provider. I believe Jenkins is my best bet for deployment, the entry point is still cd.yml, but it ends up calling Jenkins via a webhook and it takes from there, the file Jenkinsfile has the build recipe. I also added stages for the ci part, but commented them out because github is already running them.

On the other hand, had a lot of trouble with subpar Jenkins documentation and dodgy behavior (Jenkins API Tokens require authentication anyway, what's the point). The EC2 instance is also running on the edge, almost no storage left after installing the packages required for testing, building artifacts, and hosting the software. Almost no Burst CPU credits as well.

In order to save resources, had to configure Jenkins to the minimum, keep only files for the last (current) build, and clear the workspace (build folder) after a successful build. A build takes ~1GB and I only have ~3 available after the OS and other fixed costs take their toll.

Added a clone step to the Makefile to rerun the stress test, but this time on the deployed code. This in order to verify the artifact was correctly built.
