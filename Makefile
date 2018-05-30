install: analysis.install web.install

analysis.install:
	docker build --rm -f Dockerfile.analysis -t module-evaluation/analysis .

analysis.develop:
	docker run -it --rm -p 8888:8888 -v $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))):/home/jovyan module-evaluation/analysis start.sh jupyter lab

analysis.run:
	docker run -it --rm -v $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))):/home/jovyan module-evaluation/analysis ./analysis/main.py

web.install:
	docker build --rm -f Dockerfile.web -t module-evaluation/web . && docker run -it --rm -v $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))):/app module-evaluation/web yarn

web.develop:
	docker run -it --rm -p 1234:1234 -p 8080:8080 -v $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))):/app module-evaluation/web yarn develop

web.build:
	docker run -it --rm -v $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))):/app module-evaluation/web yarn build

web.serve:
	docker run -it --rm -p 80:80 -v $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))):/app module-evaluation/web yarn serve
