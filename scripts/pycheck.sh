#! /bin/bash
ret=0
for f in $(find . -name "*.py"); do
	echo -n "$f "
	wc -l < $f
	pep8 -r $f || ret=1
	pyflakes $f || ret=1
done
exit $ret
