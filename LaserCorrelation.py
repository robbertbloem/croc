from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import Resources.IOMethods
import Resources.Mathematics as M
import Resources.Equations as E

reload(Resources.IOMethods)
reload(M)
reload(E)





def import_and_process(path_input, path_output, mess_array, scan_array, mess_date, pixel = 16, maxtau = 2000, debug = False):
    """
    croc.LaserCorrelation.import_and_process

    This method imports a file, calculates the correlation using two methods for a single pixel and exports it to a new file.
    
    CHANGELOG:
    20120223/RB: collected some scripts into this function
    
    INPUT:
    - path_input (string): the path where the files can be found, for example '/Volumes/.../data/'
    - path_output (string): the path where the correlation will be written, for example '/Volumes/.../analysis/'
    - mess_array (array): the base file names, for example 'correlation_T300'
    - scan_array (array): array with the file-endings, for example ['_NR1_1.bin', '_NR1_2.bin', ...]
    - mess_date (int): the day of the measurement yyyymmdd
    - pixel (int): the pixel that should be used
    - maxtau (int): input for the correlation function. The higher the number, the longer the calculation.
    - debug (BOOL, False): If true, it will only calculate 1 correlation, not all of them.
    
    OUTPUT:
    - two files with correlation data
    
    """


    if debug:
        i_len = 1
        j_len = 1
    else:
        i_len = len(mess_array)
        j_len = len(scan_array)


    for i in range(i_len):
        for j in range(j_len):

            # import data
            path_and_filename = path_input + mess_array[i] + "/" + mess_array[i] + scan_array[j] + ".bin"
            data, fringes = Resources.IOMethods.import_data_FS(path_and_filename)
            data = data[pixel,:]
            
            # fft method
            c = croc.Functions.correlation_fft(data)
            c = numpy.real(c)
            path_and_filename = path_output + mess_array[i] + scan_array[j] + "_corr_fft.bin"
            c.tofile(path_and_filename)

            # jan method
            c = croc.Functions.correlation(data, maxtau = maxtau)
            c = numpy.real(c)
            
            path_and_filename = path_output + mess_array[i] + scan_array[j] + "_corr_jan_" + str(maxtau) + ".bin"
            
            c.tofile(path_and_filename)            


        
def fit_correlation(path, mess_array, scan_array, mess_date, maxtau, A_start = [3, 10000, 1, 10], flag_write = False, flag_plot = True, debug = False):
    """
    croc.LaserCorrelation.fit_correlation
    
    This method imports the correlation data and fits it two a double exponential.
    
    CHANGELOG:
    20120223/RB: collected some scripts into this function
    
    INPUT:
    - path (string): the path to the correlation data. Note that this is the same as the path_output in the import_and_process function.
    - mess_array (array): the base file names, for example 'correlation_T300'
    - scan_array (array): array with the file-endings, for example ['_NR1_1.bin', '_NR1_2.bin', ...]
    - mess_date (int): the day of the measurement yyyymmdd
    - pixel (int): the pixel that should be used
    - maxtau (int): to determine the correct name for the file of the correlation data
    - A_start (array, 4 elements): starting guess for the fit of the correlation data
    - flag_write (BOOL, False): If True, will write a file with the fitting data
    - flag_plot (BOOL, True): If False, it will not plot the result.
    - debug (BOOL, False): If true, it will only calculate 1 correlation, not all of them.
    
    OUTPUT:
    - a plot of the correlation data using both methods and the corresponding fits.
    - a text file with the fitting data
    
    """



    if debug:
        i_len = 1
        j_len = 1
    else:
        i_len = len(mess_array)
        j_len = len(scan_array)

    string = ""
    
    for i in range(i_len):
        for j in range(j_len):
            if flag_plot:
                plt.figure()
            for k in range(2):

                if k == 0:
                    sort = "fft"
                else:
                    sort = "jan_" + str(maxtau)
                
                c = Resources.IOMethods.import_data_correlation(path, mess_array, i, scan_array, j, mess_date, sort = sort)
                
                c = c[:1000]
                
                x = numpy.arange(len(c))
                
                A = A_start
                
                A_final = M.fit(x, c, E.double_exp, A)
                
                if flag_plot:
                    plt.plot(c, ".")
                    plt.plot(E.double_exp(A_final, x))
                    plt.title(mess_array[i] + scan_array[j])
                
                s_m = mess_array[i]
                s_s = scan_array[j]
                s_p = sort
                s_a = str(numpy.round(A_final[0],2)) 
                s_t1 = str(numpy.round(A_final[1],1))
                s_b = str(numpy.round(A_final[2],2))
                s_t2 = str(numpy.round(A_final[3],1))
                
                temp_string = "{0:5} {1:6} {2:8} {3:5} {4:7} {5:5} {6:7}".format(s_m, s_s, s_p, s_a, s_t1, s_b, s_t2)
                print(temp_string)
                string += temp_string

            if flag_plot:
                plt.show()
                
    if flag_write:
        FILE = open(path + "corr_fitting.txt", "w")
        
        FILE.write(string)
        
        FILE.close()


if __name__ == "__main__": 

    mess_array = ["scan_1640_T0", "scan_1641_T0", "scan_1642_T0"]
    mess_date = 20120206
    scan_array = ["_NR1_1", "_NR2_1", "_R1_1", "_R2_1"]
    maxtau = 6000

    fit_correlation("/Volumes/public_hamm/PML3/analysis/20120206/", mess_array, scan_array, mess_date, maxtau, A_start = [3, 10000, 1, 10], flag_write = True, flag_plot = False, debug = False)


