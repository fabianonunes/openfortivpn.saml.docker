FROM ubuntu:22.04 as openconnect

ARG URL=https://gitlab.com/openconnect/openconnect/-/archive/v9.12/openconnect-v9.12.tar.gz

RUN set -ex;                                 \
  apt-get update;                            \
  DEBIAN_FRONTEND=noninteractive             \
  apt-get install -y --no-install-recommends \
    automake                                 \
    ca-certificates                          \
    gcc                                      \
    gettext                                  \
    libssl-dev                          \
    # libgnutls28-dev                          \
    liblz4-dev                               \
    libtool                                  \
    libxml2-dev                              \
    make                                     \
    pkg-config                               \
    vpnc-scripts                             \
    wget                                     \
    zlib1g-dev;                              \
  mkdir openconnect;                         \
  cd openconnect;                            \
  wget -O openconnect.tar.gz "$URL";         \
  tar -xzf "openconnect.tar.gz"              \
     --strip-components 1;                   \
  ./autogen.sh;                              \
  ./configure --prefix="/oc";                \
  make -j $(nproc);                          \
  make install

FROM ubuntu:22.04

RUN set -ex;                                 \
  apt-get update;                            \
  apt-get install -y --no-install-recommends \
    ca-certificates                          \
    vpnc-scripts                             \
    openssl                              \
    # libgnutls30                              \
    libxml2;                                 \
  rm -rf /var/lib/apt/lists/*;

COPY --from=openconnect "/oc" /oc
# COPY --from=openconnect "/openconnect/.libs" /usr/bin/.libs
ENTRYPOINT ["/oc/sbin/openconnect"]
