#!/usr/bin/env sh

# Stop script on error
set -e

REPO_URL=https://github.com/slf-dot-ch/snowmicropyn

case $# in
1)
    TAG=$1
    SYSTEM="TEST"
    ;;
2)
    TAG=$1
    if [ $2 == "LIVE" ]
    then
        SYSTEM="LIVE"
    else
        echo "Second argument not equal LIVE, refusing publishing"
        exit 1
    fi
    ;;
*)
    echo "Usage: `basename "$0"` <tag> [LIVE]";
    echo "Publishing to PyPI live index when string LIVE is provided, otherwise publish to test index";
    exit 1
    ;;
esac

read -p "Publishing release with tag ${TAG} to ${SYSTEM} index on PyPI. Press any key to continue." dummy_var

RELEASE_DIR=RELEASE_${TAG}

CLONE="git clone ${REPO_URL} --branch ${TAG} --single-branch --depth=1 --quiet ${RELEASE_DIR}"
echo "Cloning: ${CLONE}"
`${CLONE}`

cd ${RELEASE_DIR}

GET_HASH="git rev-list -n 1 ${TAG}"
echo "Getting hash: ${GET_HASH}"
HASH=`${GET_HASH}`
echo "Hash is " ${HASH}

HASHFILE=snowmicropyn/githash
echo "Writing hash to file ${HASHFILE}"
echo ${HASH} > ${HASHFILE}

echo "Building source distribution..."
python3 setup.py sdist

echo "Building pure python wheel..."
python3 setup.py bdist_wheel

if [ ${SYSTEM} == "LIVE" ]
then
    echo "Uploading to PyPI index..."
    twine upload dist/*
else
    echo "Uploading to PyPI test index..."
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*
fi

echo "Publishing snowmicropyn ${TAG} to ${SYSTEM} PyPI complete. Have a beer."
