FROM ubuntu:26.04

RUN set -ex;                                 \
  apt-get update;                            \
  apt-get install -y --no-install-recommends \
    ca-certificates                          \
    gnutls-bin                               \
    openfortivpn                             \
    openssl                                  \
    pid1                                     \
    ppp;                                     \
  rm -rf /var/lib/apt/lists/*;

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "pid1", "/entrypoint.sh" ]
