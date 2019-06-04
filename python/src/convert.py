import os
import re

DATA_DIR = "data"

root_dir = "{0}/raw/modules/".format(DATA_DIR)
for file in os.listdir(root_dir):
    if file.endswith(".csv"):
        module = re.sub(r"([A-Z]{3}-[0-9]{5}).*", r"\1", file)

        new_dir = "{0}/{1}".format(root_dir, module)
        try:
            os.mkdir(new_dir)
        except FileExistsError:
            pass

        os.rename("{0}/{1}".format(root_dir, file), "{0}/grades.csv".format(new_dir))