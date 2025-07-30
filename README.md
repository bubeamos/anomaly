## anomaly

#### Steps To Setup 

- Configure aws cli - `aws configure --profile`
- update app as needed
- build image `docker build -t anomaly .`
- Run image locally - `docker run -itd -p 8080:8080 anomaly`
- Veriy app works by visiting localhost:8080

- Push image to AWS ECR
```
$ docker  tag anomaly AWS_ACOUNT_ID.dkr.ecr.eu-north-1.amazonaws.com/anomaly:latest

$ docker push AWS_ACOUNT_ID.dkr.ecr.eu-north-1.amazonaws.com/anomaly:latest
```

- Provision all other AWS Services Needed. Services used are; 

    - ECR
    - ECS Fargate
    - EC2 LoadBalanacer 
    - CloudWatch Logging 
    - Cloudwatch Custom Metrics and Anomaly Detection
    - SNS
    - Lambda 