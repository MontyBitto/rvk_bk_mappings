default: kxp-subjects.pg some-subjects.pg some-subjects.csv

kxp-subjects.pg: kxp-subjects.tsv.gz
	zcat kxp-subjects.tsv.gz | cargo run tsv2pg-rs --release > kxp-subjects.pg

bk_broader.pg: bk__default.jskos.ndjson
	python3 bk_broader.py bk__default.jskos.ndjson > bk_broader.pg

rvk_broader.pg:
	python3 rvk_broader_xml.py > rvk_broader.pg

rvk_bk.pg:
	python3 rvk_bk_to_pg.py > rvk_bk.pg

some-subjects.pg: rvk_bk_mappings.tsv bk__default.jskos.ndjson kxp-subjects.pg
	python3 bk_broader.py bk__default.jskos.ndjson > some_subjects.pg && \
	python3 rvk_broader_xml.py >> some_subjects.pg && \
	python3 rvk_bk_to_pg.py >> some_subjects.pg && \
	head -n 4000000 kxp-subjects.pg >> some_subjects.pg

some-subjects.csv: some_subjects.pg
	pgraph some_subjects.pg -t csv subjects