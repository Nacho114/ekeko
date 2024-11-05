# Ekeko

## Setup

### Create image 

`podman build -t arch-ekeko:latest /path/to/arch-ekeko`

> Note: you can replace podman with docker

#### Running with distrobox

Once this image is create you can then create a distrobox image.

`distrobox create --image arch-ekeko:latest --name arch-ekeko`

which you can then run with

`distrobox enter arch-ekeko`

## Setting Up the Ekeko Project with Jupyter Notebooks

Welcome to the `ekeko` project! This guide will walk you through setting up a Jupyter Notebook environment to ensure that you can run and share notebooks in a consistent environment.

## Prerequisites

1. **Python**: Ensure you have Python installed (ideally Python 3.8 or later).
2. **Poetry**: This project uses Poetry for dependency management. 

## Cloning the Project

1. Clone the project repository:

   ```bash
   git clone https://github.com/yourusername/ekeko.git
   cd ekeko
   ```

2. Install the project dependencies with Poetry:

   ```bash
   poetry install
   ```

   This command will create a virtual environment and install all dependencies specified in the `pyproject.toml` file.

## Setting Up Jupyter Notebook with the Ekeko Kernel

To ensure that Jupyter Notebooks use the correct environment and dependencies, we'll set up a dedicated IPython kernel for the `ekeko` project.

### 1. Add Jupyter as a Development Dependency (if not already added)

   If you haven’t yet added Jupyter as a dependency, run this command to add it:

   ```bash
   poetry add --dev jupyter
   ```

### 2. Install the Ekeko IPython Kernel

   Use the following command to create an IPython kernel named `ekeko`:

   ```bash
   poetry run python -m ipykernel install --user --name=ekeko
   ```

   This command registers the current Poetry environment as a Jupyter kernel named `ekeko`. You should see confirmation that the kernel has been installed.

## Running Jupyter Notebook

1. Start Jupyter Notebook with Poetry:

   ```bash
   poetry run jupyter notebook
   ```

2. When Jupyter Notebook opens, go to **Kernel > Change Kernel** and select `ekeko` from the list of available kernels. This ensures that the notebook runs in the `ekeko` environment with all necessary dependencies.

## Troubleshooting

- **Kernel Not Listed**: If you don’t see `ekeko` in the kernel list, ensure that you followed the steps above exactly, especially the `ipykernel` installation command.
- **Dependency Issues**: If you encounter issues with dependencies, ensure you've run `poetry install` in the project directory.

## Summary of Commands

Here’s a quick summary of the commands you’ll need:

```bash
# Install dependencies
poetry install

# Add Jupyter as a development dependency (if not already added)
poetry add --dev jupyter

# Install the IPython kernel
poetry run python -m ipykernel install --user --name=ekeko

# Run Jupyter Notebook
poetry run jupyter notebook
```
