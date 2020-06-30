#!/bin/bash
# Note: Update the project directory path in the following docker run command.
for file in *.txt
do
    echo "$file"
    docker run -v /Users/xinruyan/Developer/Mattress/AspectHierarchy/feng-hirst-rst-parser/preprocessed_texts:/xinru -ti feng-hirst "/xinru/$file" > "../results/$file.parse"
done
