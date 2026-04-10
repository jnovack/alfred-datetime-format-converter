.PHONY: build clean release-local

build: clean
	./scripts/build-workflow.sh

clean:
	rm -rf dist

install:
	open dist/DatetimeFormatConverter.alfredworkflow