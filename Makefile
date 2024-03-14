USERNAME=wtfox
IMAGE_NAME=downloader
VERSION=latest
BUILDER_NAME=mybuilder

setup-builder:
	@if ! docker buildx ls | grep -q $(BUILDER_NAME) ; then \
		docker buildx create --name $(BUILDER_NAME) --use; \
	fi

build: setup-builder
	docker buildx build --platform linux/amd64,linux/arm64 --builder $(BUILDER_NAME) -t $(USERNAME)/$(IMAGE_NAME):$(VERSION) .

publish: build
	docker buildx build --platform linux/amd64,linux/arm64 --builder $(BUILDER_NAME) -t $(USERNAME)/$(IMAGE_NAME):$(VERSION) --push .

.PHONY: build publish setup-builder
