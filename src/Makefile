BENCH_ABBREV := hello

KERNEL_TAR := linux-4.2.3.tar.xz

$(KERNEL_TAR):
	wget https://www.kernel.org/pub/linux/kernel/v4.x/$(KERNEL_TAR)

bench-data: $(KERNEL_TAR)
	tar tf $^ > $@

ALL_RESULTS := py-simple py-re2 lua luajit
ALL_RESULT_TARGETS := $(addprefix bench-results-, $(ALL_RESULTS))
ABBREV := $(shell cat bench-abbrev)

COMMAND-bench-results-py-simple := python2 abbrev_matcher_main.py --method simple
COMMAND-bench-results-py-re2 := python2 abbrev_matcher_main.py --method re2
COMMAND-bench-results-lua := lua abbrev_matcher_main.lua
COMMAND-bench-results-luajit := luajit abbrev_matcher_main.lua

bench-results-py-simple bench-results-py-re2: abbrev_matcher.py

bench-results-lua bench-results-luajit: abbrev_matcher.lua

TIMED_COMMAND = for i in {1..20}; do cat $< | $(COMMAND-$@) $(ABBREV) > /dev/null ; done
TIME_COMMAND = /usr/bin/time --format=%U --output=$@ sh -c '$(TIMED_COMMAND)'

$(ALL_RESULT_TARGETS): bench-data bench-abbrev
	$(TIME_COMMAND)
	cat $@

bench-results-all: $(ALL_RESULT_TARGETS)
	tail -n +1 -- $^ > $@
	echo ========================
	cat $@


