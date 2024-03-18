.PHONY: build
build:
	docker build -t greek .

.PHONY: run-main
DOCKER_COMMAND=docker run -it --rm -v ${PWD}:/app greek
STREAMLIT_COMMAND=${DOCKER_COMMANT} python -m streamlit run
run-main: build
	${STREAMLIT_COMMAND} Hello.py

.PHONY: shell
shell: build
	${DOCKER_COMMAND} bash -l -c "poetry shell"
