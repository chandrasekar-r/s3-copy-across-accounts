# s3-copy-across-accounts
This repository explains how to copy contents from one s3 bucket to other s3 bucket across different accounts.


Note: Add the following policy to the source bucket.
In the below example, I'm copying the contents from sandbox account to pipeline and production accounts. Hence I added two principals.
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCopy",
            "Effect": "Allow",
            "Principal": {
               "AWS": [
                 "arn:aws:iam::xxxxxx0072935:role/admin",
                 "arn:aws:iam::0yyyyyyyyy399:role/admin"
               ]
             },
            "Action": [
                "s3:ListBucket",
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::sample-sandbox/*",
                "arn:aws:s3:::sample-sandbox"
            ]
        }
    ]
}
```


Now create a new IAM policy in the destination account where the file needs to be copied.
Below is the IAM policy for Pipeline/Production Account.
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::*/*",
                "arn:aws:s3:::sample-sandbox"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:ListBucket",
                "s3:PutObjectAcl"
            ],
            "Resource": [
                "arn:aws:s3:::*/*",
                "arn:aws:s3:::sample-pipeline"
            ]
        }
    ]
}
```
