from __future__ import annotations

import os
import pathlib
import shutil

import nox

PROJECT = "gimli.units"
ROOT = os.path.dirname(os.path.abspath(__file__))


@nox.session
def test(session: nox.Session) -> None:
    """Run the tests."""
    session.install(
        *("-r", "requirements.in"),
        *("-r", "requirements-testing.in"),
    )

    _print_python_version(session)
    _install_from_path(session, path=session.posargs[0] if session.posargs else None)
    _test(session)


@nox.session
def coverage(session: nox.Session) -> None:
    """Run the tests and coverage."""
    env = {"UDUNITS2_PREFIX": session.posargs[0]} if session.posargs else None

    session.install(
        *("-r", "requirements.in"),
        *("-r", "requirements-testing.in"),
    )

    _print_python_version(session)
    session.install("-e", ".", env=env)
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


@nox.session(name="build-expat", python=None)
def build_expat(session: nox.Session) -> None:
    inst_dir = _build_expat(session, session.posargs[0] if session.posargs else None)
    session.log(inst_dir)


@nox.session(name="build-udunits", python=None)
def build_udunits(session: nox.Session) -> None:
    inst_dir = _build_udunits(session, session.posargs[0] if session.posargs else None)
    session.log(inst_dir)


@nox.session(name="build-vendor", python=None)
def build_vendor(session: nox.Session) -> None:
    inst_dir = os.path.abspath(
        session.posargs[0] if session.posargs else os.path.join(ROOT, "dist", "vendor")
    )

    _build_expat(session, inst_dir=inst_dir)
    _build_udunits(session, inst_dir=inst_dir, expat_prefix=inst_dir)

    session.log(inst_dir)


def _build_expat(session: nox.Session, inst_dir=None) -> str:
    inst_dir = os.path.abspath(session.create_tmp() if inst_dir is None else inst_dir)
    build_dir = os.path.join(session.create_tmp(), "expat")

    src_dir = os.path.join(ROOT, "extern", "expat-2.6.0")

    session.run(
        "cmake",
        *("-S", src_dir),
        *("-B", build_dir),
        f"-DCMAKE_INSTALL_PREFIX={inst_dir}",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_INSTALL_LIBDIR=lib",
        "-DBUILD_SHARED_LIBS=OFF",
        "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
        external=True,
    )
    session.run("cmake", "--build", build_dir, "--config", "Release", external=True)
    session.run("cmake", "--install", build_dir, "--config", "Release", external=True)

    return inst_dir


def _build_udunits(session: nox.Session, inst_dir=None, expat_prefix=None) -> str:
    inst_dir = os.path.abspath(session.create_tmp() if inst_dir is None else inst_dir)
    build_dir = os.path.join(session.create_tmp(), "udunits")

    extra_args = []
    if expat_prefix is not None:
        extra_args += [
            f"-DEXPAT_INCLUDE_DIR={expat_prefix}/include",
            f"-DEXPAT_LIBRARY={expat_prefix}/lib/libexpat.a",
        ]

    src_dir = os.path.join(ROOT, "extern", "udunits-2.2.28")

    session.run(
        "cmake",
        *("-S", src_dir),
        *("-B", build_dir),
        f"-DCMAKE_INSTALL_PREFIX={inst_dir}",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_INSTALL_LIBDIR=lib",
        "-DBUILD_SHARED_LIBS=OFF",
        "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
        *extra_args,
        external=True,
    )
    session.run("cmake", "--build", build_dir, "--config", "Release", external=True)
    session.run("cmake", "--install", build_dir, "--config", "Release", external=True)

    return inst_dir


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

    base = os.path.realpath(ROOT)
    for folder in folders:
        if os.path.commonpath([base, os.path.realpath(folder)]) != base:
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


def _print_python_version(session: nox.Session) -> None:
    session.log(f"nox session.python = {session.python}")
    session.run("python", "-c", "import sys; print(sys.executable); print(sys.version)")


def _test(session: nox.Session, path=None, tmpdir: bool = True) -> None:
    if tmpdir:
        tmp = session.create_tmp()
        session.chdir(tmp)
    session.run("pytest", *_pytest_args())


def _install_from_path(session: nox.Session, path: str | None = None) -> None:
    if path is None:
        _install_editable(session)
    elif os.path.isfile(path):
        session.install(path)
    elif os.path.isdir(path):
        session.install(
            "gimli.units",
            f"--find-links={path}",
            "--no-deps",
            "--no-index",
        )
    else:
        session.error("path must be a source distribution or folder")


def _install_editable(session: nox.Session, udunits_prefix=None) -> None:
    if udunits_prefix is None:
        udunits_prefix = _build_expat(session)
        _build_udunits(session, inst_dir=udunits_prefix, expat_prefix=udunits_prefix)

    session.install("-e", ".", env={"UDUNITS2_PREFIX": udunits_prefix})

    return udunits_prefix


def _pytest_args():
    return (
        "--config-file",
        os.path.join(ROOT, "pyproject.toml"),
        "--doctest-modules",
        "--pyargs",
        "gimli",
        os.path.join(ROOT, "tests"),
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
        session.run("coverage", "xml", "-o", os.path.join(ROOT, "coverage.xml"))
