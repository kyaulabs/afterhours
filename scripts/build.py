"""Build the importable AfterHours client pack using the Python standard library."""

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "pack"
DIST = ROOT / "dist"
VERSION = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-(?:alpha|beta|rc)\.[1-9][0-9]*)?"


def check_files(index, verify_downloads):
    if index["formatVersion"] != 1 or index["game"] != "minecraft":
        raise ValueError("Expected a format 1 Minecraft modpack")
    if not all(index["dependencies"].get(key) for key in ("minecraft", "fabric-loader")):
        raise ValueError("Pin Minecraft and Fabric Loader in the manifest")
    if not index["files"]:
        raise ValueError("The manifest contains no downloads")
    seen = set()
    for entry in index["files"]:
        name = entry["path"]
        path = PurePosixPath(name)
        if (len(path.parts) != 2 or path.parts[0] not in {"mods", "shaderpacks", "resourcepacks"}
                or path.as_posix() != name or path.name in {".", ".."} or re.search(r"[\\:]", name)):
            raise ValueError(f"Invalid download path: {name}")
        if name.casefold() in seen:
            raise ValueError(f"Duplicate download: {name}")
        seen.add(name.casefold())
        sides = entry["env"]
        if sides["client"] != "required" or sides["server"] not in {"required", "optional", "unsupported"}:
            raise ValueError(f"Invalid pack side for {name}")
        hashes = entry["hashes"]
        for algo, length in (("sha1", 40), ("sha512", 128)):
            if not re.fullmatch(f"[0-9a-f]{{{length}}}", hashes[algo]):
                raise ValueError(f"Invalid {algo} for {name}")
        url, = entry["downloads"]
        parts = urlsplit(url)
        if (parts.scheme != "https" or parts.netloc != "cdn.modrinth.com"
                or unquote(parts.path.split("/")[-1]) != path.name or entry["fileSize"] <= 0):
            raise ValueError(f"Invalid Modrinth download for {name}")
        if verify_downloads:
            request = Request(url, headers={"User-Agent": "kyaulabs/afterhours pack verification"})
            with urlopen(request, timeout=60) as response:
                data = response.read()
            if (len(data) != entry["fileSize"] or hashlib.sha1(data).hexdigest() != hashes["sha1"]
                    or hashlib.sha512(data).hexdigest() != hashes["sha512"]):
                raise ValueError(f"Download differs from manifest: {name}")
    return seen


def build(tag, verify_downloads):
    manifest = PACK / "modrinth.index.json"
    index = json.loads(manifest.read_text(encoding="utf-8"))
    version = index["versionId"]
    if not re.fullmatch(VERSION, version) or (tag is not None and tag != f"v{version}"):
        raise ValueError(f"Invalid pack version or mismatched release tag: {version!r}, {tag!r}")
    downloads = check_files(index, verify_downloads)
    sources = [manifest]
    for folder in ("overrides", "client-overrides", "server-overrides"):
        for path in sorted((PACK / folder).rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Override must be a regular file: {path}")
            if path.is_file():
                relative = path.relative_to(PACK / folder).as_posix()
                if relative.casefold() in downloads or path.suffix.lower() in {".jar", ".zip"}:
                    raise ValueError(f"List third-party downloads in the manifest: {relative}")
                sources.append(path)

    DIST.mkdir(exist_ok=True)
    name = f"AfterHours-{version}.mrpack"
    with TemporaryDirectory(dir=DIST) as tmp:
        output = Path(tmp) / name
        with ZipFile(output, "w") as archive:
            for path in sources:
                member = ZipInfo(path.relative_to(PACK).as_posix())
                member.create_system = 3
                member.external_attr = 0o100644 << 16
                archive.writestr(member, path.read_bytes(), compress_type=ZIP_DEFLATED)
        with ZipFile(output) as archive:
            if archive.testzip() is not None:
                raise ValueError("Archive integrity check failed")
        checksum = hashlib.sha256(output.read_bytes()).hexdigest()
        sidecar = Path(tmp) / (name + ".sha256")
        sidecar.write_text(f"{checksum}  {name}\n", encoding="ascii", newline="\n")
        output.replace(DIST / name)
        sidecar.replace(DIST / sidecar.name)
    print(f"Built {name} with {len(downloads)} pinned downloads and {len(sources) - 1} overrides")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-downloads", action="store_true", help="Fetch each pinned file and verify both hashes and its size")
    parser.add_argument("--tag", help="Require a Git tag matching the pack version")
    args = parser.parse_args()
    build(args.tag, args.verify_downloads)
