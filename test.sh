# bash script to test the compile.py program and check the diff between the output files and the expected output files

# The script takes 2 arguments:
# 1. The path to the directory containing the test files
# 2. The path to the directory containing the expected output files

# test all test files in the PA1_testcases directory
# and compare the output with the expected output

#clear the output and diff directories
rm -rif output/*
rm -rif diff/*

# test_directory variable contains the path to the directory containing the test files
test_directory="PA4_testcases"
# iterate through all folders in the test_directory
for folder in $test_directory/*; do
    # if the folder is not a directory, skip it
    if [ ! -d "$folder" ]; then
        continue
    fi
    # get the name of the folder
    folder_name=$(basename "$folder")
    # create a directory to store the output files
    mkdir -p "output/$folder_name"
    # iterate through all files in the folder

    input_directory="$test_directory/$folder_name"

    # if the file is a .jack file, compile it
    python3 compiler.py "$input_directory" "$folder_name"
    echo "Testing $folder_name"
    # compare the output files with the expected output files
    diff -r --ignore-space-change "output/$folder_name" "$input_directory" > "diff/$folder_name.diff"
done