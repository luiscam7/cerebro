# Cerebro AI & Analytics Platform Project
[![Lint, Format, Testing](https://github.com/luiscam7/cerebrus/actions/workflows/continuous_improvement.yml/badge.svg)](https://github.com/luiscam7/cerebrus/actions/workflows/continuous_improvement.yml)

![Alternative Text](https://images.theconversation.com/files/374303/original/file-20201210-18-elk4m.jpg?ixlib=rb-1.1.0&rect=0%2C22%2C7500%2C5591&q=45&auto=format&w=926&fit=clip)


## Overview
This project aims to develop a comprehensive toolkit for parsing, analyzing, and modeling EEG data from various neurological and physiological datasets. The primary goal is to facilitate advanced EEG data analysis and develop machine learning models for seizure detection.

## Objectives
- **Wrapper Development**: Creating a robust wrapper around the MNE Python library to streamline EEG data parsing from various datasets.
- **Dataset Analysis**: Analyzing data from the Cuban Human Brain Mapping Project.
- **Model Development**: Training a seizure detection model using the Temple University EEG Seizure Corpus.
- **Model Application**: Applying the trained seizure detection model to the MIT-BIH Seizure Corpus.
- **Public Accessibility**: Making data and model performance results publicly accessible for further research and development.

## Dataset Description
1. **Cuban Human Brain Mapping Project**: A dataset focused on mapping brain activity to understand various cognitive functions and disorders.
2. **Temple University EEG Seizure Corpus**: A dataset for training machine learning models in seizure detection.
3. **MIT-BIH Seizure Corpus**: A dataset used for testing and validating seizure detection algorithms and models.

## Methodology
- Utilizing the MNE Python library for EEG data processing and analysis.
- Developing a custom wrapper for simplified and standardized data parsing.
- Implementing machine learning algorithms for seizure detection, training them on the Temple University corpus, and validating on the MIT-BIH corpus.
- Ensuring reproducibility and accessibility of the data processing and analysis pipelines.

## Public Accessibility
- **Data**: Processed datasets and raw data (where permissible) will be available to the research community.
- **Models**: Trained models, along with their performance metrics, will be publicly accessible.
- **Code**: All source code used in this project will be available in this repository.




#Changelog

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
- Created project scaffold and project requirements using Poetry.
- Create Makefile to streamline lint, formatting, and test commands.
- Create abstract base classes for Cerebro and Parser objects.

