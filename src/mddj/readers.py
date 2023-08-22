import pathlib
import tarfile


def read_from_sdist(sdist_path: pathlib.Path, key: str) -> str:
    """
    Read a key from the PKG-INFO file in an sdist.
    """
    dist_name = sdist_path.name.rsplit(".", 2)[0]
    with tarfile.open(sdist_path, "r:gz") as tf:
        pkg_info_fp = tf.extractfile(f"{dist_name}/PKG-INFO")
        if pkg_info_fp is None:
            raise RuntimeError("Could not find and read PKG-INFO in sdist")
        pkg_info = pkg_info_fp.read().decode()
    try:
        data_line = next(
            line for line in pkg_info.splitlines() if line.startswith(f"{key}:")
        )
    except IndexError:
        raise RuntimeError(f"Could not find '{key}' in PKG-INFO")
    return data_line.partition(":")[2].strip()
