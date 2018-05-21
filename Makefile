install: assets.install web.install

assets.install:
	docker build --rm -t jupyter/module-evaluation-datascience-notebook .

assets.fiddle:
	docker run -it --rm -p 8888:8888 -v $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))):/home/jovyan jupyter/module-evaluation-datascience-notebook start.sh jupyter lab

assets.generate:
	docker run -it --rm -v $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))):/home/jovyan jupyter/module-evaluation-datascience-notebook ./analysis/main.py

web.install:
	echo 'TBD'

web.build.dev:
	cd web && yarn start
