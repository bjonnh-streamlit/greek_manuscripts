
# Usage
````shell
docker build -t greek .
docker run -v $PWD:/src:ro -v $PWD/out:/out -it greek python /src/main.py "/src/data/file.doc" /out
````
