from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import Resources.IOMethods
import Resources.Mathematics as M
import Resources.Equations as E

import croc.Functions

reload(Resources.IOMethods)
reload(M)
reload(E)













def import_and_process(path_input, path_output, mess_array, scan_array, mess_date, pixel = 16, maxtau = 2000, debug = False):

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


        
def fit_correlation(path, mess_array, scan_array, mess_date, maxtau, A_start = [3, 10000, 1, 10], debug = False):

    if debug:
        i_len = 1
        j_len = 1
    else:
        i_len = len(mess_array)
        j_len = len(scan_array)

    string = ""
    
    for i in range(i_len):
        for j in range(j_len):
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
                
                plt.plot(c, ".")
                plt.plot(E.double_exp(A_final, x))
                plt.title(str(i) + " " + str(j) + " " + sort)
                
                temp_string = str(i) + " " + str(j) + " " + sort + "\ta: " + str(numpy.round(A_final[0],2)) + "\tt1: " + str(numpy.round(A_final[1],1)) + "\tb: " + str(numpy.round(A_final[2],2)) + "  \tt2: " + str(numpy.round(A_final[3],1)) + "\n"
                print(temp_string)
                string += temp_string
    
            plt.show()

