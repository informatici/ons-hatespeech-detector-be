#!/bin/bash
TAG=dev-be-`TZ=UTC date +%Y%m%d%H%M`
#git add .
#git commit -m "TAG: $TAG"
#git push
git tag $TAG
git push origin $TAG