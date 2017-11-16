# makefile
#
PROJECT := ezpaylookup

AWS_REGION := us-east-1

default: build

GITURL := https://github.com/adieuadieu/serverless-chrome/raw/master/chrome
TARBALL := chrome-headless-lambda-linux-x64.tar.gz

headless-chrome:
	wget $(GITURL)/$(TARBALL) && \
	tar zxfv $(TARBALL) && \
	rm $(TARBALL)
	cp run headless-chrome

clean:
	rm -f *.zip
	rm -f *.pyc
	rm -rf headless-chrome 
	rm -rf dist
	rm -f 

test:	test0 test1 test2 test3

test0:
	python3 ezpaylookup.py bad_violation bad_plate | jq .

test1:
	python3 ezpaylookup.py T021775658460 FEB6625 | jq .

test2:
	python3 ezpaylookup.py T021783673301 T737609C | jq .

test3:
	python3 ezpaylookup.py T021784575788 T720852C | jq .

build: headless-chrome
	lambda build

deploy: build
	lambda deploy_s3
