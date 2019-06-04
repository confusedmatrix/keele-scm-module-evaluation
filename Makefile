# Runs a jupter lab server
jupyter:
	docker-compose run -p 8888:8888 app start.sh jupyter lab

# Runs the flask application (proxied via NGINX) on localhost:80
run:
	docker-compose up nginx

# Installs the node_modules for the web container
web.install:
	docker-compose build web

# Launches develop server for web container
web.develop:
	docker-compose up web

# Runs build script for frontend asserts
web.build:
	docker-compose run web yarn build && make web.copy

# Copies the frontend assets to static dir in python container
web.copy:
	rm -rf python/src/static/* && cp -R web/dist/* python/src/static

