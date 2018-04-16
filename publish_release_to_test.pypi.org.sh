#!/usr/bin/env sh

# Stop script on error
set -e

REPO_URL=https://github.com/slf-dot-ch/snowmicropyn

if [ $# -eq 1 ]
then
    echo "Publishing release with tag $1..."
else
    echo "Provide git tag to release as argument"
    exit 1
fi

TAG="$1"
RELEASE_DIR=RELEASE_${TAG}

CLONE="git clone ${REPO_URL} --branch ${TAG} --single-branch --depth=1 --quiet ${RELEASE_DIR}"
echo "Cloning... ${CLONE}"
`${CLONE}`

cd ${RELEASE_DIR}
GET_HASH="git rev-list -n 1 ${TAG}"
echo "Getting Hash... ${GET_HASH}"
HASH=`${GET_HASH}`
echo "Hash is " ${HASH}

HASHFILE=snowmicropyn/githash
echo "Writing Hash to File..." ${HASHFILE}
echo ${HASH} > ${HASHFILE}

echo "Building Pure Python Wheel..."
python setup.py bdist_wheel

echo "Uploading to PyPI test index..."
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

echo "Publishing snowmicropyn ${TAG} test.pypi.org complete. Have a beer."
