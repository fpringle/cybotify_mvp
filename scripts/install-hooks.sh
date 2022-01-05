#!/bin/sh

ROOT_DIR=$(git rev-parse --show-toplevel)
HOOKS_DIR=$ROOT_DIR/.git/hooks
SCRIPTS_DIR=$ROOT_DIR/scripts

mkdir -p $HOOKS_DIR
cp $SCRIPTS_DIR/hooks/* $HOOKS_DIR/
chmod +x $HOOKS_DIR/*

cd $ROOT_DIR
pre-commit install
