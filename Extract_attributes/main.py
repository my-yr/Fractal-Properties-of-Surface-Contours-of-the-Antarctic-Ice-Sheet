import sys
import extract_attributes

if __name__ == '__main__':
    argv = sys.argv
    target_file=[
        argv[2], # GaplessREMA100.tif
        argv[3], # bm3_thickness.tif
        argv[4], # bm3_bed.tif
        argv[5], # RACMO_Temperature_2m_35km.tif
        argv[6]] # bedmap3_bed_roughness.tif

    name = ["surface_elevation","ice_thickness","bed_elevation","surface_temperature","bed_roughness"]
    point_file=argv[1] # '0_4000_samelong_rockcount.csv'
    aquire_it_result_file='attribute_result.csv' # "0_4000_samelong_all_test.csv"
    # calculate_it_result_file="rema_100_local_fractal_calculate_it.csv"

    extract_attributes.aquire_it('data/'+target_file,name,'data/'+point_file,'result/'+aquire_it_result_file,2)