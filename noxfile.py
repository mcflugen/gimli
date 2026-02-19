from __future__ import annotations

import os
import pathlib
import shutil

import nox

PROJECT = "gimli.units"
ROOT = pathlib.Path(__file__).parent
PYTHON_VERSION = "3.12"


@nox.session(python=PYTHON_VERSION)
def test(session: nox.Session) -> None:
    """Run the tests."""
    arg = session.posargs[0] if session.posargs else None
    if arg and os.path.isdir(arg):
        session.install(
            "gimli.units",
            f"--find-links={arg}",
            "--no-deps",
            "--no-index",
        )
    elif arg and os.path.isfile(arg):
        session.install(arg, "--no-deps")
    else:
        session.install(".", "--no-deps")

    session.install(
        *("-r", "requirements.in"),
        *("-r", "requirements-testing.in"),
    )
    session.run("pytest", *_pytest_args())


@nox.session
def coverage(session: nox.Session) -> None:
    session.install(
        *("-r", "requirements.in"),
        *("-r", "requirements-testing.in"),
    )

    session.install("-e", ".")
    _coverage(session, tmpdir=False)


@nox.session
def lint(session: nox.Session) -> None:
    """Look for lint."""
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files")


@nox.session
def build(session: nox.Session) -> None:
    session.install("pip")
    session.install("build")
    session.run("python", "--version")
    session.run("pip", "--version")
    session.run("python", "-m", "build", "--outdir", "./build/wheelhouse")


@nox.session(name="build-extern", python=None)
def build_extern(session: nox.Session) -> None:
    build_dir = str(ROOT / "build/extern")
    inst_dir = str(ROOT / "dist/extern")
    src_dir = str(ROOT / "extern/udunits-2.2.28")

    os.makedirs(inst_dir, exist_ok=True)

    os.makedirs(os.path.join(build_dir, "expat"), exist_ok=True)
    with session.chdir(os.path.join(build_dir, "expat")):
        session.run(
            "cmake",
            *("-S", str(ROOT / "extern/expat-2.6.0/")),
            *("-D", f"CMAKE_INSTALL_PREFIX={inst_dir}"),
            external=True,
        )
        session.run(
            "cmake",
            *("--build", "."),
            *("--config", "Release"),
            external=True,
        )
        session.run(
            "cmake",
            *("--build", "."),
            *("--config", "Release"),
            *("--target", "install"),
            external=True,
        )

    os.makedirs(os.path.join(build_dir, "udunits"), exist_ok=True)
    with session.chdir(os.path.join(build_dir, "udunits")):
        session.run(
            "cmake",
            *("-S", src_dir),
            *("-D", f"CMAKE_INSTALL_PREFIX={inst_dir}"),
            *("-D", f"EXPAT_LIBRARY={inst_dir}/lib/libexpat.dylib"),
            env={
                "LD_LIBRARY_PATH": f"{inst_dir}/lib",
                "DYLD_LIBRARY_PATH": f"{inst_dir}/lib",
                "LDFLAGS": f"-L{inst_dir}/lib",
                "CFLAGS": f"-I{inst_dir}/include",
            },
            external=True,
        )
        session.run(
            "cmake",
            *("--build", "."),
            *("--config", "Release"),
            *("--target", "libudunits2"),
            external=True,
        )
        session.run(
            "cmake",
            *("--build", "."),
            *("--config", "Release"),
            *("--target", "install"),
            external=True,
        )


@nox.session(name="build-docs")
def build_docs(session: nox.Session) -> None:
    """Build the docs."""

    build_generated_docs(session)

    session.install(
        *("-r", "requirements-docs.in"),
        *("-r", "requirements.in"),
    )
    session.install(".")

    pathlib.Path("build").mkdir(exist_ok=True)

    session.run(
        "sphinx-build",
        "-b",
        "html",
        "-W",
        "--keep-going",
        "docs",
        "build/html",
    )
    session.log("generated docs at build/html")


@nox.session(name="build-generated-docs", reuse_venv=True)
def build_generated_docs(session: nox.Session) -> None:
    """Build auto-generated files used by the docs."""
    # FOLDER["docs_generated"].mkdir(exist_ok=True)

    session.install("sphinx")
    session.install("-e", ".")

    with session.chdir(ROOT):
        os.makedirs("src/docs/_generated/api", exist_ok=True)
        session.log("generating api docs in docs/api")
        session.run(
            "sphinx-apidoc",
            "-e",
            "-force",
            "--no-toc",
            "--module-first",
            "-o",
            "docs/_generated/api",
            "src/bmi_tester",
        )


@nox.session(name="publish-testpypi")
def publish_testpypi(session):
    """Publish wheelhouse/* to TestPyPI."""
    session.run("twine", "check", "build/wheelhouse/*")
    session.run(
        "twine",
        "upload",
        "--skip-existing",
        "--repository-url",
        "https://test.pypi.org/legacy/",
        "build/wheelhouse/*.tar.gz",
    )


@nox.session(name="publish-pypi")
def publish_pypi(session):
    """Publish wheelhouse/* to PyPI."""
    session.run("twine", "check", "build/wheelhouse/*")
    session.run(
        "twine",
        "upload",
        "--skip-existing",
        "build/wheelhouse/*.tar.gz",
    )


@nox.session(name="list-ci-matrix")
def list_ci_matrix(session):
    def _os_from_wheel(name):
        if "linux" in name:
            return "ubuntu-latest"
        elif "macos" in name:
            return "macos-latest"
        elif "win" in name:
            return "windows-latest"

    for wheel in _get_wheels(session):
        print(f"- cibw-only: {wheel!r}".replace("'", '"'))
        print(f"  os: {_os_from_wheel(wheel)!r}".replace("'", '"'))


def _get_wheels(session):
    platforms = session.posargs or ["linux", "macos", "windows"]
    session.install("cibuildwheel")

    wheels = []
    for platform in platforms:
        wheels += session.run(
            "cibuildwheel",
            "--print-build-identifiers",
            "--platform",
            platform,
            silent=True,
        ).splitlines()
    return wheels


@nox.session(python=False)
def clean(session):
    """Remove all .venv's, build files and caches in the directory."""
    folders = (
        (ROOT,) if not session.posargs else (pathlib.Path(f) for f in session.posargs)
    )

    for folder in folders:
        if not str(folder.resolve()).startswith(str(ROOT.resolve())):
            session.log(f"skipping {folder}: folder is outside of repository")
            continue

        with session.chdir(folder):
            session.log(f"cleaning {folder}")

            shutil.rmtree("build", ignore_errors=True)
            shutil.rmtree("dist", ignore_errors=True)
            shutil.rmtree(f"src/{PROJECT}.egg-info", ignore_errors=True)
            shutil.rmtree(".pytest_cache", ignore_errors=True)
            shutil.rmtree(".venv", ignore_errors=True)

            for d in ("src", "tests"):
                with session.chdir(d):
                    for pattern in ["*.py[co]", "__pycache__", "*.c", "*.so"]:
                        _clean_rglob(pattern)


def _clean_rglob(pattern):
    nox_dir = pathlib.Path(".nox")

    for p in pathlib.Path(".").rglob(pattern):
        if nox_dir in p.parents:
            continue
        if p.is_dir():
            p.rmdir()
        else:
            p.unlink()


def _pytest_args():
    return (
        "--config-file",
        os.path.join(str(ROOT), "pyproject.toml"),
        "--doctest-modules",
        "--pyargs",
        "gimli",
        os.path.join(str(ROOT), "tests"),
    )


def _coverage(session: nox.Session, tmpdir: bool = True) -> None:
    if tmpdir:
        tmp_dir = session.create_tmp()
        session.chdir(tmp_dir)

    session.run(
        "coverage",
        "run",
        *("-m", "pytest"),
        *_pytest_args(),
        env={"COVERAGE_CORE": "sysmon"},
    )

    session.run("coverage", "report", "--ignore-errors", "--show-missing")
    if "CI" in os.environ:
        session.run("coverage", "xml", "-o", os.path.join(str(ROOT), "coverage.xml"))
