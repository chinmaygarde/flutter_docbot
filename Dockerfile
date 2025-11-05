
# First build doxygen2docset as there are no official build rules.
FROM debian:trixie AS doxygen2docset_builder

RUN apt update
RUN apt install -y cmake ninja-build build-essential git
RUN git clone https://github.com/chinmaygarde/doxygen2docset /src
RUN mkdir -p /src/build
WORKDIR /src/build
RUN git submodule update --init --recursive
RUN cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release
RUN ninja


# Then build the documentation using doxygen and package it up via doxygen2docset.
FROM debian:trixie AS documentation_builder

COPY . /src
COPY --from=doxygen2docset_builder /src/build/source/doxygen2docset /usr/local/bin/
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /src
RUN apt update -y
RUN apt install -y doxygen make git
RUN make


# Move the built documentation into the caddy container.
FROM caddy:alpine

COPY --from=documentation_builder /src/build /www
ENTRYPOINT ["caddy", "file-server", "--browse", "--root", "/www"]
