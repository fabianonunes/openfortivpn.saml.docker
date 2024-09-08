#!/bin/bash
set -uo pipefail

host="${1:?}"

function check_ssl {
  echo | gnutls-cli --ca-auto-retrieve --print-cert "$host" | openssl x509 -outform der | sha256sum | cut -d ' ' -f 1
}

if ! cert_hash=$(check_ssl); then
  unset cert_hash
fi

exec openfortivpn "$@" ${cert_hash:+--trusted-cert "$cert_hash"}
