ROOT_DIR	:= $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
GITHASH 	:= $(shell git rev-parse --short HEAD)


.PHONY:all
all:
	@echo 'Available make targets:'
	@grep '^[^#[:space:]\.PHONY.*].*:' Makefile

.PHONY: build-no-cache
build-no-cache:
	docker build . -t travel_dog:latest --no-cache

.PHONY: build
build:
	echo "\n $(shell python3 -c 'import uuid; print(uuid.uuid4().hex)')" >> CHANGELOG.md
	docker build  . -t travel_dog:latest

.PHONY: tag
tag:
	docker tag travel_dog:latest $(shell aws sts get-caller-identity | jq .Account -r).dkr.ecr.us-west-2.amazonaws.com/travel_dog_sample:latest

.PHONY: push
push:
	aws ecr get-login-password | docker login --username AWS --password-stdin $(shell aws sts get-caller-identity | jq .Account -r).dkr.ecr.us-west-2.amazonaws.com
	docker push $(shell aws sts get-caller-identity | jq .Account -r).dkr.ecr.us-west-2.amazonaws.com/travel_dog_sample:latest

.PHONY: create-ecr 
create-ecr:
	aws ecr create-repository --repository-name travel_dog_sample

.PHONY: grant-ecr
grant-ecr:
	aws ecr set-repository-policy \
    --repository-name travel_dog_sample \
    --policy-text file://repository-policy.json


.PHONY: update-deps
update-deps:
	touch poetry.lock
	rm poetry.lock
	docker run -ti -v `pwd`:/app travel_dog /bin/bash -c 'cd ../ && poetry update --lock'
	docker build . --target stage2 -t travel_dog:latest

.PHONY: clean
clean:
	rm -rf travel_dog/__pycache__/
	rm docker/dynamodb/shared-local-instance.db
	docker-compose rm -f
 
.PHONY: run
run:
	DD_API_KEY=$(shell aws ssm get-parameter --name=/datadog/reinvent2022/dd_api_key --with-decryption | jq .Parameter.Value -r -c) docker-compose up

.PHONY: run-no-dd
run-no-dd:
	docker-compose -f docker-compose.no-appsec.yml up -d 

.PHONY: run-live-aws
run-live-aws:
	docker-compose -f docker-compose.no-appsec-aws.yml up -d 

.PHONY: shell
shell:
	docker-compose exec app-node /bin/bash

.PHONY: fmt
fmt:
	black travel_dog/*
	black tests/*

.PHONY: stop
stop:
	docker-compose stop 