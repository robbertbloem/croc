from __future__ import print_function
from __future__ import division

import time
import inspect
import copy

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import croc.Resources.DataClasses as DC
import croc.Plotting.Functions as PFU
import croc.Debug as DBG

reload(PFU)

class Figure(DC.ClassTools):
    
    def __init__(self):
        
        # arrays for the plots
        self.plot_objects = []
        self.subplot_position = []
        self.subplot_dim = False

        # some defaults - as per matplotlib
        self.fig_size = False
        self.dpi = False

        self.axes_attr = []
        self.subplots_attr = []
        
        self.hide_labels_subplots = False

    def add_plot_object(self, obj, pos = 1):
        
        self.plot_objects.append(obj)
        self.subplot_position.append(pos)
        self.axes_attr.append(False)

    def create_special_axes_instance(self, index):
        self.axes_attr[index] = plot_object()
        


    def make_axes_object(self, fig, rows, columns, index):
        
        # make new axes object
        if self.plot_objects[index].second_y_scale:
            ax_s = fig.add_subplot(rows, columns, self.subplot_position[index])
            ax = ax_s.twinx()
        elif self.plot_objects[index].second_x_scale:
            ax_s = fig.add_subplot(rows, columns, self.subplot_position[index])
            ax = ax_s.twiny()
        else:
            ax = fig.add_subplot(rows, columns, self.subplot_position[index])
        
        return ax
        

    def add_axes_attributes(self, obj, ax):
        
        # determine color
        if obj.x_axes_color: 
            x_axes_color = obj.x_axes_color
        else:
            x_axes_color = "k"
        if obj.y_axes_color: 
            y_axes_color = obj.y_axes_color
        else:
            y_axes_color = "k"        
        
        # labels
        if obj.x_label:
            ax.set_xlabel(obj.x_label, color = x_axes_color)
        if obj.y_label:
            ax.set_ylabel(obj.y_label, color = y_axes_color)

        # range
        if obj.x_range:
            ax.set_xlim(obj.x_range[0], obj.x_range[1])
        if obj.y_range:
            ax.set_ylim(obj.y_range[0], obj.y_range[1])
            
        # hide labels for ticks
        if obj.x_tick_label_hide:
            tick_labels = [""] * len(ax.get_xticklabels())
            ax.set_xticklabels(tick_labels)
        if obj.y_tick_label_hide:
            tick_labels = [""] * len(ax.get_yticklabels())
            ax.set_yticklabels(tick_labels)
        
        # color labels and ticks
        if obj.x_axes_color:   
            for tl in ax.get_xticklabels():
                tl.set_color(x_axes_color)
        if obj.y_axes_color:   
            for tl in ax.get_yticklabels():
                tl.set_color(y_axes_color)
            
        # title
        if obj.title:
            ax.set_title(obj.title)

    def add_axes_attributes_old(self, obj, ax):
        
        # determine color
        if self.plot_objects[index].x_axes_color: 
            x_axes_color = self.plot_objects[index].x_axes_color
        else:
            x_axes_color = "k"
        if self.plot_objects[index].y_axes_color: 
            y_axes_color = self.plot_objects[index].y_axes_color
        else:
            y_axes_color = "k"        
        
        # labels
        if self.plot_objects[index].x_label:
            ax.set_xlabel(self.plot_objects[index].x_label, color = x_axes_color)
        if self.plot_objects[index].y_label:
            ax.set_ylabel(self.plot_objects[index].y_label, color = y_axes_color)

        # range
        if self.plot_objects[index].x_range:
            ax.set_xlim(self.plot_objects[index].x_range[0], self.plot_objects[index].x_range[1])
        if self.plot_objects[index].y_range:
            ax.set_ylim(self.plot_objects[index].y_range[0], self.plot_objects[index].y_range[1])
            
        # hide labels for ticks
        if self.plot_objects[index].x_tick_label_hide:
            tick_labels = [""] * len(ax.get_xticklabels())
            ax.set_xticklabels(tick_labels)
        if self.plot_objects[index].y_tick_label_hide:
            tick_labels = [""] * len(ax.get_yticklabels())
            ax.set_yticklabels(tick_labels)
        
        # color labels and ticks
        if self.plot_objects[index].x_axes_color:   
            for tl in ax.get_xticklabels():
                tl.set_color(x_axes_color)
        if self.plot_objects[index].y_axes_color:   
            for tl in ax.get_yticklabels():
                tl.set_color(y_axes_color)
            
        # title
        if self.plot_objects[index].title:
            ax.set_title(self.plot_objects[index].title)


    def make_figure(self):

        # init figure
        fig = plt.figure()
        if self.fig_size:
            fig.set_size_inches(self.fig_size, forward=True)
        if self.dpi:
            fig.set_dpi = self.dpi

        # determine subplots
        n_subplots = numpy.max(self.subplot_position)
        
        if self.subplot_dim:
            rows = self.subplot_rc[0]
            columns = self.subplot_rc[1]
        else:
            rows, columns = PFU.find_subplot_size(n_subplots)
        rows = int(rows)
        columns = int(columns)
        
        print(rows, columns)
        
        n_obj = len(self.plot_objects)
        
        ax = [0] * n_obj
        
        for i in range(n_obj):
            ax[i] = self.make_axes_object(fig, rows, columns, i)
        
            self.plot_objects[i].plot(ax[i])
            
            if self.hide_labels_subplots :
                if (self.subplot_position[i] - 1) % columns != 0:
                    self.plot_objects[i].y_tick_label_hide = True  
                if (self.subplot_position[i] - (rows - 1) * columns) <= 0:
                    self.plot_objects[i].x_tick_label_hide = True    
            
                
            
            self.add_axes_attributes(self.plot_objects[i], ax[i])

        for i in range(n_obj):
            
            if self.axes_attr[i]:
                print(i, self.axes_attr[i])
                
                self.add_axes_attributes(self.axes_attr[i], ax[i])  
        
        plt.show()
        



class plot_object(DC.ClassTools):

    def __init__(self):
        
        # axes 
        self.second_x_scale = False
        self.second_y_scale = False
        
        self.x_range = False
        self.y_range = False 
        self.z_range = -1

        # titles
        self.title = False
        
        self.x_label = False
        self.y_label = False
        
        # ticks
        self.x_tick_label_hide = False
        self.y_tick_label_hide = False
        
        # color of both ticks and labels
        self.x_axes_color = False
        self.y_axes_color = False


class line_plot(plot_object):
    
    def __init__(self):
    
        plot_object.__init__(self)

        # axes and data
        self.x_axis = []
        self.data = False

        self.color = False
        
        self.line_width = False
        
        self.line_style = ""
        
        self.markersize = False

    
    def plot(self, obj_ax):
        
        obj_ax.plot(self.x_axis, self.data, self.line_style)
        
        lines = obj_ax.get_lines()
        
        if self.color:
            lines[-1].set_color(self.color)
        if self.line_width:
            lines[-1].set_linewidth(self.line_width)
        if self.markersize:
            lines[-1].set_markersize(self.markersize)







     
class contour_plot(plot_object):
    
    def __init__(self):

        plot_object.__init__(self)

        # axes and data
        self.x_axis = []
        self.y_axis = []
        self.z_axis = []  
        self.data = False

        self.filled = True
        self.filled_map = PFU.rwb_map()
        
        self.lines = True
        self.lines_color = False
        self.lines_map = False
        self.line_width = False
        
        self.contour_levels = False # the actual levels
        self.n_contours = 21
        

    def plot(self, obj_ax):
    
        if self.contour_levels:
            V = self.contour_levels
        else:
            V = PFU.make_contours_2d(self.data, zlimit = self.z_range, contours = self.n_contours)
    
        if self.filled:
            obj_ax.contourf(self.x_axis, self.y_axis, self.data, V, cmap = self.filled_map)
            if self.lines:
                obj_ax.contour(self.x_axis, self.y_axis, self.data, V, colors = "k", linestyles = "solid")            

        
        elif self.lines:
            if self.lines_color:
                obj_ax.contour(self.x_axis, self.y_axis, self.data, V, colors = self.lines_color)
            elif self.lines_map:
                obj_ax.contour(self.x_axis, self.y_axis, self.data, V, cmap = self.lines_map)
            else:
                obj_ax.contour(self.x_axis, self.y_axis, self.data, V)
                
        
     
        
        
        



























