import time
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
import fractal_dimension as frac
from numpy import *
from shapefile import Reader as ShapefileReader
import csv
from multiprocessing import Pool
from functools import partial


def single_process(i, shp):
    """
    Compute the fractal dimension of single isoline

    Parameters
    ----------
    i: int
        The order of the isoline in shp
    shp: string
        The file name of shp

    Returns
    -------
    elevation_value: int
        Elevation value of this isoline,
    re: float
        Dim of this isoline
    cheak_num: int
        The num of ruler do not go forward of this isoline,
    ruler_lens: list
        Ruler length used of this isoline
    ruler_counts: list
        Every count under every ruler of this isoline

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

    # build ruler
    ruler = frac.RulerMethod()
    ruler.load(shp, i)  # load the i isoline
    perimeter = ruler.shape.length  # get perimeter
    ruler_num = 20  # ruler num
    ruler_lens = logspace(log10(perimeter / 1000.0), log10(perimeter / 4.0), ruler_num)  # ruler length
    ruler_counts = []
    cheak_num = 0

    # for every ruler having different length
    for j1 in range(ruler_num):
        # get ruler count and cheak_value
        ruler_count_result, cheak_value = ruler.count_overall(ruler_lens[j1])
        # get the num of ruler do not go forward
        if cheak_value == 0:
            cheak_num += 1
        ruler_counts.append(ruler_count_result)
    # calcurate fractal dim
    dim = frac.fractal_dimension(ruler_lens, ruler_counts)
    return elevation_value, dim, cheak_num, ruler_lens, ruler_counts

class overall_fractal:

    def __init__(self, filepaths, process_num):
        self.filepaths = filepaths
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
            Elevation value of every isoline
        dims: float list
            Dim of every isoline
        cheak_nums: int list
            The num of ruler do not go forward of every isoline
        ruler_lens: float list
            Ruler length used of every isoline
        ruler_counts: int list
            Every count under every ruler of every isoline

        """
        #prepare box to store result
        elevation_values = []
        dims = []
        cheak_nums = []
        ruler_lens = []
        ruler_counts = []

        # get num of isoline
        ruler = frac.RulerMethod()
        ruler.load(filepath, 0)
        isoline_num = ruler.l
        del ruler

        #build processing pool
        pool = Pool(processes=process_num)
        func = partial(single_process, shp=filepath) #for more parameters
        results = pool.map(func, range(isoline_num)) #get result

        #transform turple into list
        for result in results:
            elevation_values.append(list(result)[0])
            dims.append(list(result)[1])
            cheak_nums.append(list(result)[2])
            ruler_lens.append(list(result)[3])
            ruler_counts.append(list(result)[4])

        return elevation_values, dims, cheak_nums, ruler_lens, ruler_counts

    def aquire_it(self,result_file_path1,result_file_path2,elevation_values, dims, cheak_nums, ruler_lens, ruler_counts):
        """
        Store the result in csv file

        Parameters
        ----------
        result_file_path1: string
            Name of the file (it will contain
                elevation value of every isoline,
                dim of every isoline,
                the num of ruler do not go forward of every isoline)
            will be output
        result_file_path2: string
           Name of the file (it will contain
                elevation value of every isoline,
                ruler length used of every isoline,
                every count under every ruler of every isoline)
            will be output
        ele: int list
            Elevation value of every isoline
        dim: float list
            Dim of every isoline
        cheak_num: int list
            The num of ruler do not go forward of every isoline
        length: float list
            Ruler length used of every isoline
        count: int list
            Every count under every ruler of every isoline

        Returns
        -------
        This function will not return anything, but it will generate two csv file to store the result

        """
        # store elevation_values, dims, cheak_nums
        with open(result_file_path1, 'w') as csvfile1:
            writer = csv.writer(csvfile1)
            # field name
            header = ('elevation','dim','cheak_num')
            # write field name
            writer.writerow(header)

            for i in range(len(dims)):
                row = [
                    elevation_values[i],
                    dims[i],
                    cheak_nums[i]
                ]
                writer.writerow(row)
        csvfile1.close()

        # store elevation_values, ruler_lens, ruler_counts
        with open(result_file_path2, 'w') as csvfile2:
            writer = csv.writer(csvfile2)
            # field name
            header = ('elevation','ruler_len','ruler_count')
            # write field name
            writer.writerow(header)

            for i in range(len(ruler_lens)):
                row = [
                    elevation_values[i],
                    ruler_lens[i],
                    ruler_counts[i]
                ]
                writer.writerow(row)
        csvfile2.close()

    #main function
    def run(self):
        start_time = time.time()

        # all file in filepaths will be processing
        for filepath in self.filepaths:
            # get result
            elevation_values, dims, cheak_nums, ruler_lens, ruler_counts=self.for_result('data/'+filepath,self.process_num)
            # write in csv
            self.aquire_it(
                'result/'+filepath[0:-4]+'_ele_dim_cheak'+'.csv',
                'result/'+filepath[0:-4]+'_ele_length_count'+'.csv',
                elevation_values, dims, cheak_nums, ruler_lens, ruler_counts
            )

        end_time = time.time()
        # print time used
        print (end_time - start_time)


