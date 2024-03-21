DOCKER_RUN=docker run -it -v $(PWD)/../html_templates:/template greek_manuscripts_tailwind_generator
.PHONY: build
build:
	docker build -t greek_manuscripts_tailwind_generator .
	$(DOCKER_RUN) tailwindcss -i input.css -o output.css --minify

.PHONY: shell
shell:
	$(DOCKER_RUN) /bin/bash

.PHONY: watcher
watcher:
	$(DOCKER_RUN) tailwindcss -i input.css -o output.css --watch
