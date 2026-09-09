CC ?= gcc
CFLAGS ?= -O3 -Wall
LDFLAGS ?= -lm

all: donut

donut: donut.c
	$(CC) $(CFLAGS) $< $(LDFLAGS) -o $@

clean:
	rm -f donut

.PHONY: all clean
