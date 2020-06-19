#!/bin/bash

# build feng-hirst-rst-parser
cd ../feng-hirst-rst-parser/
docker build -t feng-hirst .
# preprocess reviews
cd ../src/
pipenv run python review_preprocess.py -r ../../Mattress/data/preprocessed/brand_data_new.csv -o ../feng-hirst-rst-parser/preprocessed_texts/
# run feng-hirst-rst-parser, this can take a while
cd ../feng-hirst-rst-parser/preprocessed_txts/
./run.sh
# parse RST result, create RST graphs and generate aspect pairs
cd ../src/
pipenv run python treeparser.py -i ../../Mattress/feng-2/feng-hirst-rst-parser/results2 -o ../rst_results
# generate and examine primary aspects
pipenv run python primary_aspects.py -p ../rst_results/noun_pairs.pickle2 -na ../data/resources/not_cared_aspects -k mattress
# generate and examine secondary aspects
pipenv run python aspect_hierarchy.py -b Serta -p ../feng-2/feng-hirst-rst-parser/results2 -d ../data/preprocessed/brand_data_new.csv -ca ../data/resources/primary_aspects -na ../data/resources/not_cared_aspects -rl ../data/resources/relations -dt ../data/resources/determiners -k mattress
# create aspect hierarchy graphs
pipenv run python gen_graph.py -b Serta -o ../figs/
