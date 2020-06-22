#!/bin/bash

for file in *.txt
do
    echo "$file"
    docker run -v /Users/xinruyan/Developer/Mattress/AspectHierarchy/feng-hirst-rst-parser/preprocessed_texts:/xinru -ti feng-hirst "/xinru/$file" > "../results/$file.parse"
done
