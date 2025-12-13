# Build in one container and copy over the built artifacts to the Caddy container.
FROM debian:trixie AS doc_builder

RUN apt update
RUN apt install -y cmake ninja-build build-essential git just curl zip unzip tar pkg-config doxygen make git
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install doxygen2docset
RUN git clone https://github.com/chinmaygarde/doxygen2docset /src
ENV VCPKG_ROOT="/src/vcpkg"
RUN git clone https://github.com/microsoft/vcpkg.git ${VCPKG_ROOT}
RUN ${VCPKG_ROOT}/bootstrap-vcpkg.sh
WORKDIR /src
RUN git checkout 5f26f78989d5f5b43bb13fac6ab84b89b88734bc
RUN just sync
RUN just install

# Generate documentation.
COPY . /flutter_docbot
WORKDIR /flutter_docbot
RUN just

# Move the built documentation into the Caddy container.
FROM caddy:alpine
COPY --from=doc_builder /flutter_docbot/build /www
ENTRYPOINT ["caddy", "file-server", "--browse", "--root", "/www"]
