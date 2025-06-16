# Conda
## build new conda env
- `conda create -p ./env python=3.13`

## rebuild the conda env
- First, change to the project path
- `conda env create -p ./env -f environment.yml`

## Using conda command line
- `conda activate ./env`

## Add package
- `conda install [package_name]`
- `conda install -c conda-forge [package_name]`

## Remove the env
- `conda env remove -p ./env -y`

## Backup the env info
- `conda env export -p ./env > environment.yml`
