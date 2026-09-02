.EXPORT_ALL_VARIABLES:

# The latest Prometheus tag can be found at <https://github.com/prometheus/prometheus/releases>
# choose the latest and avoid pre-releases.
PROM_VERSION = 3.13.2
TAG = 1.0.3

all: lint build clean test

build:
	docker compose build
	docker build --build-arg PROM_VERSION=${PROM_VERSION} -t promtools:${TAG} -t promtools:latest -t ghcr.io/cbdq-io/promtools:latest -t ghcr.io/cbdq-io/promtools:${TAG} .

changelog:
	docker run --quiet --rm --volume "${PWD}:/mnt/source" --workdir /mnt/source ghcr.io/cbdq-io/gitchangelog > CHANGELOG.md

clean:
	docker compose down -t 0 --remove-orphans

lint:
	docker run --rm -i hadolint/hadolint < Dockerfile

tag:
	@echo $(TAG)

test:
	docker compose up -d --wait
