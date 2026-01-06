"""Library dependency management for Zapio.

This module handles downloading, extracting, and compiling external libraries
from lib_deps in platformio.ini. Libraries are cached locally in the build
directory for fast rebuilds and proper invalidation.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from zapio.packages.downloader import PackageDownloader


class LibraryError(Exception):
    """Base exception for library management errors."""

    pass


class GitHubURLOptimizer:
    """Optimizes GitHub URLs to use zip downloads instead of git clone."""

    @staticmethod
    def is_github_url(url: str) -> bool:
        """Check if a URL is a GitHub repository URL.

        Args:
            url: The URL to check

        Returns:
            True if the URL is a GitHub repository
        """
        parsed = urlparse(url)
        return parsed.netloc.lower() in ("github.com", "www.github.com")

    @staticmethod
    def detect_default_branch(url: str) -> str:
        """Detect the default branch name for a GitHub repository.

        Makes a HEAD request to determine if the repo uses 'main' or 'master'.

        Args:
            url: GitHub repository URL

        Returns:
            Default branch name ('main' or 'master')
        """
        try:
            import requests

            # Try main first (modern default)
            test_url = f"{url}/archive/refs/heads/main.zip"
            response = requests.head(test_url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                return "main"

            # Fall back to master
            test_url = f"{url}/archive/refs/heads/master.zip"
            response = requests.head(test_url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                return "master"

            # Default to main if both fail
            return "main"

        except Exception:
            # If we can't detect, default to main
            return "main"

    @classmethod
    def optimize_url(cls, url: str) -> str:
        """Convert a GitHub URL to use zip download instead of git clone.

        Transforms:
            https://github.com/FastLED/FastLED
        Into:
            https://github.com/FastLED/FastLED/archive/refs/heads/main.zip

        Args:
            url: Original GitHub URL

        Returns:
            Optimized zip download URL
        """
        if not cls.is_github_url(url):
            return url

        # Remove trailing slashes and .git suffix
        url = url.rstrip("/")
        if url.endswith(".git"):
            url = url[:-4]

        # Check if already a zip URL
        if "/archive/" in url:
            return url

        # Detect default branch
        branch = cls.detect_default_branch(url)

        # Build zip URL
        return f"{url}/archive/refs/heads/{branch}.zip"


class LibraryInfo:
    """Metadata about a downloaded and compiled library."""

    def __init__(
        self,
        name: str,
        url: str,
        version: str,
        commit_hash: Optional[str],
        compiler: str,
        compile_commands: List[str],
        link_commands: List[str],
    ):
        """Initialize library info.

        Args:
            name: Library name
            url: Source URL
            version: Version or commit
            commit_hash: Git commit hash if available
            compiler: Compiler used
            compile_commands: Commands used for compilation
            link_commands: Commands/flags for linking
        """
        self.name = name
        self.url = url
        self.version = version
        self.commit_hash = commit_hash
        self.compiler = compiler
        self.compile_commands = compile_commands
        self.link_commands = link_commands

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "url": self.url,
            "version": self.version,
            "commit_hash": self.commit_hash,
            "compiler": self.compiler,
            "compile_commands": self.compile_commands,
            "link_commands": self.link_commands,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "LibraryInfo":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            url=data["url"],
            version=data["version"],
            commit_hash=data.get("commit_hash"),
            compiler=data["compiler"],
            compile_commands=data["compile_commands"],
            link_commands=data["link_commands"],
        )

    def save(self, path: Path) -> None:
        """Save library info to JSON file.

        Args:
            path: Path to info.json file
        """
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: Path) -> "LibraryInfo":
        """Load library info from JSON file.

        Args:
            path: Path to info.json file

        Returns:
            LibraryInfo instance
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


class Library:
    """Represents a downloaded and compiled library."""

    def __init__(self, lib_dir: Path, name: str):
        """Initialize library.

        Args:
            lib_dir: Root directory for the library (.zap/build/{mode}/libs/{name})
            name: Library name
        """
        self.lib_dir = lib_dir
        self.name = name
        self.src_dir = lib_dir / "src"
        self.info_file = lib_dir / "info.json"
        self.archive_file = lib_dir / f"lib{name}.a"

    @property
    def exists(self) -> bool:
        """Check if library is downloaded and compiled."""
        return (
            self.lib_dir.exists()
            and self.src_dir.exists()
            and self.archive_file.exists()
            and self.info_file.exists()
        )

    def get_info(self) -> Optional[LibraryInfo]:
        """Load library info if available."""
        if self.info_file.exists():
            return LibraryInfo.load(self.info_file)
        return None

    def get_source_files(self) -> List[Path]:
        """Find all source files (.c, .cpp) in the library.

        Returns:
            List of source file paths
        """
        if not self.src_dir.exists():
            return []

        sources = []

        # Check for src/src/ structure (like FastLED)
        src_src = self.src_dir / "src"
        search_dir = (
            src_src if (src_src.exists() and src_src.is_dir()) else self.src_dir
        )

        for pattern in ["**/*.c", "**/*.cpp", "**/*.cc", "**/*.cxx"]:
            sources.extend(search_dir.glob(pattern))

        return sources

    def get_include_dirs(self) -> List[Path]:
        """Get include directories for this library.

        For Arduino libraries, the typical structure is:
        - libname/src/ (contains headers and sources)
        - or libname/ (root contains headers)

        Returns:
            List of include directory paths
        """
        include_dirs = []

        if not self.src_dir.exists():
            return include_dirs

        # Check if there's a src subdirectory inside src_dir
        # This happens with libraries like FastLED that have src/src/ structure
        src_src = self.src_dir / "src"
        if src_src.exists() and src_src.is_dir():
            # Arduino library with src/src/ structure
            # Add src/src/ as the main include path
            include_dirs.append(src_src)
        else:
            # Standard Arduino library structure
            # Add src/ as the include path
            include_dirs.append(self.src_dir)

        # Look for additional include directories
        for name in ["include", "Include", "INCLUDE"]:
            inc_dir = self.lib_dir / name
            if inc_dir.exists():
                include_dirs.append(inc_dir)

        return include_dirs


class LibraryManager:
    """Manages library dependencies for a build."""

    def __init__(
        self,
        build_dir: Path,
        mode: str = "release",
        downloader: Optional[PackageDownloader] = None,
    ):
        """Initialize library manager.

        Args:
            build_dir: Build directory (.zap/build/{env_name})
            mode: Build mode (release, quick, debug)
            downloader: Optional custom downloader instance
        """
        self.build_dir = Path(build_dir)
        self.mode = mode
        self.libs_dir = self.build_dir / "libs"
        self.downloader = downloader or PackageDownloader()

        # Ensure libs directory exists
        self.libs_dir.mkdir(parents=True, exist_ok=True)

    def _extract_library_name(self, url: str) -> str:
        """Extract library name from URL.

        Args:
            url: Library URL

        Returns:
            Library name in lowercase
        """
        # For GitHub URLs, use the repo name
        if GitHubURLOptimizer.is_github_url(url):
            parts = urlparse(url).path.strip("/").split("/")
            if len(parts) >= 2:
                name = parts[1]
                # Remove .git suffix if present
                if name.endswith(".git"):
                    name = name[:-4]
                return name.lower()

        # For other URLs, use the filename without extension
        filename = Path(urlparse(url).path).name
        # Remove common archive extensions
        for ext in [".zip", ".tar.gz", ".tar.bz2", ".tar.xz"]:
            if filename.endswith(ext):
                filename = filename[: -len(ext)]
                break

        return filename.lower()

    def get_library(self, name: str) -> Library:
        """Get a Library instance for a given name.

        Args:
            name: Library name

        Returns:
            Library instance
        """
        lib_dir = self.libs_dir / name
        return Library(lib_dir, name)

    def download_library(self, url: str, show_progress: bool = True) -> Library:
        """Download and extract a library from a URL.

        Args:
            url: Library source URL
            show_progress: Whether to show download progress

        Returns:
            Library instance for the downloaded library

        Raises:
            LibraryError: If download or extraction fails
        """
        try:
            # Optimize GitHub URLs
            original_url = url
            if GitHubURLOptimizer.is_github_url(url):
                url = GitHubURLOptimizer.optimize_url(url)
                if show_progress:
                    print(f"Optimized GitHub URL: {url}")

            # Extract library name
            lib_name = self._extract_library_name(original_url)
            library = self.get_library(lib_name)

            # Skip if already downloaded
            if library.exists:
                if show_progress:
                    print(f"Library '{lib_name}' already downloaded")
                return library

            # Create library directory
            library.lib_dir.mkdir(parents=True, exist_ok=True)

            # Download to temporary location
            filename = Path(urlparse(url).path).name
            temp_archive = library.lib_dir / filename

            if show_progress:
                print(f"Downloading library: {lib_name}")

            self.downloader.download(url, temp_archive, show_progress=show_progress)

            # Extract to src directory
            if show_progress:
                print(f"Extracting library: {lib_name}")

            temp_extract = library.lib_dir / "_extract"
            temp_extract.mkdir(exist_ok=True)

            self.downloader.extract_archive(
                temp_archive, temp_extract, show_progress=show_progress
            )

            # Find the actual source directory
            # Archives often have a top-level directory like "FastLED-main"
            extracted_contents = list(temp_extract.iterdir())

            if len(extracted_contents) == 1 and extracted_contents[0].is_dir():
                # Single directory - move its contents
                source_root = extracted_contents[0]
            else:
                # Multiple items - use extract dir as root
                source_root = temp_extract

            # Move to src directory
            if library.src_dir.exists():
                import shutil

                shutil.rmtree(library.src_dir)

            source_root.rename(library.src_dir)

            # Clean up
            if temp_extract.exists():
                import shutil

                shutil.rmtree(temp_extract)
            temp_archive.unlink()

            # Create initial info.json
            info = LibraryInfo(
                name=lib_name,
                url=original_url,
                version="unknown",
                commit_hash=None,
                compiler="",
                compile_commands=[],
                link_commands=[],
            )
            info.save(library.info_file)

            return library

        except Exception as e:
            raise LibraryError(f"Failed to download library from {url}: {e}") from e

    def needs_rebuild(
        self, library: Library, compiler_flags: List[str]
    ) -> Tuple[bool, str]:
        """Check if a library needs to be rebuilt.

        Args:
            library: Library to check
            compiler_flags: Current compiler flags

        Returns:
            Tuple of (needs_rebuild, reason)
        """
        if not library.archive_file.exists():
            return True, "Archive not found"

        if not library.info_file.exists():
            return True, "Info file missing"

        info = library.get_info()
        if info is None:
            return True, "Could not load info"

        # Check if compile commands changed
        current_compile_cmd = " ".join(compiler_flags)
        stored_compile_cmd = " ".join(info.compile_commands)

        if current_compile_cmd != stored_compile_cmd:
            return True, "Compiler flags changed"

        return False, ""

    def compile_library(
        self,
        library: Library,
        compiler_path: Path,
        mcu: str,
        f_cpu: str,
        defines: List[str],
        include_paths: List[Path],
        extra_flags: List[str],
        show_progress: bool = True,
    ) -> Path:
        """Compile a library into a static archive (.a file).

        Args:
            library: Library to compile
            compiler_path: Path to avr-gcc/avr-g++
            mcu: MCU target (e.g., atmega328p)
            f_cpu: CPU frequency (e.g., 16000000L)
            defines: Preprocessor defines
            include_paths: Include directories
            extra_flags: Additional compiler flags
            show_progress: Whether to show progress

        Returns:
            Path to compiled archive file

        Raises:
            LibraryError: If compilation fails
        """
        try:
            if show_progress:
                print(f"Compiling library: {library.name}")

            # Get source files
            sources = library.get_source_files()
            if not sources:
                raise LibraryError(f"No source files found in library '{library.name}'")

            # Get library's own include directories
            lib_includes = library.get_include_dirs()
            all_includes = list(include_paths) + lib_includes

            # Compile each source file
            object_files = []
            gcc_path = compiler_path.parent / "avr-gcc"
            gxx_path = compiler_path.parent / "avr-g++"

            for source in sources:
                # Determine compiler based on extension
                if source.suffix in [".cpp", ".cc", ".cxx"]:
                    compiler = gxx_path
                    std_flag = "-std=gnu++11"
                else:
                    compiler = gcc_path
                    std_flag = "-std=gnu11"

                # Output object file
                obj_file = library.lib_dir / f"{source.stem}.o"

                # Build compile command
                # Use -flto with -fno-fat-lto-objects to generate only LTO bytecode
                # This avoids assembly errors with complex code like FastLED
                # The trade-off is we must link with object files, not archives
                cmd = [
                    str(compiler),
                    "-c",
                    "-g",
                    "-Os",
                    std_flag,
                    "-ffunction-sections",
                    "-fdata-sections",
                    "-flto",
                    "-fno-fat-lto-objects",  # LTO bytecode only, no assembly
                    f"-mmcu={mcu}",
                ]

                # Add defines from list (format: "KEY=value" or "KEY")
                for define in defines:
                    cmd.append(f"-D{define}")

                # Add include paths
                for inc_path in all_includes:
                    cmd.append(f"-I{inc_path}")

                # Add extra flags
                cmd.extend(extra_flags)

                # Add source and output
                cmd.extend(["-o", str(obj_file), str(source)])

                # Compile
                if show_progress:
                    print(f"  Compiling {source.name}...")

                result = subprocess.run(
                    cmd, capture_output=True, text=True, encoding="utf-8"
                )

                if result.returncode != 0:
                    raise LibraryError(f"Failed to compile {source}:\n{result.stderr}")

                object_files.append(obj_file)

            # Create static archive using avr-ar
            ar_path = compiler_path.parent / "avr-ar"

            if show_progress:
                print(f"  Creating archive: {library.archive_file.name}")

            # Remove old archive if exists
            if library.archive_file.exists():
                library.archive_file.unlink()

            # Create new archive
            cmd = [str(ar_path), "rcs", str(library.archive_file)] + [
                str(obj) for obj in object_files
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, encoding="utf-8"
            )

            if result.returncode != 0:
                raise LibraryError(
                    f"Failed to create archive for {library.name}:\n{result.stderr}"
                )

            # Update info.json with compile information
            info = library.get_info() or LibraryInfo(
                name=library.name,
                url="",
                version="unknown",
                commit_hash=None,
                compiler="",
                compile_commands=[],
                link_commands=[],
            )

            info.compiler = str(compiler_path)
            info.compile_commands = cmd
            info.link_commands = [str(library.archive_file)]
            info.save(library.info_file)

            # Keep object files for LTO linking (don't delete them)
            # Object files are needed for proper LTO symbol resolution

            if show_progress:
                print(f"Library '{library.name}' compiled successfully")

            return library.archive_file

        except subprocess.CalledProcessError as e:
            raise LibraryError(
                f"Compilation failed for library '{library.name}': {e}"
            ) from e
        except Exception as e:
            raise LibraryError(
                f"Failed to compile library '{library.name}': {e}"
            ) from e

    def ensure_libraries(
        self,
        lib_deps: List[str],
        compiler_path: Path,
        mcu: str,
        f_cpu: str,
        defines: List[str],
        include_paths: List[Path],
        extra_flags: List[str],
        show_progress: bool = True,
    ) -> List[Library]:
        """Ensure all library dependencies are downloaded and compiled.

        Args:
            lib_deps: List of library dependency URLs
            compiler_path: Path to compiler
            mcu: MCU target
            f_cpu: CPU frequency
            defines: Preprocessor defines
            include_paths: Include directories
            extra_flags: Additional compiler flags
            show_progress: Whether to show progress

        Returns:
            List of compiled Library instances
        """
        libraries = []

        for url in lib_deps:
            # Download library
            library = self.download_library(url, show_progress)

            # Check if rebuild needed
            needs_rebuild, reason = self.needs_rebuild(library, extra_flags)

            if needs_rebuild:
                if show_progress and reason:
                    print(f"Rebuilding library '{library.name}': {reason}")

                self.compile_library(
                    library,
                    compiler_path,
                    mcu,
                    f_cpu,
                    defines,
                    include_paths,
                    extra_flags,
                    show_progress,
                )

            libraries.append(library)

        return libraries

    def get_library_archives(self) -> List[Path]:
        """Get paths to all compiled library archives.

        Returns:
            List of .a archive file paths
        """
        archives = []
        if self.libs_dir.exists():
            for lib_dir in self.libs_dir.iterdir():
                if lib_dir.is_dir():
                    archive = lib_dir / f"lib{lib_dir.name}.a"
                    if archive.exists():
                        archives.append(archive)
        return archives

    def get_library_objects(self) -> List[Path]:
        """Get paths to all compiled library object files.

        This is useful for LTO linking where object files work better than archives.

        Returns:
            List of .o object file paths from all libraries
        """
        objects = []
        if self.libs_dir.exists():
            for lib_dir in self.libs_dir.iterdir():
                if lib_dir.is_dir():
                    # Find all .o files in the library directory
                    for obj_file in lib_dir.glob("*.o"):
                        objects.append(obj_file)
        return objects

    def get_library_include_paths(self) -> List[Path]:
        """Get all include paths from downloaded libraries.

        Returns:
            List of include directory paths
        """
        include_paths = []
        if self.libs_dir.exists():
            for lib_dir in self.libs_dir.iterdir():
                if lib_dir.is_dir():
                    library = Library(lib_dir, lib_dir.name)
                    include_paths.extend(library.get_include_dirs())
        return include_paths
