"""
DataLoader — swappable data source for the spending pipeline.

Set DATA_SOURCE env var to choose where input files come from:
  DATA_SOURCE=local  (default) — reads from a folder on local disk
  DATA_SOURCE=s3     — downloads files from an S3 bucket before processing

For S3 mode, also set:
  S3_BUCKET=my-bucket-name
  S3_PREFIX=monthly/data/    (optional, defaults to bucket root)
  AWS_REGION=ap-south-1      (or configure via AWS CLI / EC2 instance role)

Usage in spending_pipeline or any script:
    from data_loader import get_loader
    loader = get_loader()
    local_folder = loader.acquire(dest_dir="/tmp/my-work-dir")
    # ... run pipeline on local_folder ...
    loader.release(dest_dir="/tmp/my-work-dir")
"""

import os
import shutil
from abc import ABC, abstractmethod


class DataLoader(ABC):
    @abstractmethod
    def acquire(self, dest_dir: str) -> str:
        """Make source files available locally. Returns the path to process."""

    @abstractmethod
    def release(self, dest_dir: str) -> None:
        """Clean up any temp resources created by acquire."""


class LocalDataLoader(DataLoader):
    def __init__(self, source_folder: str):
        self.source_folder = source_folder

    def acquire(self, dest_dir: str) -> str:
        return self.source_folder  # files already on disk — nothing to download

    def release(self, dest_dir: str) -> None:
        pass  # nothing to clean up


class S3DataLoader(DataLoader):
    def __init__(self, bucket: str, prefix: str = "", region: str = None):
        self.bucket = bucket
        self.prefix = prefix.rstrip("/") + "/" if prefix else ""
        self.region = region or os.environ.get("AWS_REGION", "ap-south-1")

    def acquire(self, dest_dir: str) -> str:
        import boto3
        s3 = boto3.client("s3", region_name=self.region)
        paginator = s3.get_paginator("list_objects_v2")
        downloaded = 0
        for page in paginator.paginate(Bucket=self.bucket, Prefix=self.prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                filename = key[len(self.prefix):]
                if not filename or filename.endswith("/"):
                    continue
                local_path = os.path.join(dest_dir, os.path.basename(filename))
                s3.download_file(self.bucket, key, local_path)
                downloaded += 1
        print(f"  [S3] Downloaded {downloaded} file(s) from s3://{self.bucket}/{self.prefix}")
        return dest_dir

    def release(self, dest_dir: str) -> None:
        shutil.rmtree(dest_dir, ignore_errors=True)


def get_loader() -> DataLoader:
    """Return the right DataLoader based on DATA_SOURCE env var."""
    source = os.environ.get("DATA_SOURCE", "local").lower()
    if source == "s3":
        bucket = os.environ.get("S3_BUCKET")
        if not bucket:
            raise EnvironmentError("S3_BUCKET env var is required when DATA_SOURCE=s3")
        prefix = os.environ.get("S3_PREFIX", "")
        return S3DataLoader(bucket=bucket, prefix=prefix)
    folder = os.environ.get("DATA_FOLDER", "../../local-database/budget-tracker/monthly-data")
    return LocalDataLoader(source_folder=folder)
