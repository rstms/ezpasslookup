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
---------------
If the function encounters an error, it should return ERROR No Violations Match or ERROR Unknown
