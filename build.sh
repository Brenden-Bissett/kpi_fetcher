#!/bin/env bash

# Produces a zip `deployment.zip` which can be uploaded to aws lambda.

pip install --target package -r requirements.txt
cd package
zip ../deployment.zip .
cd ..
zip -g deployment.zip main.py
