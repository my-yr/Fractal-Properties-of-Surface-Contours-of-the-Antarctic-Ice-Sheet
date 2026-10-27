# Fractal Properties of Contours of the Antarctic Ice Sheet Topographic Surface

## Introduction

This project is the accompanying code for the paper *Fractal Properties of Contours of the Antarctic Ice Sheet Topographic Surface*. It mainly includes data download, contour extraction, overall fractal computation, local fractal computation, and attribute extraction. To make the code serve different audiences, we designed it in a modular way. You can select different modules according to your purpose, and for each module we provide the data, results, and run commands used in the paper as examples. The related article is available at: (paper link to be added)

## Table of Contents

- [Introduction](#introduction)
- [Project Structure](#project-structure)
- [Data Download](#data-download)
- [Contour Extraction](#contour-extraction)
- [Fractal Computation](#fractal-computation)
- [Overall Fractal Computation](#overall-fractal-computation)
- [Local Fractal Computation](#local-fractal-computation)
- [Attribute Extraction](#attribute-extraction)
- [Notes](#notes)
- [Contact](#contact)

## Project Structure

This project consists of six main components:

1. Data download
2. Contour extraction
3. Fractal computation
4. Overall fractal computation
5. Local fractal computation
6. Attribute extraction

## Data Download

- DEM data Gapless-REMA100: <https://figshare.com/articles/dataset/Gapless-REMA100/19122212>
- Temperature data RACMO_Temperature_2m_35km: <https://npolar.no/en/quantarctica>. After downloading the Quantarctica 3 package, go to the `Atmosphere/RACMO` directory to find the raster data of RACMO_Temperature_2m_35km.
- The Bedmap3 ice thickness, bed elevation, and exposed bedrock mask raster data can all be downloaded from [UK Polar Data Centre - BEDMAP3 - Ice thickness, bed and surface elevation for Antarctica - gridding products](https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=2d0e4791-8e20-46a3-80e4-f5f6716025d2).
- For details on the Antarctic drainage basin boundary data, see [MEaSUREs Antarctic Boundaries for IPY 2007-2009 from Satellite Radar, Version 2 | National Snow and Ice Data Center](https://nsidc.org/data/nsidc-0709/versions/2), which provides multiple download methods.

## Contour Extraction

This module is located in the `Extract_isoline` folder on the main branch.

We extracted contour lines at 100 m intervals from the Antarctic DEM Gapless-REMA100. This step is relatively simple, so we directly provide the shapefile of the complete extracted contours and the shapefile of the selected contours (in the `Extract_isoline` folder on the main branch).

## Fractal Computation

This module is the `fractal_dimension.py` file on the main branch. The core idea is to compute the fractal dimension of contour lines using the ruler method.

- `BaseFractalDimension` class: loads and stores the data of linear fractal objects, such as their shapes;
- `RulerMethod` class: computes the fractal dimension of linear fractal objects using the ruler method.

## Overall Fractal Computation

This module is located in the `Overall_fractal` folder on the main branch. The core idea is to use multiple processes to compute the fractal dimension of each contour line.

The code includes `overall_fractal_dimension_calculation.py` and `main.py`.

- `overall_fractal_dimension_calculation.py` defines the `single_process` function, a single process for computing the overall fractal dimension of one contour line; it also provides the class `overall_fractal`, which launches multiple processes that call the `single_process` function simultaneously to compute the overall fractal dimension of multiple contour lines.
- `main.py` calls `overall_fractal_dimension_calculation.py` and extracts parameters from the command line.

We provide the data used in the paper (in the `data` folder), the results (in the `result` folder), and the corresponding run commands in `example.txt` in the same directory:

```bash
conda activate fractal
python main.py 4 rema_100.shp BASIN1_rema_100.shp BASIN2_rema_100.shp BASIN3_rema_100.shp BASIN5_rema_100.shp BASIN6_rema_100.shp BASIN7_rema_100.shp
```

## Local Fractal Computation

This module is located in the `Local_fractal` folder on the main branch. The core idea is to use multiple processes to split each contour line into equal-length segments, and then compute the local fractal dimension of each resulting segment.

The code includes `local_fractal_dimension_calculation.py` and `main.py`.

- `local_fractal_dimension_calculation.py` defines the `single_process` function, a single process for computing the local fractal dimension of one contour line; it also provides the class `local_fractal`, which launches multiple processes that call the `single_process` function simultaneously to compute the local fractal dimension of multiple contour lines.
- `main.py` calls `local_fractal_dimension_calculation.py` and extracts parameters from the command line.

We provide the data used in the paper (in the `data` folder), the results (in the `result` folder), and the corresponding run commands in `example.txt` in the same directory:

```bash
conda activate fractal
python main.py 4 rema_100.shp
```

## Attribute Extraction

This module is located in the `Extract_attributes` folder on the main branch. The core idea is to use the `gdal` library to perform a GIS overlay analysis between the center point of each local segment and the raster of each attribute, thereby obtaining the attributes of each local segment.

The code includes `extract_attributes.py` and `main.py`.

- `extract_attributes.py` defines the `read_dem_at_point_gdal` function (reads the attribute value of raster data at a specified point with GDAL), the `csv_based_extract` function (reads the csv file of the fractal computation results), and the `aquire_it` function (extracts the attribute values from each raster and writes them into the resulting csv, including surface_elevation, ice_thickness, bed_elevation, surface_temperature, and bed_roughness).
- `main.py` calls `extract_attributes.py` and extracts parameters from the command line.

We provide the data used in the paper (in the `data` folder), the results (in the `result` folder), and the corresponding run commands in `example.txt` in the same directory:

```bash
conda activate fractal
python main.py 0_4000_samelong_rockcount.csv GaplessREMA100.tif bm3_thickness.tif bm3_bed.tif RACMO_Temperature_2m_35km.tif bedmap3_bed_roughness.tif
```

## Notes

The scripts are written in Python.

Recommended to use Anaconda's virtual environment.

Library `shapefile`, `shapely`, `numpy`, `scipy` are needed.

Python version 2.7 is recommended.

## Contact

If you have any questions or suggestions, or would like to collaborate, please open an issue or contact the maintainer of this repository.
