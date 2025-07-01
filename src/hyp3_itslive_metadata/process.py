"""itslive-metadata processing."""

import logging
from pathlib import Path, PurePosixPath

import s3fs
from cryoforge import generate_itslive_metadata, save_metadata


log = logging.getLogger(__name__)


def process_itslive_metadata(bucket: str = "",
                             prefix: str = "") -> list[Path]:
    """Generates ITS_LIVE granule metadata files from a source S3 bucket, copies the files back to the source bucket.
    It also copies the STAC item to a designated ingest location in S3.

    Args:
        bucket: S3 bucket.
        prefix: S3 prefix for the granule.
        stac_output: S3 path for the STAC item.

    Outputs:
        str: S3 path of the generated STAC item.
    """
    s3_fs = s3fs.S3FileSystem(anon=False)
    bucket_prefix = str(PurePosixPath(bucket) / prefix)
    if not bucket_prefix.endswith('/'):
        bucket_prefix += '/'
    granules = s3_fs.glob(f'{bucket_prefix}*.nc') # should only be one
    granule = granules[0] if granules else None
    if not granule:
        raise ValueError(f"No granules found in {bucket_prefix}")

    log.debug(f'Processing itslive metadata for granule: {granule}')
    metadata = generate_itslive_metadata(
        url=granule,
        store=None # Store is for Obstore
    )
    # saves the stac item, the nsidc 
    save_metadata(metadata, "./output")
    file_paths = [f for f in Path("./output").glob("*") if not f.name.endswith(".ref.json")]

    return file_paths
