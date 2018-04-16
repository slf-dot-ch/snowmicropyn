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
        echo "Second Argument not equal LIVE, refusing publishing"
        exit 1
    fi
    ;;
*)
    echo "Usage: `basename "$0"` <tag> [LIVE]";
    echo "Publishing to PyPI live index when String LIVE is provided, otherwise publish to test index";
    exit 1
    ;;
esac

read -p "Publishing release with tag ${TAG} to ${SYSTEM} index on PyPI. Press enter to continue"

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
if [ ${SYSTEM} == "LIVE" ]
then
    twine upload dist/*
else
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*
fi

echo "Publishing snowmicropyn ${TAG} to ${SYSTEM} PyPI complete. Have a beer."
