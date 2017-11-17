# ezpaylookup
EZ-Pay Violation Lookup Lambda Function

Project Specifications

Deliverable
-----------

Deliverable should be a python AWS Lambda app function that goes to https://www.e-zpassny.com/payviolation

INPUT:
------

* Violation Number
* License Plate Number

License State is always NY, License Country is always USA.


OUTPUT:
-------
* JSON array of ALL violations in the violation list table.


Error Handling:
--------------- If the function encounters an error, it should return ERROR No Violations Match or ERROR Unknown


Installation
------------
The project has a Makefile which may be used to build and deploy the function to AWS Lambda.  Due to the size of the binaries,
it requires an S3 bucket with a folder.


AWS Authentication
------------------
The system's ~/.aws/config and ~/.aws/credentials will be used for AWS authentication
The IAM user specified must be authorized to write to the S3 bucket and create the Lambda function


Virtualenv
----------
[virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/#) is highly recommended for the build and deploy environment.  


Configure
---------
Edit the folowing items in config.yaml

 - region: ex: `us-east-1`
 - role: ex: `lambda_execute_role`
 - bucket_name: ex: `ezpasslookup-lambda`
 - s3_key_prefix: ex: `ezpasslookup/`
 - aws_access_key_id: YOUR_AWS_ACCESS_KEY_ID
 - aws_secret_access_key: YOUR_AWS_SECRET_ACCESS_KEY


Build and Deploy
----------------
This command will download the dependencies, build, and deploy the lambda function:
```
make deploy
```
