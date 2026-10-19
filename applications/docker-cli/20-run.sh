mkdir -p ~/.docker/cli-plugins
ln -sfn $(which docker-buildx) ~/.docker/cli-plugins/docker-buildx
ln -sfn $(which docker-compose) ~/.docker/cli-plugins/docker-compose
