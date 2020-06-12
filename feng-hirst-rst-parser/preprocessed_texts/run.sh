#!/bin/bash

for file in *.txt
do
    echo "$file"
    docker run -v /path_to_parser/preprocessed_texts:/name -ti feng-hirst "/name/$file" > "../results2/$file.parse"
done
