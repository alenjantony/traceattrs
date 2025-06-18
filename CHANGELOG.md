# Changelog

## [1.0.1] - 2025-06-18
### Changed
- Fixed typo in the changelog where the year was incorrecly listed as 2024 instead of 2025
- Switched build backend from setuptools to flit for modern, PEP 517-compliant builds and installation using only pyproject.toml
- **Motivation**: setuptools does not fully support installation using only pyproject.toml and still requires setup.py or setup.cfg for metadata

## [1.0.0] - 2025-06-18
### Added
- Initial release of traceattrs
- Track changes to any attribute of class instances
- Support for regular classes, dataclasses and classes with __slots__
- Supports inheritance: tracks attribute changes in both base and derived classes
- Access attribute history via dot notation
- Includes history management (clear, get all)
- Pure Python, no dependencies
- Includes tests and documentation
