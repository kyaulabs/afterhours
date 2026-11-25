"""Run a disposable, offline single-player test with a cached 64-bit Windows Prism instance."""

import argparse
import configparser
import hashlib
import json
import re
import shlex
import shutil
import statistics
import subprocess
import tempfile
from pathlib import Path
from zipfile import ZipFile

from build import DIST, PACK, ROOT, check_files


def classpath(prism, instance):
    libraries = []
    components = json.loads((instance / "mmc-pack.json").read_text())["components"]
    for component in reversed(components):
        meta = prism / "meta" / component["uid"] / (component["version"] + ".json")
        info = json.loads(meta.read_text(encoding="utf-8"))
        rows = list(info.get("libraries", []))
        if "mainJar" in info:
            rows.append(info["mainJar"])
            asset_index = info["assetIndex"]["id"]
            runtime = info["compatibleJavaName"]
        for row in rows:
            if row.get("downloads") == {}:
                continue  # Prism metadata can include a native variant with no artifact.
            rules = row.get("rules", [])
            allowed = not rules
            for rule in rules:
                os_rule = rule.get("os", {})
                if os_rule.get("name", "windows") == "windows" and os_rule.get("arch", "x86_64") in {"x86_64", "amd64"}:
                    allowed = rule["action"] == "allow"
            if allowed:
                group, artifact, version, *classifier = row["name"].split(":")
                jar = "-".join([artifact, version, *classifier]) + ".jar"
                path = prism / "libraries" / Path(*group.split(".")) / artifact / version / jar
                if not path.is_file():
                    raise FileNotFoundError(f"Prism library missing: {path}")
                libraries.append(path.as_posix())
    return ";".join(libraries), asset_index, prism / "java" / runtime / "bin"


def write_args(path, args):
    path.write_text("\n".join('"' + str(arg) + '"' for arg in args), encoding="utf-8")


def install_pack(archive_path, live, game):
    with ZipFile(archive_path) as archive:
        index = json.loads(archive.read("modrinth.index.json"))
        check_files(index, False)
        for entry in index["files"]:
            source = live / entry["path"]
            if hashlib.sha512(source.read_bytes()).hexdigest() != entry["hashes"]["sha512"]:
                raise ValueError(f"Installed download differs from pack: {source.name}")
            dest = game / entry["path"]
            dest.parent.mkdir(exist_ok=True, parents=True)
            shutil.copyfile(source, dest)
        for prefix in ("overrides/", "client-overrides/"):
            for name in archive.namelist():
                if name.startswith(prefix) and not name.endswith("/"):
                    dest = (game / name.removeprefix(prefix)).resolve()
                    if not dest.is_relative_to(game):
                        raise ValueError(f"Invalid archive path: {name}")
                    dest.parent.mkdir(exist_ok=True, parents=True)
                    dest.write_bytes(archive.read(name))
    return index


def run(args, tmp):
    game = tmp / "game"
    game.mkdir()
    parts = json.loads((PACK / "modrinth.index.json").read_text())
    archive = DIST / f"AfterHours-{parts['versionId']}.mrpack"
    index = install_pack(archive, args.instance / "minecraft", game)
    components = {c["uid"]: c["version"] for c in json.loads((args.instance / "mmc-pack.json").read_text())["components"]}
    if (index["dependencies"]["minecraft"] != components["net.minecraft"] or
            index["dependencies"]["fabric-loader"] != components["net.fabricmc.fabric-loader"]):
        raise ValueError("Prism instance and pack must use the same Minecraft and Fabric versions")
    options = game / "options.txt"
    defaults = dict(line.split(":", 1) for line in options.read_text().splitlines() if ":" in line)
    with options.open("a", encoding="utf-8") as settings:
        settings.write('\npauseOnLostFocus:false\nonboardAccessibility:false\ninactivityFpsLimit:"minimized"\n')
    prism = args.instance.parent.parent
    cp, assets, jdk = classpath(prism, args.instance)
    shutil.copyfile(ROOT / "scripts/smoke/WorldProbe.java", tmp / "WorldProbe.java")
    write_args(tmp / "compile.args", ["-classpath", cp, "WorldProbe.java"])
    subprocess.run([jdk / "javac.exe", "@compile.args"], cwd=tmp, check=True)
    probe = tmp / "probe.jar"
    with ZipFile(probe, "w") as jar:
        jar.write(tmp / "WorldProbe.class", "WorldProbe.class")
        jar.writestr("fabric.mod.json", json.dumps({
            "schemaVersion": 1, "id": "afterhours_local_qa", "version": "1.0.0",
            "environment": "client", "entrypoints": {"client": ["WorldProbe"]},
        }))
    width, height = args.size.split("x")
    launcher = configparser.ConfigParser(interpolation=None, strict=False)
    launcher.read([prism / "prismlauncher.cfg"], encoding="utf-8-sig")
    settings = configparser.ConfigParser(interpolation=None, strict=False)
    settings.read(args.instance / "instance.cfg", encoding="utf-8-sig")
    local = settings["General"]
    memory = local if local.getboolean("OverrideMemory", fallback=False) else launcher["General"]
    options_source = local if local.getboolean("OverrideJavaArgs", fallback=False) else launcher["General"]
    # Prism uses the global value when an enabled override has no stored value of its own.
    effective_args = options_source.get("JvmArgs", launcher["General"].get("JvmArgs", ""))
    java_args = args.jvm_arg if args.jvm_arg is not None else shlex.split(effective_args)
    write_args(game / "launch.args", [
        f"-Xms{memory.getint('MinMemAlloc', 512)}m", f"-Xmx{memory.getint('MaxMemAlloc', 4096)}m", *java_args,
        "-Xlog:gc,safepoint", "--enable-native-access=ALL-UNNAMED", f"-Dfabric.addMods={probe.as_posix()}",
        "-cp", cp, "net.fabricmc.loader.impl.launch.knot.KnotClient", "--username", "AfterHoursQA",
        "--uuid", "00000000000040008000000000000001", "--accessToken", "0", "--version", components["net.minecraft"],
        "--gameDir", game.as_posix(), "--assetsDir", (prism / "assets").as_posix(), "--assetIndex", assets,
        "--width", width, "--height", height, "--disableMultiplayer",
    ])
    log = DIST / "smoke.log"
    run_log = tmp / "smoke.log"
    try:
        with run_log.open("wb") as output:
            subprocess.run([jdk / "javaw.exe", "@launch.args"], cwd=game, stdout=output,
                           stderr=subprocess.STDOUT, timeout=420, check=True)
        result = run_log.read_text(encoding="utf-8", errors="replace")
    finally:
        run_log.replace(log)
    pauses = sorted(int(ns) / 1e6 for ns in re.findall(r'Safepoint "(?:G1|Z)[^"]*".*Total: (\d+) ns', result))
    if pauses:
        print(f"GC safepoints ({len(pauses)}): p95 {pauses[(len(pauses) * 95 - 1) // 100]:.2f} ms, max {pauses[-1]:.2f} ms")
    selected = next(file["path"].split("/")[-1] for file in index["files"] if file["path"].startswith("shaderpacks/"))
    for marker in ("AFTERHOURS_WORLD_OK", "Set the weather to rain", "Using graphics backend OpenGL", f"Using shaderpack: {selected}",
                   "Profile: HIGH", "Creating pipeline for dimension minecraft:overworld"):
        if marker not in result:
            raise ValueError(f"Missing {marker!r} in {log}")
    if re.search("falling back to vanilla|failed to create shader rendering pipeline", result, re.I):
        raise ValueError(f"Shader fallback in {log}")
    if error := re.search(r"Mod \S+ provides a broken implementation of ModMenuApi", result):
        raise ValueError(f"{error.group()}. See {log}")
    rows = re.findall(r"AFTERHOURS_SAMPLE (clear|rain) (\d+) (\d+x\d+) (\d+) (\d+)", result)
    for weather in ("clear", "rain"):
        samples = [int(fps) for phase, fps, size, render, sim in rows
                   if (phase, size, render, sim) == (weather, args.size, defaults["renderDistance"], defaults["simulationDistance"])]
        if len(samples) != 20:
            raise ValueError(f"Expected 20 {weather} samples at the configured resolution and distances. See {log}")
        print(f"{weather}: median {statistics.median(samples):g} FPS, range {min(samples)}-{max(samples)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instance", type=Path, help="Cached instance under Prism's instances directory")
    parser.add_argument("--size", default="1280x720", help="Framebuffer size, e.g. 3440x1440")
    parser.add_argument("--jvm-arg", action="append", help="Override the instance JVM arguments for this test. Repeat per flag.")
    args = parser.parse_args()
    args.instance = args.instance.resolve(strict=True)
    if not re.fullmatch(r"[1-9]\d*x[1-9]\d*", args.size):
        parser.error("Expected WIDTHxHEIGHT")
    DIST.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="smoke-", dir=DIST) as directory:
        run(args, Path(directory).resolve())
