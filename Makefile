build:
	docker build --rm -t jupyter/module-evaluation-datascience-notebook .

run:
	docker run -it --rm -p 8888:8888 -v $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))):/home/jovyan jupyter/module-evaluation-datascience-notebook start.sh jupyter lab

generate:
	docker run -it --rm -v $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))):/home/jovyan jupyter/module-evaluation-datascience-notebook ./analysis/main.py