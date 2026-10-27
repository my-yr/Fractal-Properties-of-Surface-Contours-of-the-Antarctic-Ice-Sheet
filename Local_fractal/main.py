import local_fractal_dimension_calculation as lfdc
import sys



if __name__ == '__main__':
    argv = sys.argv
    process_num = int(argv[1])
    filepath_local = argv[2]


    test_local=lfdc.local_fractal(argv[2],process_num)
    test_local.run()





