set -eux

[ -z "$(git status --porcelain)" ]

if [ -z "${1+x}" ]
then
  set +x
  exit 1
fi

export TAG="v${1}"

git tag "${TAG}"
git push origin master "${TAG}"
rm -rf ./build ./dist
python -m build --sdist --wheel .
twine upload ./dist/*.whl dist/*.tar.gz
