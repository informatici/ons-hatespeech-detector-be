#!/bin/bash
docker run --rm -p 5000:5000 -e SECRET_KEY=pippo -e DEFAULT_USER=pluto -e DEFAULT_PASSWORD=paperino -e SIGNUP_ENABLED=false  gcr.io/ons-hatespeech-detector-2/ons2-be-hs:latest
