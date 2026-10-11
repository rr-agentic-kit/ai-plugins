#!/usr/bin/env bash
# Build marketplace zip, tag v{version}, and create a GitHub Release with the zip asset.
# Usage: ci_publish_github_release.sh <version> <publish_ref> <gh_release_target>
set -euo pipefail

version="${1:?version required}"
publish_ref="${2:?publish_ref required}"
release_target="${3:?gh release --target required}"

tag="v${version}"
zip_glob="dist/ai-plugins-*.zip"

if git rev-parse -q --verify "refs/tags/${tag}" >/dev/null; then
  echo "tag already exists: ${tag}" >&2
  exit 1
fi
if gh release view "${tag}" >/dev/null 2>&1; then
  echo "GitHub release already exists: ${tag}" >&2
  exit 1
fi

git pull --ff-only origin "${publish_ref}"

uv run python scripts/build_marketplace_zip.py --version "${version}"
mapfile -t zips < <(compgen -G "${zip_glob}" || true)
if [[ ${#zips[@]} -ne 1 ]]; then
  echo "expected exactly one ${zip_glob}, found: ${zips[*]:-none}" >&2
  exit 1
fi
zip_path="${zips[0]}"

prerelease_flag=()
prerelease_line="$(uv run python scripts/build_marketplace_zip.py --version "${version}" --print-prerelease)"
if [[ "${prerelease_line}" == "prerelease=true" ]]; then
  prerelease_flag=(--prerelease)
fi

git tag "${tag}"
git push origin "${tag}"

gh release create "${tag}" "${zip_path}" \
  --generate-notes \
  --target "${release_target}" \
  --title "${version}" \
  "${prerelease_flag[@]}"
