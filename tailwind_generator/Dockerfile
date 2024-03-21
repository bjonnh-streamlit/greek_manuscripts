FROM ubuntu:latest
RUN apt update && apt install -y curl
RUN useradd -m nonroot
USER nonroot
WORKDIR /home/nonroot
RUN curl -L -o tailwindcss https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.1/tailwindcss-linux-x64
RUN chmod +x tailwindcss
# Use tailwind as the entrypoint
VOLUME /template
WORKDIR /template
ENV PATH="/home/nonroot:${PATH}"
CMD ["/home/nonroot/tailwindcss"]
