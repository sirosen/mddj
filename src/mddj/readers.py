import contextlib
import pathlib
import tarfile

from importlib_metadata import Distribution


class TarballSourceDistribution(Distribution):
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.dist_name = path.name.rsplit(".", 2)[0]

    def read_text(self, filename: str) -> str | None:
        with tarfile.open(self.path, "r:gz") as tf:
            with contextlib.suppress(KeyError):
                fp = tf.extractfile(f"{self.dist_name}/{filename}")
                if fp is None:
                    return None
                return fp.read().decode()

    def locate_path(self, path: str) -> pathlib.Path:
        return pathlib.PurePosixPath(path)
