FROM ubuntu:20.04 as openfortivpn

ARG OPENFORTIVPN_URL=https://github.com/adrienverge/openfortivpn/archive/refs/tags/v1.17.3.tar.gz
COPY ./patches /patches
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
  wget "$OPENFORTIVPN_URL";                  \
  tar -xzf v1.17.3.tar.gz;                   \
  cd openfortivpn-1.17.3;                    \
  cat /patches/* | patch -p1;                \
  ./autogen.sh;                              \
  ./configure --prefix="";                   \
  make;

FROM ubuntu:20.04

RUN set -ex;                                 \
  apt-get update;                            \
  apt-get install -y --no-install-recommends \
    ca-certificates                          \
    openssl                                  \
    ppp;                                     \
  rm -rf /var/lib/apt/lists/*;               \
  mkdir -p /etc/openfortivpn;                \
  touch /etc/openfortivpn/config;

COPY --from=openfortivpn /openfortivpn-1.17.3/openfortivpn /usr/bin/openfortivpn
ENTRYPOINT ["openfortivpn"]
