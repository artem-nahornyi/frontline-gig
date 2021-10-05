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
provider:
  ...
  profile: personal
  ...

...

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

| Name | Description |
|------|-------------|
| profile | Frontline GIG AWS profile name from ~/.aws/credentials |
| DAILY_LOOKBACK_DAYS | Number of lookback days to be processed every run. If DB was temporary not responsive given the lookback days, next N daily runs will catch up oin the missed service requests (redundancy) |
| SOCRATA_API_TOKEN | Socrata API Token. Create by following the [link](https://data.norfolk.gov/login) |
| DB_ENGINE_STRING | DB type intentified, won't change as far as DB is Postgresql |
| DB_ENDPOINT | Public DB address, taken from terraform_aws_rds deployment output |
| DB_PORT | DB port, taken from terraform_aws_rds configuration |
| DB_NAME | DB name, taken from terraform_aws_rds configuration |
| DB_USER | DB user, taken from terraform_aws_rds configuration |
| DB_PWD | DB password, taken from terraform_aws_rds configuration |

### 2. Run

```bash
$ cd serverless_service_pipeline
$ sls deploy
```


# Backfilling Past Data

1. Go to https://console.aws.amazon.com/console/
2. Login using Frontline GIG credentials
3. Open Lambda Service (type "Lambda" in the search bar and click on the Lamda service)
4. Go to "Functions"
5. Open "sls-socrata-norfolk-integration-dev-invoker"
6. Select "Test" Tab
7. Create Test Event
7.1 Give it name
7.2 Create json payload in the code section. Payload example:
```json
{"backfill":true, "start_date":"2021-01-01", "end_date":"2021-06-01"}
```
7.3 Click "Test" Button

| Name | Description |
|------|-------------|
| backfill | BOOL, indicates whether you want to trigger backfill, true if yes |
| start_date | String of yyyy-mm-dd format, start date for backfill, inclusive |
| end_date | String of yyyy-mm-dd format, end date for backfill, inclusive | 

> Note: This instruction assumes that the pipeline was already deployed to AWS
-----
> Note: If you can not find the lambda function from 5., make sure you secelted the right region (upper right corner). Region in AWS console must match the region from serverless.yml configuration file

