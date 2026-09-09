CC ?= gcc
CFLAGS ?= -O3 -Wall
LDFLAGS ?= -lm

all: donut cava_bars

donut: donut.c
	$(CC) $(CFLAGS) $< $(LDFLAGS) -o $@

cava_bars: cava_bars.c
	$(CC) $(CFLAGS) $< $(LDFLAGS) -o $@

clean:
	rm -f donut cava_bars

.PHONY: all clean
