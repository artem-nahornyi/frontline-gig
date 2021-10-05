# Project Description

Configuration in this directory creates a set of RDS resources including Public DB instance, DB subnet group and DB parameter group.

## Prerequisites

### 1. [Install aws-cli](https://learn.hashicorp.com/tutorials/terraform/install-cli)

#### Windows

Run the following command in CMD. The latest version of the AWS will be downloaded and installed

```cmd
$ C:\> msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```

#### Mac

Run the following command in CMD. The latest version of the AWS will be downloaded and installed 
```bash
$ curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
$ sudo installer -pkg AWSCLIV2.pkg -target /
```

#### Linux

```bash
$ curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
$ unzip awscliv2.zip
$ sudo ./aws/install
```

#### Verify aws-cli is successfully installed

```
$ aws --version
```

### 2. [Configuration and credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)

Run **aws configure --profile frontline_gig** in terminal. You will be propted to enter AWS Access Key ID, AWS Secret Access Key, Default region name and default input format. Enter as following (with replacing credentials to actual ones)

```bash
$ aws configure --profile frontline_gig
AWS Access Key ID [None]: AKIAI44QH8DHBEXAMPLE
AWS Secret Access Key [None]: je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: text
```
> Note: --profile frontline_gig will create a named profile "frontline_gig" on your computer with credentials tied to it. You will need to use this profile to provision aws infrastructure or deploy services to AWS.

### 3. [Install Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli)

#### Windowns

```cmd
$ choco install terraform
```

#### Mac

```bash
$ brew tap hashicorp/tap
$ brew install hashicorp/tap/terraform
$ brew update
$ brew upgrade hashicorp/tap/terraform
```

#### Linux

```bash
$ sudo apt-get update && sudo apt-get install -y gnupg software-properties-common curl
$ curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
$ sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
$ sudo apt-get update && sudo apt-get install terraform
```

#### Verify terraform is successfully installed

```
$ terraform -help
```

# Usage

## 1. Edit the configuration

Main configurable parameters are isolated at the top of main.tf file
```
locals {
  name                     = "frontline-postgresql"
  region                   = "us-east-1"
  profile                  = "personal" 
  db_name                  = "db01" 
  db_username              = "frontlinegig" 
  db_password              = "YourPwdShouldBeLongAndSecure!" 
  db_instance_class        = "db.t3.micro" 
  db_allocated_storage     = 20
  db_max_allocated_storage = 100


  tags = {
    Owner       = "user"
    Environment = "dev"
  }
}
```

> Note: Do not push your configuration with credentials back to github after editing

## 2. Run:

```bash
$ terraform init
$ terraform plan
$ terraform apply
```

> Note that this example may create resources which cost money. Run `terraform destroy` when you don't need these resources.


## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.12.26 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 2.49 |


## Outputs

| Name | Description |
|------|-------------|
| <a name="output_db_default_instance_address"></a> [db\_default\_instance\_address](#output\_db\_default\_instance\_address) | The address of the RDS instance |
| <a name="output_db_default_instance_arn"></a> [db\_default\_instance\_arn](#output\_db\_default\_instance\_arn) | The ARN of the RDS instance |
| <a name="output_db_default_instance_availability_zone"></a> [db\_default\_instance\_availability\_zone](#output\_db\_default\_instance\_availability\_zone) | The availability zone of the RDS instance |
| <a name="output_db_default_instance_endpoint"></a> [db\_default\_instance\_endpoint](#output\_db\_default\_instance\_endpoint) | The connection endpoint |
| <a name="output_db_default_instance_hosted_zone_id"></a> [db\_default\_instance\_hosted\_zone\_id](#output\_db\_default\_instance\_hosted\_zone\_id) | The canonical hosted zone ID of the DB instance (to be used in a Route 53 Alias record) |
| <a name="output_db_default_instance_id"></a> [db\_default\_instance\_id](#output\_db\_default\_instance\_id) | The RDS instance ID |
| <a name="output_db_default_instance_name"></a> [db\_default\_instance\_name](#output\_db\_default\_instance\_name) | The database name |
| <a name="output_db_default_instance_password"></a> [db\_default\_instance\_password](#output\_db\_default\_instance\_password) | The database password (this password may be old, because Terraform doesn't track it after initial creation) |
| <a name="output_db_default_instance_port"></a> [db\_default\_instance\_port](#output\_db\_default\_instance\_port) | The database port |
| <a name="output_db_default_instance_resource_id"></a> [db\_default\_instance\_resource\_id](#output\_db\_default\_instance\_resource\_id) | The RDS Resource ID of this instance |
| <a name="output_db_default_instance_status"></a> [db\_default\_instance\_status](#output\_db\_default\_instance\_status) | The RDS instance status |
| <a name="output_db_default_instance_username"></a> [db\_default\_instance\_username](#output\_db\_default\_instance\_username) | The master username for the database |
| <a name="output_db_default_parameter_group_arn"></a> [db\_default\_parameter\_group\_arn](#output\_db\_default\_parameter\_group\_arn) | The ARN of the db parameter group |
| <a name="output_db_default_parameter_group_id"></a> [db\_default\_parameter\_group\_id](#output\_db\_default\_parameter\_group\_id) | The db parameter group id |
| <a name="output_db_default_subnet_group_arn"></a> [db\_default\_subnet\_group\_arn](#output\_db\_default\_subnet\_group\_arn) | The ARN of the db subnet group |
| <a name="output_db_default_subnet_group_id"></a> [db\_default\_subnet\_group\_id](#output\_db\_default\_subnet\_group\_id) | The db subnet group name |
| <a name="output_db_enhanced_monitoring_iam_role_arn"></a> [db\_enhanced\_monitoring\_iam\_role\_arn](#output\_db\_enhanced\_monitoring\_iam\_role\_arn) | The Amazon Resource Name (ARN) specifying the monitoring role |
| <a name="output_db_instance_address"></a> [db\_instance\_address](#output\_db\_instance\_address) | The address of the RDS instance |
| <a name="output_db_instance_arn"></a> [db\_instance\_arn](#output\_db\_instance\_arn) | The ARN of the RDS instance |
| <a name="output_db_instance_availability_zone"></a> [db\_instance\_availability\_zone](#output\_db\_instance\_availability\_zone) | The availability zone of the RDS instance |
| <a name="output_db_instance_endpoint"></a> [db\_instance\_endpoint](#output\_db\_instance\_endpoint) | The connection endpoint |
| <a name="output_db_instance_hosted_zone_id"></a> [db\_instance\_hosted\_zone\_id](#output\_db\_instance\_hosted\_zone\_id) | The canonical hosted zone ID of the DB instance (to be used in a Route 53 Alias record) |
| <a name="output_db_instance_id"></a> [db\_instance\_id](#output\_db\_instance\_id) | The RDS instance ID |
| <a name="output_db_instance_name"></a> [db\_instance\_name](#output\_db\_instance\_name) | The database name |
| <a name="output_db_instance_password"></a> [db\_instance\_password](#output\_db\_instance\_password) | The database password (this password may be old, because Terraform doesn't track it after initial creation) |
| <a name="output_db_instance_port"></a> [db\_instance\_port](#output\_db\_instance\_port) | The database port |
| <a name="output_db_instance_resource_id"></a> [db\_instance\_resource\_id](#output\_db\_instance\_resource\_id) | The RDS Resource ID of this instance |
| <a name="output_db_instance_status"></a> [db\_instance\_status](#output\_db\_instance\_status) | The RDS instance status |
| <a name="output_db_instance_username"></a> [db\_instance\_username](#output\_db\_instance\_username) | The master username for the database |
| <a name="output_db_parameter_group_arn"></a> [db\_parameter\_group\_arn](#output\_db\_parameter\_group\_arn) | The ARN of the db parameter group |
| <a name="output_db_parameter_group_id"></a> [db\_parameter\_group\_id](#output\_db\_parameter\_group\_id) | The db parameter group id |
| <a name="output_db_subnet_group_arn"></a> [db\_subnet\_group\_arn](#output\_db\_subnet\_group\_arn) | The ARN of the db subnet group |
| <a name="output_db_subnet_group_id"></a> [db\_subnet\_group\_id](#output\_db\_subnet\_group\_id) | The db subnet group name |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
