#!/bin/bash
# Note: Update the project directory path in the following docker run command.
for file in *.txt
do
    echo "$file"
    docker run -v PROJECT_ABSOLUTE_PATH/AspectHierarchy/feng-hirst-rst-parser/preprocessed_texts:/RANDOM_DIR_NAME -ti feng-hirst "/RANDOM_DIR_NAME/$file" > "../results/$file.parse"
done
