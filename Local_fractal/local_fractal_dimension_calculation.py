import os
import numpy as np
import math
from multiprocessing import Pool
from functools import partial
import time
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
import fractal_dimension as frac
from shapefile import Reader as ShapefileReader
import csv
import shapefile


def single_process(i, shp):
    """
    Compute the local fractal dimension of single isoline

    Parameters
    ----------
    i: int
        The order of the isoline in shp
    shp: string
        The file name of shp

    Returns
    -------
    elevation_value: int list
        Elevation value of this isoline
    ptxy: float list
        location of circle dots
    dims: float list
        dim of local lines
    local_lines: float list
        shape of local lines
    local_lens: float list
        length of local lines

    """
    # get elevation value
    shpfile = ShapefileReader(shp)
    shape_record = shpfile.shapeRecords()[i]
    fields = shpfile.fields[1:]
    field_names = [field[0] for field in fields]
    elev_index = field_names.index('ELEV')
    elevation_value = shape_record.record[elev_index]
    print elevation_value
    shpfile.close()

    # get result
    ruler = frac.RulerMethod()
    ruler.load(shp, i)  # load i isoline of shp
    target_shape = ruler.shape  # load data of i isoline
    perimeter = ruler.shape.length  # get perimeter
    dist = 50000  # constant distance 50km
    point_num = int(math.ceil(perimeter / dist))  # get num of point
    print (elevation_value, "num", perimeter, (perimeter / dist), point_num, os.getpid())
    pts, dims, local_lines, local_lens = frac.fractal_at_points(target_shape, dist, point_num)

    # get location of points
    xy = np.array(target_shape.coords[:])
    # get location of circle dots
    ptxy = np.array([p.coords[0] for p in pts])

    return {
        'elevation_value': elevation_value,
        'dims': dims,
        'ptxs': ptxy[:, 0],
        'ptys': ptxy[:, 1],
        'local_lines': local_lines,
        'local_lens': local_lens
    }


class local_fractal:
    def __init__(self, target_filename, process_num):
        self.target_filename = target_filename
        self.process_num = process_num

    def for_result(self,filepath,process_num):
        """
         Start multiprocess and pack the result

        Parameters
        ----------
        filepath: string
            File name of one shp
        process_num: int
            The num of processes

        Returns
        -------
        elevation_values: int list
            Elevation value of this isoline
        i: int
            The order of the isoline in shp
        ptxy: float list
            Location of circle dots
        dims: float list
            Dim of local lines
        local_lines: float list
            Shape of local lines
        local_lens: float list
            Length of local lines

        """
        # prepare box for result
        elevation_values=[]
        dims = []
        local_lens=[]
        ptxs = []
        ptys = []
        local_lines = []

        # get num of isoline
        ruler = frac.RulerMethod()
        ruler.load(filepath, 0)
        isoline_num = ruler.l
        del ruler



        #build processing pool
        pool = Pool(processes=process_num)
        func = partial(single_process, shp=filepath) #for more parameters
        results = pool.map(func, range(isoline_num)) #get result


        # transform result into general format
        for result in results:
            dims = np.append(dims,result['dims'])
            local_lens = np.append(local_lens,result['local_lens'])
            ptxs = np.append(ptxs, result['ptxs'])
            ptys = np.append(ptys, result['ptys'])
            local_lines=np.append(local_lines,result['local_lines'])
            for i in range(len(result['ptxs'])):
                elevation_values=np.append(elevation_values,result['elevation_value'])
        results_pack={
            'elevation_values':elevation_values,
            'dims': dims,
            'local_lens': local_lens,
            'ptxs': ptxs,
            'ptys': ptys,
            'local_lines': local_lines
        }
        return results_pack

    # write in csv
    def acquire_it(self,result,filepath): # result:the result;filepath:csv file name
        """
        Store the result in csv file

        Parameters
        ----------
        result: dict
            Contain all result

        filepath: string
            Name of the file (it will contain
                elevation value of this isoline,
                the order of the isoline in shp,
                location of circle dots,
                dim of local lines,
                shape of local lines,
                length of local lines)
            will be output

        Returns
        -------
        This function will not return anything, but it will generate a csv file to store the result

        """
        # store ele,dim,the location of points
        with open(filepath, 'w') as csvfile:
            writer = csv.writer(csvfile)
            # field name
            headers = ['elevation', 'ptx', 'pty', 'dim']
            # write field name
            writer.writerow(headers)

            for i in range(len(result['ptxs'])):
                row = [
                    result['elevation_values'][i],
                    result['ptxs'][i],
                    result['ptys'][i],
                    result['dims'][i]
                ]
                writer.writerow(row)
        csvfile.close()

    def acquire_shp(self,result,filepath):
        """
        Store the result in shp file

        Parameters
        ----------
        result: dict
            Contain all result
        filepath: string
            Name of the file (it will contain
                elevation value of this isoline,
                the order of the isoline in shp,
                location of circle dots,
                dim of local lines,
                shape of local lines,
                length of local lines)
            will be output

        Returns
        -------
        This function will not return anything, but it will generate a shp file to store the result

        """
        write_shp = shapefile.Writer(filepath, shapeType=shapefile.POLYLINE)

        # write field name
        write_shp.field("dim", "F", 10, 5)
        write_shp.field("ptx", "F", 18,3)
        write_shp.field("pty", "F", 18,3)
        write_shp.field("elevation", "N", 10)
        write_shp.field("local_len", "F", 18,3)

        # store result
        for i in range(len(result['local_lines'])):
            write_shp.line([result['local_lines'][i]])
            write_shp.record( result['dims'][i], result['ptxs'][i], result['ptys'][i], result['elevation_values'][i], result['local_lens'][i])
        write_shp.close()

    # main function
    def run(self):

        # input your target file
        result_filename='result/'+self.target_filename[0:-4]+'_result'

        start1=time.time()

        # get result
        all_result=self.for_result('data/'+self.target_filename,self.process_num)
        # store result in csv file
        self.acquire_it(all_result, result_filename)
        # store result in shp file
        self.acquire_shp(all_result,result_filename)

        end1=time.time()
        # print time used
        print end1-start1
