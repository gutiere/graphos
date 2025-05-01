# Graphos

## Local Installation

-   [Install UV](https://docs.astral.sh/uv/getting-started/installation/)
-   Install dependencies
    -   `$ uv sync`

## Running Locally

### Start app

-   `$ uv run -m graphos.src.main`

### Debug app (VSCode)

-   `$ uv run -m debugpy --listen 2929  --wait-for-client -m graphos.src.main`
-   Hit `F5` to start the debugger
    -   If this doesn't work, ask Elijah why... we'll need to debug on your machine.

### View logs

Due to the nature of this being a terminal GUI, logs are output to `logging/application.log`

You can follow the logs live by running the following command:

-   `$  tail -f logging/application.log`

## Deploy to https://pypi.org/

-   `$ sh scripts/deploy.sh`

## Resources

-   https://www.turing.com/kb/how-to-create-pypi-packages
