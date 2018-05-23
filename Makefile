install: analysis.install web.install

analysis.install:
	docker build --rm -t jupyter/module-evaluation-datascience-notebook .

analysis.develop:
	docker run -it --rm -p 8888:8888 -v $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))):/home/jovyan jupyter/module-evaluation-datascience-notebook start.sh jupyter lab

analysis.run:
	docker run -it --rm -v $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))):/home/jovyan jupyter/module-evaluation-datascience-notebook ./analysis/main.py

web.install:
	echo 'TBD'

web.develop:
	cd web && yarn start

web.build:
	echo 'TBD'

web.serve:
	echo 'TBD'
