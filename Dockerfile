# Build in one container and copy over the built artifacts to the Caddy container.
FROM debian:trixie AS doc_builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt update
RUN apt install -y just wget git doxygen

# Install doxygen2docset
RUN mkdir -p /src/doxygen2docset
WORKDIR /src/doxygen2docset
RUN wget https://github.com/chinmaygarde/doxygen2docset/releases/download/v0.2.2/doxygen2docset-linux-$(uname -m).tar.gz
RUN tar -xzvf doxygen2docset-linux-$(uname -m).tar.gz
RUN cp /src/doxygen2docset/bin/doxygen2docset /usr/local/bin

# Generate documentation.
COPY . /flutter_docbot
WORKDIR /flutter_docbot
RUN just

# Move the built documentation into the Caddy container.
FROM caddy:alpine
COPY --from=doc_builder /flutter_docbot/build /www
ENTRYPOINT ["caddy", "file-server", "--browse", "--root", "/www"]
