# make                     nasa_run: the brain on windows of NASA telemetry (TARGET=linux-x86_64 or linux-aarch64 on Linux)
TARGET ?= macos-arm64
nasa_run: nasa_run.c
	cc -std=c11 -O2 -Wall -Wextra -I../brain/include nasa_run.c ../brain/lib/$(TARGET)/libaa.a -o nasa_run
