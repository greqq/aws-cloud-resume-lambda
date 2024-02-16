# Cloud Resume Challenge - Visitor Counter Lambda Function

## Overview

This AWS Lambda function, part of the [Cloud Resume Challenge](https://cloudresumechallenge.dev/docs/the-challenge/aws/), is implemented in Python and designed to count and track the number of unique visitors.

## Functionality

The function performs the following operations:

- **IP Hashing:** Hashes the IP address of each visitor using SHA-256 to ensure privacy and uniqueness.
- **Visitor Verification:** Checks if the visitor is unique within a 24-hour timeframe by querying the `UniqueVisitors` DynamoDB table with the hashed IP.
- **Counter Update:** Increments the visitor count in the `VisitorCounter` DynamoDB table if the visitor is unique within the specified timeframe.
- **Count Retrieval:** Returns the current unique visitor count.

Additionally, the function employs environment variables to manage resource names and operational modes, ensuring flexibility across different deployment environments.

## Related Repository

The frontend component of the Cloud Resume Challenge, which this Lambda function supports, can be found here: [Cloud Resume Frontend Repo](https://github.com/greqq/cloud-resume).
