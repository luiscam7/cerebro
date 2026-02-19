# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


## [0.13.0] - 2023-12-08

### Added
- Added peak detection with Fooof library.
- Connectivity and graph analysis.
- Added unit test for get_version function.

### Removed
- DSP_utils folder and functions.


## [0.12.0] - 2023-12-07

### Added
- NeuroDSP convenient functions for absolute/relative/band ratio power calculations.
- Fooof library for finding individual alpha peak frequency and statistics.

### Removed
- Native absolute power calculation.

### Changed
- Refactored QEEG analysis code with NeuroDSP functions to simplify the codebase.

## [0.11.0] - 2023-12-06

### Added
- Added mesuring date, processing date, version, sampling rate, filename , and source to analysis JSON.


## [0.10.0] - 2023-11-28

### Added
- Unit test for writers.py functions.
- Additional top level documentation across all modules.

### Changed
- Changed powerline noise removal logic, using maximum peak height instead of area under the curve to gauge notch filter decision process.
- Updated TUH parser to check for ECG and ear clip channels.
### Fixed
- Fixed a bug where preprocessing would impact both the original eeg as well as the filtered (processed) data. 

### Removed
- Removed default sampling rate, nyquist limit, and EEG spectrum parameters from paras.py.
- Removed hdf5 analysis output method.
- Decorator module.


## [0.9.0] - 2023-11-27

### Added
- New methods for saving analysis data in the Cerebro class. Save data in JSON, HDF5 format.
- Added new methods to QEEGAnalysis class. Calculate Power Spectra, Magnitude Spectra, Power Ratios, Determine Frontal Generator, Low voltage EEG endophenotype.
- EEG Frequency bands are defined in params.


## [0.8.0] - 2023-11-26

### Changed
- Modified parameters around PSD calculation.
- Captured data if ecg noise/powerline noise was detected or removed.
- Made Cerebro a dataclass.
- Added more logging statements  and error handling around preprocessing functions.


## [0.7.0] - 2023-11-26
### Added
- Created PowerSpectralAnalysis class that inherits from Cerebro. 
- Added new constants that defined EEG regions as a list of channels.
- Add JSON files to gitignore.

### Changed
- Changed local.py to test new PowerSpectrumAnalysis class.

### Removed
- Deleted test_qeeg, need to think of a better way to test new classes. 


## [0.6.0] - 2023-11-25
### Added
- Parser for TDBrain dataset's Brainvision eeg files.
- Local script for quick testing.

### Changed
- Upgrade to Python 3.10.
- Import statements for Cerebro and various EEG parsers.
- Renamed all Parser classes.
- Ruff ignores F401 errors; ignore unused imports across all init scripts.


## [0.5.0] - 2023-11-24
### Added
- Added Github actions workflow for linting, formatting, and testing.


## [0.4.0] - 2023-11-24
### Added
- Development of a concrete Cerebro class.
- Preprocessing module includes bandpass filter, automatic detection and removal of powerline noise and ecg interfernece.
- Added function to compute power spectral density.
- Expanded params; set default sampling rate to 200 Hz for all eeg processing, set high threshold for ECG contamination.
- Added unit tests for preprocessing, base models, parsing, parameters in Pytest.


## [0.3.0] - 2023-11-23
### Added
- Temple University EEG Corpus Edf parser.


## [0.2.0] - 2023-11-23
### Added
- Created EdfParser base class.
- Developed CHBMP parser that inherits from the EdfParser class and reconfigures the Cuban Human Brain Mapping Project's 10-10 system to 10-20.
- Added notebook folder for exploratory data analysis.


## [0.1.0] - 2023-11-22
### Added
- Created project scaffold and project requirements using UV.
- Create Makefile to streamline lint, formatting, and test commands.
- Create abstract base classes for Cerebro and Parser objects.

