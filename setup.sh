#!/bin/bash

rm package-lock.json
npm install -g npm@7.0.9
npm install
npm install --global lite-server
npm audit fix --force

