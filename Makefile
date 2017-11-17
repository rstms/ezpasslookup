# makefile
#
PROJECT := ezpasslookup

AWS_REGION := us-east-1

DEPENDENCIES := https://github.com/rstms/python-lambda/archive/v2.2.0-fixed.zip chromedriver selenium

GITURL := https://github.com/adieuadieu/serverless-chrome/raw/master/chrome
TARBALL := chrome-headless-lambda-linux-x64.tar.gz

default: depends headless-chrome

depends:
	pip install $(DEPENDENCIES)

headless-chrome:
	wget $(GITURL)/$(TARBALL) && \
	tar zxfv $(TARBALL) && \
	rm $(TARBALL)
	cp templates/* headless-chrome

clean:
	rm -f *.zip
	rm -f *.pyc
	rm -rf headless-chrome 
	rm -rf dist
	rm -f 

test:	test0 test1 test2 test3

test0:
	python3 ezpasslookup.py bad_violation bad_plate | jq .

test1:
	python3 ezpasslookup.py T021775658460 FEB6625 | jq .

test2:
	python3 ezpasslookup.py T021783673301 T737609C | jq .

test3:
	python3 ezpasslookup.py T021784575788 T720852C | jq .
