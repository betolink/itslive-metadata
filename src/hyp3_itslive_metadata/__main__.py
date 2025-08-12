"""itslive-metadata processing for HyP3."""

import logging
from argparse import ArgumentParser
from pathlib import Path
from urllib.parse import urlparse

from hyp3lib.aws import upload_file_to_s3

from hyp3_itslive_metadata.aws import determine_granule_uri_from_bucket, upload_file_to_s3_with_publish_access_keys
from hyp3_itslive_metadata.process import process_itslive_metadata


def str_without_trailing_slash(s: str) -> str:
    return s.rstrip('/')


def main() -> None:
    """HyP3 entrypoint for hyp3_itslive_metadata."""
    parser = ArgumentParser()
    hyp3_group = parser.add_argument_group(
        'HyP3 content bucket',
        'AWS S3 bucket and prefix to upload metadata product(s) to. Will also be used to find the input granule if `--granule-uri` is not provided`.',
    )
    hyp3_group.add_argument('--bucket')
    hyp3_group.add_argument('--bucket-prefix', default='')

    parser.add_argument(
        '--granule-uri',
        help='URI for a granule to generate metadata for. If not provided, will find the first granule in HyP3 content bucket.',
    )

    parser.add_argument(
        '--publish-output',
        type=str_without_trailing_slash,
        help='Additional S3 location (bucket + prefix) for STAC item to be published to (e.g., `s3://its-live-data/test-space/stac/ndjson/ingest`).',
    )

    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO
    )
    logging.info(f'Processing itslive metadata with args: {args}')

    if args.granule_uri is None:
        if args.bucket:
            args.granule_uri = determine_granule_uri_from_bucket(args.bucket, args.bucket_prefix)
        else:
            raise ValueError('Must provide --granule-uri or --bucket')

    metadata_files = process_itslive_metadata(args.granule_uri)

    if args.bucket and args.bucket_prefix:
        logging.info(f'Uploading metadata files to s3://{args.bucket}/{args.bucket_prefix}/')
        for file in metadata_files:
            upload_file_to_s3(file, args.bucket, args.bucket_prefix)

    if args.publish_output:
        for file in metadata_files:
            if '.stac.json' in file.name:
                logging.info(f'Publishing STAC JSON to: {args.publish_output}/{file.name}')
                publish_uri = urlparse(args.publish_output)
                upload_file_to_s3_with_publish_access_keys(
                    file, bucket=publish_uri.netloc, prefix=publish_uri.path.lstrip('/')
                )
            else:
                publish_uri = urlparse(args.granule_uri)
                publish_bucket = publish_uri.netloc
                publish_prefix = str(Path(publish_uri.path).parent)
                logging.info(f'Publishing {file.suffix.upper()} to: {publish_bucket}/{publish_prefix}/{file.name}')
                upload_file_to_s3_with_publish_access_keys(file, bucket=publish_bucket, prefix=publish_prefix)


if __name__ == '__main__':
    main()
