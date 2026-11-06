.PHONY: build test benchmark benchmark-source

build:
	dune build --ignore-promoted-rules -j 2 @install

test:
	dune runtest --ignore-promoted-rules -j 2

benchmark:
	python3 -B benchmarks/run.py --output results/semantic-$$(date -u +%Y%m%dT%H%M%SZ)

benchmark-source:
	python3 -B tools/eunoia-runtime-profile/profile.py --output /tmp/eunoia-source-$$(date -u +%Y%m%dT%H%M%SZ)

.PHONY: benchmark-helpers
benchmark-helpers:
	python3 -B benchmarks/helper_cache.py --output /tmp/eunoia-helpers-$$(date -u +%Y%m%dT%H%M%SZ)
