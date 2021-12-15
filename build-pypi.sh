#!/bin/bash

echo "Building pypi package ..."

rm -r dist/*
python.exe setup.py sdist bdist_wheel
python.exe -m twine upload -u apetros -p gY8DDF1VSzKD dist/*

echo "Building pypi package done!"