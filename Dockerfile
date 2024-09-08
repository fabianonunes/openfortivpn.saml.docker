FROM ubuntu:22.04 AS openfortivpn

ARG VERSION=1.21.0
ARG URL=https://github.com/adrienverge/openfortivpn/archive/refs/tags

RUN set -ex;                                 \
  apt-get update;                            \
  apt-get install -y --no-install-recommends \
    autoconf                                 \
    automake                                 \
    ca-certificates                          \
    gcc                                      \
    libc6-dev                                \
    libssl-dev                               \
    make                                     \
    patch                                    \
    pkg-config                               \
    wget;                                    \
  mkdir openfortivpn;                        \
  cd openfortivpn;                           \
  wget "$URL/v$VERSION.tar.gz";              \
  tar -xzf "v$VERSION.tar.gz"                \
     --strip-components 1;                   \
  ./autogen.sh;                              \
  ./configure --prefix="";                   \
  make;

FROM ubuntu:22.04

RUN set -ex;                                 \
  apt-get update;                            \
  apt-get install -y --no-install-recommends \
    ca-certificates                          \
    openssl                                  \
    ppp;                                     \
  rm -rf /var/lib/apt/lists/*;               \
  mkdir -p /etc/openfortivpn;                \
  touch /etc/openfortivpn/config;

COPY --from=openfortivpn "/openfortivpn/openfortivpn" /usr/bin/openfortivpn
ENTRYPOINT ["openfortivpn"]
