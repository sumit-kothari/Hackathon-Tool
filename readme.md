# Hackathon Tool

---

# Basic Overview

This tool can be used to host Hackathons, following are few features supported:

- **Sign In / Sign Up**: Very basic functionality, should add proper authentication 
- **User Profile**
- **Teams** for competitions
- **Competition Overview**
- **Competition Details**
- **Rules page**

#### [Screenshot][1]

---

# Installation

### Pre-request

- Python 3.x
- Framework: Flask
- Database: DynamoDB
- Storage: S3

*Note: This webtool needs AWS services, hence dependency on AWS*


### Run Tool

- `pip install -r requirements.txt`
- Update AWS keys and path in `database.py` & `constants.py`
- `python app.py`


[1]: [https://github.com/sumit-kothari/Hackathon-Tool/tree/master/screenshots]