from osgeo import gdal
import numpy as np
import csv
# import calculate_it as ci

# get information of local point
def read_dem_at_point_gdal(dem_path,x,y, band=1, nodata=np.nan):

    gdal.UseExceptions()
    ds = gdal.Open(dem_path, gdal.GA_ReadOnly)
    band = ds.GetRasterBand(band)
    gt = ds.GetGeoTransform()  # (x0, dx, 0, y0, 0, dy)
    x0, dx, _, y0, _, dy = gt
    ncols = ds.RasterXSize
    nrows = ds.RasterYSize


    col = list(int(round((x1 - x0) / dx)) for x1 in x)
    row = list(int(round((y1 - y0) / dy)) for y1 in y)

    elev=[]
    for i in range(len(col)):

        data = band.ReadAsArray(col[i], row[i], 1, 1)

        elev.append(float(data[0, 0]) )
        if elev[i] == band.GetNoDataValue():
            elev[i] = nodata

    return elev
    ds = None

# read information from csv
def csv_based_extract(file_path,mode):

    ele=[]
    ptx = []
    pty = []
    dims=[]
    count=[]
    perimeter=[]

    if mode==1:
        with open(file_path, 'r') as f:
            reader = csv.reader(f)

            i=0
            for row in reader:
                if i==0:
                    i = i + 1
                    continue
                if i%2==0:
                    rowk=list(map(float, row))
                    ele.append(rowk[0])
                    ptx.append(float(rowk[1]))
                    pty.append(float(rowk[2]))
                    dims.append(float(rowk[3]))

                i=i+1
        f.close()
        result = ele,ptx, pty,dims

    elif mode==2:
        with open(file_path, 'r') as f:
            reader = csv.reader(f)

            i = 0
            for row in reader:
                if i == 0:
                    i = i + 1
                    continue


                rowk = list(map(float, row))
                ele.append(rowk[6])
                ptx.append(float(rowk[4]))
                pty.append(float(rowk[5]))
                dims.append(float(rowk[3]))
                count.append(float(rowk[1]))
                perimeter.append(float(rowk[7]))

                i = i + 1
        f.close()

        result = ptx, pty, ele,dims,count,perimeter
    return result

# generate result csv
def aquire_it(target_file_path,name,origin_file_path,result_file_path,mode):
    acquire_value=[]
    if mode==1:
        ele,ptx ,pty,dims=csv_based_extract(origin_file_path,mode)
    elif mode==2:
        ptx, pty, ele, dims, count, perimeter=csv_based_extract(origin_file_path,mode)
    for i in range(len(target_file_path)):
        acquire_value[i]=read_dem_at_point_gdal(target_file_path[i],ptx, pty)

    with open(origin_file_path, mode='r') as infile,\
        open(result_file_path, 'w') as csvfile:
        reader = csv.reader(infile)
        writer = csv.writer(csvfile)

        header = (next(reader))
        for j in range(len(name)):
            header.append(name[j])

        writer.writerow(header)

        for i in range(len(ptx)):
            row = [
                ptx[i],
                pty[i],
                ele[i],
                dims[i],
                count[i],
                perimeter[i],
                acquire_value[0][i],
                acquire_value[1][i],
                acquire_value[2][i],
                acquire_value[3][i],
                acquire_value[4][i]
            ]
            writer.writerow(row)
    infile.close()
    csvfile.close()
