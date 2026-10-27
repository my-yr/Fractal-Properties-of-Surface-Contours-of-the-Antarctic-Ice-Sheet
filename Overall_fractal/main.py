import overall_fractal_dimension_calculation as ofdc
import sys

# main function
if __name__ == '__main__':
    argv = sys.argv
    process_num = int(argv[1])
    files=[]

    for j,ar in enumerate(argv[2:]):
        files.append(ar)

    test_overall=ofdc.overall_fractal(files,process_num)
    test_overall.run()



