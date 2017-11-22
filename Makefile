# makefile
#
PROJECT := ezpasslookup

AWS_REGION := us-east-1

DEPENDENCIES := https://github.com/rstms/python-lambda/archive/v2.2.0-fixed.zip chromedriver selenium

GITURL := https://github.com/rstms/serverless-chrome/raw/master/chrome
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
	rm -f *.json
	rm -f 

test:	test0 test1 test2 test3

test0:
	python3 ezpasslookup.py bad_violation bad_plate | jq .

test1:
	python3 ezpasslookup.py T021775658460 FEB6625

test2:
	python3 ezpasslookup.py T021783673301 T737609C

test3:
	python3 ezpasslookup.py T021784575788 T720852C | jq .

test4:
	python3 ezpasslookup.py T217069659280 T737701C | jq .

test5:
	python3 ezpasslookup.py T021785619113 T720852C | jq .

testfile:
	cut -d- -f1 <testcases | sort | uniq | awk '{print $$1,$$2; system("python3 ezpasslookup.py " $$2 " " $$1 "|jq . > results-" $$1 "-" $$2 ".json");}'
