.PHONY: build
build:
	docker build -t greek .

.PHONY: run-main
CMD=docker run -it --rm -v ${PWD}:/src greek python -m streamlit run
run-main: build
	${CMD} Hello.py
