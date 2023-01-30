import boto3
import sys
import argparse

class S3Copier:
    def __init__(self, session, source_bucket_name, destination_bucket_name):
        self.s3 = session.resource("s3")
        self.source_bucket = self.s3.Bucket(source_bucket_name)
        self.destination_bucket = self.s3.Bucket(destination_bucket_name)

    def copy(self, folder_name):
        # Counter for total objects to be copied
        counter = 1
        # Total number of objects to be copied
        total_objects = sum(1 for _ in self.source_bucket.objects.filter(Prefix=folder_name))
        # Loop through objects in source bucket with prefix folder_name
        for obj in self.source_bucket.objects.filter(Prefix=folder_name):
            obj_key = obj.key
            # Copy object from source to destination bucket
            self.s3.meta.client.copy_object(Bucket=self.destination_bucket.name, CopySource={"Bucket": self.source_bucket.name, "Key": obj_key}, Key=obj_key)
            print(f"\tCopied object {counter}/{total_objects}: {obj_key}")
            counter += 1

    def delete_existing_objects(self, folder_name):
        # Get a list of all object versions in the destination bucket
        versions = self.destination_bucket.object_versions.all()
        if versions:
            delete_batch = []
            # Loop through object versions in destination bucket
            for version in versions:
                if version.object_key.startswith(folder_name + '/'):
                    # Add object to delete batch
                    delete_batch.append({'Key': version.object_key, 'VersionId': version.id})
            # Delete objects if the delete_batch is not empty
            if delete_batch:
                self.destination_bucket.delete_objects(Delete={'Objects': delete_batch})
                print(f"Deleted existing objects in {folder_name} from {self.destination_bucket.name}")
            else:
                print(f"No objects found in {folder_name} in {self.destination_bucket.name}")
        else:
            print(f"No object versions found in {self.destination_bucket.name}")

def main():
    if len(sys.argv) < 2:
        print("Please provide the folder names to be copied as arguments")
        return

    # Create S3 client for pipeline
    session_pipeline = boto3.Session(profile_name='boomi-dcp-pipeline-admin')
    pipeline_copier = S3Copier(session_pipeline, "dcp-resources-sandbox", "dcp-resources-pipeline")

    # Create S3 client for production
    session_production = boto3.Session(profile_name='boomi-dcp-production-admin')
    production_copier = S3Copier(session_production, "dcp-resources-sandbox", "dcp-resources-production")

    folder_names = sys.argv[1:]
    for folder_name in folder_names:
        print(f"Deleting existing objects in {folder_name} from Pipeline Bucket...")
        pipeline_copier.delete_existing_objects(folder_name)

        print(f"Copying {folder_name} from Sandbox to Pipeline Bucket.\n")
        pipeline_copier.copy(folder_name)

        print(f"Deleting existing objects in {folder_name} from Production Bucket...")
        production_copier.delete_existing_objects(folder_name)

        print(f"Copying {folder_name} from Sandbox to Production Bucket.\n")
        production_copier.copy(folder_name)


# The code sets up an argparse argument parser with a description and a positional argument "folder_names" that takes one or more folders to be copied.
# It then parses the command line arguments, obtains the "folder_names" argument and passes it to the main function.
# Finally, it calls the main function.

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Copy S3 folders')
    parser.add_argument('folder_names', nargs='+', help='Folders to be copied')

    args = parser.parse_args()
    folder_names = args.folder_names
    main()
