BENCH_ABBREV := hello

KERNEL_TAR := linux-4.2.3.tar.xz

$(KERNEL_TAR):
	wget https://www.kernel.org/pub/linux/kernel/v4.x/$(KERNEL_TAR)

bench-data: $(KERNEL_TAR)
	tar tf $^ > $@

PYTHON_RESULTS := py-slow py-re2 py-pcre py-re2-rank
PYTHON_RESULT_TARGETS := $(addprefix bench-results-, $(PYTHON_RESULTS))
LUA_RESULTS := lua luajit
LUA_RESULT_TARGETS := $(addprefix bench-results-, $(LUA_RESULTS))
# ALL_RESULTS := $(PYTHON_RESULTS) $(LUA_RESULTS)
ALL_RESULTS := $(PYTHON_RESULTS)
ALL_RESULT_TARGETS := $(PYTHON_RESULT_TARGETS) $(LUA_RESULT_TARGETS) bench-results-perl bench-results-egrep bench-results-ag bench-results-grep-py
PATTERN := $(shell cat bench-pattern)

COMMAND-bench-results-py-slow := python2 abbrev_matcher1.py --no-re $(PATTERN)
COMMAND-bench-results-py-re2 := python2 abbrev_matcher1.py --re-engine re2 $(PATTERN)
COMMAND-bench-results-py-pcre := python2 abbrev_matcher1.py --re-engine pcre $(PATTERN)
COMMAND-bench-results-perl := ./grep.pl `./abbrev_matcher1.py --regex $(PATTERN)`
COMMAND-bench-results-egrep := grep -E -n `./abbrev_matcher1.py --regex $(PATTERN)`
COMMAND-bench-results-grep-py := ./grep_matcher.py `./abbrev_matcher1.py --regex $(PATTERN)`
COMMAND-bench-results-ag := ag --numbers `./abbrev_matcher1.py --regex $(PATTERN)`
COMMAND-bench-results-py-re2-rank := python2 abbrev_matcher1.py --re-engine re2 --rank file $(PATTERN)
COMMAND-bench-results-lua := lua abbrev_matcher_main.lua $(PATTERN)
COMMAND-bench-results-luajit := luajit abbrev_matcher_main.lua $(PATTERN)

$(PYTHON_RESULT_TARGETS): abbrev_matcher1.py

$(LUA_RESULT_TARGETS): abbrev_matcher.lua

TIMED_COMMAND = for i in {1..20}; do cat $< | $(COMMAND-$@) > /dev/null ; done
TIME_COMMAND = /usr/bin/time --format=%U --output=$@ sh -c '$(TIMED_COMMAND)'

$(ALL_RESULT_TARGETS): bench-data bench-pattern
	$(TIME_COMMAND)
	cat $@

bench-results-all: $(ALL_RESULT_TARGETS)
	tail -n +1 -- $^ > $@
	echo ========================
	cat $@


