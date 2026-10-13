# 南极冰盖地形表面等高线的分形属性

## 简介

本项目是论文《南极冰盖地形表面等高线的分形属性》的附属代码。主要包括了数据下载、等高线提取、整体分形计算、局部分形计算和局部属性提取。为了使代码服务不同的人群，我们对代码进行了模块化设计。你可以根据你的目的选用不同的模块，我们对每个模块提供了论文中的数据与结果作为示例。相关文章位于：（待补充论文链接）

## 目录

- [简介](#简介)
- [项目结构](#项目结构)
- [数据下载](#数据下载)
- [等高线提取](#等高线提取)
- [分形计算](#分形计算)
- [整体分形计算](#整体分形计算)
- [局部分形计算](#局部分形计算)
- [提取属性](#提取属性)
- [注释](#注释)
- [联系方式](#联系方式)

## 项目结构

该项目分为六个主要组成部分：

1. 数据下载
2. 等高线提取
3. 分形计算
4. 整体分形计算
5. 局部分形计算
6. 提取属性

## 数据下载

- DEM 数据 Gapless-REMA100 的下载地址：<https://figshare.com/articles/dataset/Gapless-REMA100/19122212>
- 气温数据 RACMO_Temperature_2m_35km 的下载地址：<https://npolar.no/en/quantarctica>，把 Quantarctica 3 包下载下来后找到目录 `Atmosphere/RACMO` 即可找到 RACMO_Temperature_2m_35km 的栅格数据。
- Bedmap3 的冰厚、基岩高程和裸岩掩膜的栅格数据均在网址 [UK Polar Data Centre - BEDMAP3 - Ice thickness, bed and surface elevation for Antarctica - gridding products](https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=2d0e4791-8e20-46a3-80e4-f5f6716025d2) 上下载。
- 南极的流域边界数据的详情见网址 [MEaSUREs Antarctic Boundaries for IPY 2007-2009 from Satellite Radar, Version 2 | National Snow and Ice Data Center](https://nsidc.org/data/nsidc-0709/versions/2)，它提供了多种下载方式。

## 等高线提取

该模块位于 main 分支的 `Extract_isoline` 文件夹下。

我们在南极 DEM 数据 Gapless-REMA100 上按照 100 m 的间隔提取等高线，这一步较为简单，我们直接提供了提取出来的完整等高线的 shapefile 文件和经过挑选后的等高线的 shapefile 文件（在 main 分支的 `Extract_isoline` 文件夹下）。

## 分形计算

该模块是 main 分支的 `fractal_dim_mf_for_both_make.py` 文件。

- `BaseFractalDimension` 类：用于加载和储存线状分形对象的数据，如形状等；
- `RulerMethod` 类：用作分形维数的计算。

## 整体分形计算

该模块位于 main 分支的 `Overall_fractal` 文件夹下。

代码包括了 `exetest_pro_time_github.py` 和 `main.py`。

- `exetest_pro_time_github.py` 中定义了用于计算单条等高线整体分形的单个进程 `single_process` 函数；并提供了类 `overall_fractal` 用于开启多个进程同时调用函数 `single_process` 对多条等高线进行整体分形计算。
- `main.py` 用于调用 `exetest_pro_time_github.py` 和从命令行中提取参数。

我们提供了论文中的数据（位于 `data` 文件夹）、结果（位于 `result` 文件夹）并在同目录下的 `example.txt` 中提供了相应的运行命令：

```bash
conda activate fractal
python main.py 4 rema_100.shp BASIN1_rema_100.shp BASIN2_rema_100.shp BASIN3_rema_100.shp BASIN5_rema_100.shp BASIN6_rema_100.shp BASIN7_rema_100.shp
```

## 局部分形计算

该模块位于 main 分支的 `Local_fractal` 文件夹下。

代码包括了 `exetest_local_pro_time_github.py` 和 `main.py`。

- `exetest_local_pro_time_github.py` 中定义了用于计算单条等高线局部分形的单个进程 `single_process` 函数；并提供了类 `local_fractal` 用于开启多个进程同时调用函数 `single_process` 对多条等高线进行局部分形计算。
- `main.py` 用于调用 `exetest_local_pro_time_github.py` 和从命令行中提取参数。

我们提供了论文中的数据（位于 `data` 文件夹）、结果（位于 `result` 文件夹）并在同目录下的 `example.txt` 中提供了相应的运行命令：

```bash
conda activate fractal
python main.py 4 rema_100.shp
```

## 提取属性

该模块位于 main 分支的 `Extract_attributes` 文件夹下。

代码包括了 `acquire_it.py` 和 `main.py`。

- `acquire_it.py` 中定义了 `read_dem_at_point_gdal` 函数（用 GDAL 读取栅格数据在指定点处的属性值）、`csv_based_extract` 函数（读取分形计算结果的 csv 文件）和 `aquire_it` 函数（把各栅格的属性值提取出来并写入结果 csv，包括 surface_elevation、ice_thickness、bed_elevation、surface_temperature 和 bed_roughness）。
- `main.py` 用于调用 `acquire_it.py` 和从命令行中提取参数。

我们提供了论文中的数据（位于 `data` 文件夹）、结果（位于 `result` 文件夹）并在同目录下的 `example.txt` 中提供了相应的运行命令：

```bash
conda activate fractal
python main.py 0_4000_samelong_rockcount.csv GaplessREMA100.tif bm3_thickness.tif bm3_bed.tif RACMO_Temperature_2m_35km.tif bedmap3_bed_roughness.tif
```

## 注释

脚本用 Python 编写。

建议使用 Python 版本 2.7。

## 联系方式

如果您有任何问题、建议或希望合作，请发起问题或联系本仓库的维护者。
