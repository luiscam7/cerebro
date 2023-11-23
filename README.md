# EEG Data Analysis and Seizure Detection Project

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

## [0.2.0] - 2023-11-22
### Added
- Created EdfParser base class.
- Developed CHBMP parser that inherits from the EdfParser class and reconfigures the Cuban Human Brain Mapping Project's 10-10 system to 10-20.
- Added notebook folder for exploratory data analysis.




## [0.1.0] - 2023-11-22
### Added
- Created project scaffold and project requirements using Poetry.
- Create Makefile to streamline lint, formatting, and test commands.
- Create abstract base classes for Cerebro and Parser objects.

