# makefile
#
PROJECT := ezpaylookup

AWS_REGION := us-east-1


$(PROJECT).zip:	$(PROJECT).py
	zip $@ $<

clean:
	rm *.zip

test1:
	python3 ezpaylookup.py T021775658460 FEB6625

test9:
	python3 ezpaylookup.py T021784575788 T720852C

test2:
	python3 ezpaylookup.py T021783673301 T737609C

install:
	aws lambda delete-function --region=$(AWS_REGION) --function-name=$(PROJECT)
