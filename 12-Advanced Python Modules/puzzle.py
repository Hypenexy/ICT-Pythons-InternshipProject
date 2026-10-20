import zipfile
import os
import re

zip_obj = zipfile.ZipFile("12-Advanced Python Modules/unzip_me_for_instructions.zip", "r")

zip_obj.extractall()

unzipPath = "extracted_content"

dirs = os.listdir(unzipPath)
dirs.remove("Instructions.txt")

pattern = re.compile(r"\d{3}-\d{3}-\d{4}")
for dir in dirs:
    files = os.listdir(f"{unzipPath}/{dir}")

    for file in files:
        for i, line in enumerate(open(f"{unzipPath}/{dir}/{file}")):
            for match in re.finditer(pattern, line):
                print('Found inside folder %s in file %s on line %s: %s' % (dir, file, i+1, match.group()))