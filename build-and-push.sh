#!/bin/bash
docker build -t gcr.io/ons-hatespeech-detector-2/ons2-be-hs:latest .
gcloud docker -- push gcr.io/ons-hatespeech-detector-2/ons2-be-hs:latest
