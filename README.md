# Collections Generator
> Collections Generator is a desktop app with a goal of making the process of creating new product collections fast, easy and flexible.

## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Screenshots](#screenshots)
* [Setup](#setup)
* [Usage](#usage)
* [Project Status](#project-status)
* [Room for Improvement](#room-for-improvement)
* [Acknowledgements](#acknowledgements)


## General Information
- Collection is defined as a set of products, which are technically just unique numbers - all are fictional.
- This is my re-done code, since majority of app design and functions was created fully by me during time I was employed at Shopee. App is written in Python with a more modern CustomTkinter UI. Data is coming and going in form of .csv files, and is manipulated by Pandas' dataframes.
- The problem that created a need for this project was how large datasets for collection creation were, > 100k products with multiple columns of information. That caused manual operation in Excel to be really slow, inefficient and error prone. Also, differences in formats of source and CMS system upload files were creating additional workload. So seeing how easy it was for Python to handle such huge files I've decided to create an app to bring a supporting tool for team members and myself, that was simple to start using, with enough functionalities and exponential overall collection creation time improvements.
- Since original app was pretty much tailored-made for a specific use case, within internal company processes, I won't be going in-depth on functionalities, restrictions etc., because I'd re-done the code to with showcasing my skills in mind. For the real world scenario, for the original app, a documentation, training video and in-person training was created.


## Technologies Used
- Python 3.9.13
- CustomTkinter 5.1.2


## Features
All features focus around applying various criteria to a data source. They are as following:
- source file and additional input selection
- sorting by "ADO" and "Rating"
- filtering by category ids, clusters (i.e. Fashion or Electronics), price points
- limiting size of to be generated collection
- setting ratio of local to offshore products, which means e.g. putting first 3 local products, then 2 offshore and continuing that order
- generating ready to upload file into fictional CMS system with just 3 columns
- generating additional file, along with upload file, with all columns provided by data source, but adjusted to all criteria
- removing products with a 0 in 'Stock' column, so sold-out products
- quick criteria clearing for user convenience
- app theme selection - Light, Dark or System


## Screenshots
> Screenshot of user interface in light theme.

![image](https://user-images.githubusercontent.com/31664490/223411973-15482240-2866-4610-b22c-6f05b209aee7.png)


## Setup
Setup is simple, it doesn't require Python etc. installed or admin rights to run. Please download [.zip archive](https://github.com/dberinger/collections-generator/releases/download/production-v1.0.0/Collections.Generator.v.1.0.zip). After unpacking, just open `Collections Generator v. 1.0.exe`.


## Usage
Since for the re-done version of the app all data and the CMS system are fictional, there isn't much actual use for it, but regardless this project is fully functional, so one can create new collections.
1. Select a data source from 'CMS' - [cms_5000_dummy_data.csv](https://github.com/dberinger/collections-generator/files/10908946/cms_5000_dummy_data.csv) or 'Bank' - 
[bank_250000_dummy_data.csv](https://github.com/dberinger/collections-generator/files/10908954/bank_250000_dummy_data.csv) using **Select source** button.
2. Apply whatever criteria you want.
3. (Optionally) add additional input by **+Input** button and just copy-pasting non-empty contents of a file like this [extra_50_dummy_data.csv](https://github.com/dberinger/collections-generator/files/10909015/extra_50_dummy_data.csv).
4. Click **Create** to generate upload file and optionally check **Include full file?** checkbox to generate two files.


## Project Status
Project is: _no longer being worked on_. There is no use case for this project anymore.


## Room for Improvement
I had some additional ideas for this app in mind. I would've liked to had added:
- Custom sorting
- Mass/bulk generation for multiple collections at once


## Acknowledgements
- UI was created, with thanks, using [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).
