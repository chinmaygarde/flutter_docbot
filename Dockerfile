FROM google/cloud-sdk:slim as build

RUN apt update
RUN apt install -y cmake ninja-build build-essential git
RUN git clone https://github.com/chinmaygarde/doxygen2docset /src
RUN mkdir -p /src/build
WORKDIR /src/build
RUN git submodule update --init --recursive
RUN cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release
RUN ninja

FROM google/cloud-sdk:slim

COPY . /src
COPY --from=build /src/build/source/doxygen2docset /usr/local/bin/
RUN apt update
RUN apt install -y doxygen make python3 git
WORKDIR /src

ENTRYPOINT make upload
