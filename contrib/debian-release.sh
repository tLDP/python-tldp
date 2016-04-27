#! /bin/bash
#
#

set -e
set -x
set -o pipefail

PACKAGE=$(dpkg-parsechangelog | awk '/Source:/{print $2}')
VERSION=$(dpkg-parsechangelog | awk -F'[- ]' '/Version:/{print $2}')

PREFIX="${PACKAGE}-${VERSION}"
TARBALL="../${PACKAGE}_${VERSION}.orig.tar.xz"

git archive \
  --format tar \
  --prefix "${PREFIX}/" \
  "${PREFIX}" \
  | xz \
    --compress \
    --to-stdout \
  > "${TARBALL}"

exec debuild "$@"

# -- end of file
