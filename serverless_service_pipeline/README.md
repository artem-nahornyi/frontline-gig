# Project Score


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
      <span style="color:red;">DAILY_LOOKBACK_DAYS: 2</span>
      <span style="color:red;">SOCRATA_API_TOKEN: "GlDpNs6BxylbpumxZ1svqIFGv"</span>
      
  ...

  transcoder:
    handler: src/functions/transcoder.transcode
    environment:
      <span style="color:red;">DB_ENGINE_STRING: "postgresql"</span>
      <span style="color:red;">DB_ENDPOINT:      "frontline-postgresql.cvym3s2dsr13.us-east-1.rds.amazonaws.com"</span>
      <span style="color:red;">DB_PORT:          "5432"</span>
      <span style="color:red;">DB_NAME:          "db01"</span>
      <span style="color:red;">DB_USER:          "frontlinegig"</span>
      <span style="color:red;">DB_PWD:           "YourPwdShouldBeLongAndSecure!"</span>
      
  ...
```

