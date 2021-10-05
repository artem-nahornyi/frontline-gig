# Project Description
Configuration in this directory creates pipeline and AWS resources that processes Socrata Norfold service requests, geocodes location addresses and writes results into Frontline GIG Postgresql DB. 


## Prerequisites

### 1. Install Node.js

Follow instructions from the official [website](https://nodejs.org/en/download/)

### 2. Install Serverless Framework

Follow instructions from [Serverless.com](https://www.serverless.com/framework/docs/providers/aws/guide/installation)

## Usage

### 1. Edit the configuration

```sls
functions:
  invoker:
    handler: src/functions/invoker.invoke
    environment:
      DAILY_LOOKBACK_DAYS: 2
      SOCRATA_API_TOKEN: "GlDpNs6BxylbpumxZ1svqIFGv"

  ...

  transcoder:
    handler: src/functions/transcoder.transcode
    environment:
      DB_ENGINE_STRING: "postgresql"
      DB_ENDPOINT:      "frontline-postgresql.cvym3s2dsr13.us-east-1.rds.amazonaws.com"
      DB_PORT:          "5432"
      DB_NAME:          "db01"
      DB_USER:          "frontlinegig"
      DB_PWD:           "YourPwdShouldBeLongAndSecure!"
  ...
```

#### Variables:
DAILY_LOOKBACK_DAYS         Number of lookback days to be processed every day (redundancy)

SOCRATA_API_TOKEN           Socrata API Token. Create by following the [link](https://data.norfolk.gov/login)

DB_ENGINE_STRING            DB type intentified, won't change as far as DB is Postgresql

DB_ENDPOINT                 Public DB address, taken from terraform_aws_rds deployment output

DB_PORT                     DB port, taken from terraform_aws_rds configuration

DB_NAME                     DB name, taken from terraform_aws_rds configuration

DB_USER                     DB user, taken from terraform_aws_rds configuration

DB_PWD                      DB password, taken from terraform_aws_rds configuration

### 2. Run

```bash
$ cd serverless_service_pipeline
$ sls deploy
```
