import shutil
import sys

source_directory = sys.argv[1]
destination_directory = sys.argv[2]

shutil.copytree(source_directory, destination_directory)