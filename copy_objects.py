import boto3

class S3Copier:
    """
    S3Copier

    This class provides functionality to copy all objects from one S3 bucket to another S3 bucket.

    Attributes:
    s3 (boto3.resource): S3 resource.
    source_bucket (boto3.s3.bucket.Bucket): Source S3 bucket.
    destination_bucket (boto3.s3.bucket.Bucket): Destination S3 bucket.

    Methods:
    copy (): Copies all objects from source bucket to destination bucket.

    """
    def __init__(self, session, source_bucket_name, destination_bucket_name):
        self.s3 = session.resource("s3")
        self.source_bucket = self.s3.Bucket(source_bucket_name)
        self.destination_bucket = self.s3.Bucket(destination_bucket_name)

    def copy(self):
        counter = 1
        total_objects = sum(1 for _ in self.source_bucket.objects.all())
        for obj in self.source_bucket.objects.all():
            obj_key = obj.key
            self.s3.meta.client.copy_object(Bucket=self.destination_bucket.name, CopySource={"Bucket": self.source_bucket.name, "Key": obj_key}, Key=obj_key)
            print(f"{counter}/{total_objects} objects copied")
            counter += 1

def main():
    """
    main

    The main function creates two S3Copier objects and calls their copy methods to copy objects from a 'sample-sandbox'
    bucket to both 'sample-pipeline' and 'sample-production' buckets.

    Two boto3 sessions are created, one with profile_name '*************321' and another with profile_name '*************123',
    to handle copying objects to the 'sample-pipeline' and 'sample-production' buckets, respectively.

    """
    # Create S3 client for pipeline
    session_pipeline = boto3.Session(profile_name='*************321')
    pipeline_copier = S3Copier(session_pipeline, "sample-sandbox", "sample-pipeline")
    print("Copying files from Sandbox to Pipeline Bucket./n")
    pipeline_copier.copy()

    # Create S3 client for production
    session_production = boto3.Session(profile_name='*************123')
    production_copier = S3Copier(session_production, "sample-sandbox", "sample-production")
    print("Copying files from Sandbox to Production Bucket./n")
    production_copier.copy()

if __name__ == "__main__":
    main()
