#!/bin/bash
echo '#################################################################'
echo Type in the input data path:
read input
echo '#################################################################'
echo 'Type in the brand (case sensitive; All for all brands)':
read brand
echo '#################################################################'
echo 'Type in the product (lowercase)':
read keyword
echo '#################################################################'
echo Building feng-hirst-rst-parser
cd ../feng-hirst-rst-parser/
docker build -t feng-hirst .
echo '#################################################################'
echo Preprocessing reviews.
cd ../src/
python review_preprocess.py -r $input -o ../feng-hirst-rst-parser/preprocessed_texts/
echo '#################################################################'
echo Running feng-hirst-rst-parser. This can take a while.
cd ../feng-hirst-rst-parser/preprocessed_texts/
./runrst.sh
echo '#################################################################'
echo Parsing RST result, create RST graphs and generate aspect pairs.
cd ../../src/
python -m spacy download en_core_web_sm
python treeparser.py -i ../feng-hirst-rst-parser/results -o ../rst_results
echo '#################################################################'
echo Generating and examining primary aspects.
python primary_aspects.py -p ../rst_results/noun_pairs.pickle -na ../data/resources/not_cared_aspects -k $keyword
echo '#################################################################'
echo Type in the selected primary aspects from the above aspect list, one aspect per line. Enter ctrl + D on a new line when finished.
arrAspects=()
while IFS= read -r aspect
do
    arrAspects+=("$aspect")
done
printf "%s\n" "${arrAspects[@]}" >> ../data/resources/primary_aspects
echo '#################################################################'
echo Generating and examining secondary aspects.
python aspect_hierarchy.py -b $brand -p ../feng-hirst-rst-parser/results -d $input -ca ../data/resources/primary_aspects -na ../data/resources/not_cared_aspects -rl ../data/resources/relations -dt ../data/resources/determiners -k $keyword > "../data/brand/$brand.txt"
echo '#################################################################'
echo Creating aspect hierarchy graphs.
python gen_graph.py -b $brand -o ../graphs/
echo '#################################################################'
echo Done
