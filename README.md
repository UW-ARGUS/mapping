# ARGUS Mapping Software

## Overview
The purpose of this repository is to house the mapping software for the base terminal.

## Setup
1. Clone the `mapping` repository with the command below

```
git clone https://github.com/UW-ARGUS/mapping.git
```

2. Ensure you have python version 3.11 or greater installed. Run the command below to check the python version.
```
python --version
# Example output: Python 3.11.2
```

3. Create a virtual environment. At the root of the repository, run the command below. This command should create a hidden folder at the root of the repository named `.venv`.
```
python -m venv .venv
```

4. Activate the virtual environment by running the command below based on your operating system.

    - **Windows**
    ```
    .venv\Scripts\activate
    ```
    - **Linux or MacOS**
    ```
    source .venv/bin/activate
    ```
5. Install project dependencies with `pip` by running the command below at the root of the repository.
```
pip install -r requirements.txt
```
## Teardown
To deactivate the virtual environment, run the command below.
```
deactivate
```
