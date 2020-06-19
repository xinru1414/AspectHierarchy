# Aspect Hierarchy
Opinion mining on Amazon product reviews [using rhetorical structure theory and graph analysis](https://arxiv.org/abs/1909.01800).

## Installation & Dependencies 
First, install [docker](https://www.docker.com/). Next, install [pipenv](https://pipenv-fork.readthedocs.io/en/latest/install.html).

After cloning the project, run the following command in the root dir `AspectHierarchy` to install all dependencies.
```
$ pipenv install
```
This package uses [feng-hirst-rst-parser](https://github.com/arne-cl/feng-hirst-rst-parser). In the `feng-hirst-rst-parser`  dir, run the following command to build an image from the dockerfile.
```
$ docker build -t feng-hirst .
```
## Usage
[Sys.Arc](https://github.com/xinru1414/AspectHierarchy/blob/master/SysArc.svg) provides an overview of the system architecture.

The system takes a CSV file as an input, including four columns: `Id`, `Text`, `Brand` and `ReviewRating`. Column `Id` represents the review id, Column `Text` represents the product review, Column `Brand` represents the product brand and Column `ReviewRating` represents the rating for the product in range `[0,100]`.

To run the system:

1. Run the following command in `src` dir to prepare data for the RST parser.
```
$ pipenv run python review_preprocess.py
```
2. Run the following command in `feng-hirst-rst-parser/preprocessed_texts` dir to perform RST.
```
$ ./run.sh
```
3. Run the following command in `src` dir to parse RST result, create RST graphs and generate aspect pairs.
```
$ pipenv run python treeparser.py
```
4. Run the following command in `src` dir to generate and examine primary aspects.
```
$ pipenv run python primary_aspects.py
```
5. Run the following command in `src` dir to generate and examine secondary aspects.
```
$ pipenv run python aspect_hierarchy.py
```
6. Run the following command in `src` dir to create aspect hierarchy graphs.
```
$ pipenv run python gen_graph.py
```
All python files allow users to set up command line parameters. Details see each python file, or simply add `--help` at the end of each command.

## Structure
### feng-hirst-rst-parser
Contains code for `feng-hirst-rst-parser`, dir preprocessed_texts and dir results.
### rst_results
Contains RST visualization (graphs) and the gloabally extracted aspect pairs.
### data
Contains preprocessed Amazon Reviews and other resource files used by the system.
### src
Contains src code for the system.
### test
Contains unit tests for the RST tree parser.
### figs
Contains generated aspect hierarchy graphs.
### run.sh
A sample script to run the system.

