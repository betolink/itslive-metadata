"""itslive-metadata processing for HyP3."""

import logging
from argparse import ArgumentParser

from hyp3lib.aws import upload_file_to_s3

from hyp3_itslive_metadata.process import process_itslive_metadata


def main() -> None:
    """HyP3 entrypoint for hyp3_itslive_metadata."""
    parser = ArgumentParser()
    parser.add_argument('--bucket', help='AWS S3 bucket HyP3 for upload the final product(s)')
    parser.add_argument('--bucket-prefix', default='', help='Add a bucket prefix to product(s)')

    parser.add_argument(
        '--stac-output',
        help='S3 location for STAC item inside the its-live-data bucket',
        default='s3://its-live-data/test-space/stac/ndjson/ingest',
    )
    parser.add_argument(
        '--upload',
        help='Upload metadata files to S3',
        default=False,
        action='store_true',
    )

    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO
    )
    print(f'Processing itslive metadata with args: {args}')

    if args.bucket and args.bucket_prefix:
        metadata_files = process_itslive_metadata(bucket=args.bucket, prefix=args.bucket_prefix)
        if args.upload:
            logging.debug('Uploading metadata files to S3...')
            for file in metadata_files:
                if '.stac.json' in file.name:
                    # assumes the same AWS credentials will work with this bucket
                    upload_file_to_s3(file, bucket='its-live-data', prefix=args.stac_output)
                upload_file_to_s3(file, args.bucket, args.bucket_prefix)
            logging.info(f'Uploaded {len(metadata_files)} files to {args.bucket}/{args.bucket_prefix}')


if __name__ == '__main__':
    main()
