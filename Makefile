# makefile
#
PROJECT := ezpaylookup

AWS_REGION := us-east-1


$(PROJECT).zip:	$(PROJECT).py
	zip $@ $<

clean:
	rm *.zip

test:	test0 test1 test2 test3

test0:
	python3 ezpaylookup.py bad_violation bad_plate | jq .

test1:
	python3 ezpaylookup.py T021775658460 FEB6625 | jq .

test2:
	python3 ezpaylookup.py T021783673301 T737609C | jq .

test3:
	python3 ezpaylookup.py T021784575788 T720852C | jq .

install:
	aws lambda delete-function --region=$(AWS_REGION) --function-name=$(PROJECT)
