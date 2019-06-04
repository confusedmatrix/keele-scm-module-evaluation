jupyter:
	docker-compose run -p 8888:8888 app start.sh jupyter lab

web.install:
	# docker build --rm -f Dockerfile.web -t module-evaluation/web . && docker run -it --rm -v $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))):/app module-evaluation/web yarn
	docker-compose build web

web.develop:
	# docker run -it --rm -p 1234:1234 -p 8080:8080 -v $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))):/app module-evaluation/web yarn develop
	docker compose up

web.build:
	# docker run -it --rm -v $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))):/app module-evaluation/web yarn build && make web.copy
	docker compose run web yarn build && make web.copy

web.copy:
	rm -rf python/src/static/* && cp -R web/dist/* python/src/static

run:
	docker-compose up nginx