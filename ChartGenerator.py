from matplotlib import pyplot as plt
from matplotlib.ticker import PercentFormatter
import scipy.stats as stats
import numpy as np, inspect, time

class PlotGenerator: 
    def __init__(self,height=2, width=2):
        """ This function initializes the PlotGenerator class.
            Args:
                axs: Axis object
                rows: Number of rows in the plot
                cols: Number of columns in the plot
                height: Height of the plot
                width: Width of the plot
        """
        # assert (axes is not None) and (create_new_axs is True), "You cannot both pass axs and create_new_axs=True"
        self.height = height
        self.width = width


        self.__setup__()
        # Create a list with different colors for the plots
        self.colors = [
            "#3d3f41",  # Obsidian
            "blue",  # Mauve
            "#3f4145",  # Graphite
            "#6a514e",  # Rust
            "#5a4f52",  # Plum
            "red",  # Moss
            "#5c5655",  # Chestnut
            "#534e4d",  # Ash
            "#3f4a4e"   # Deep Teal
        ]
        self.trendline_colors = [
            "grey",  # Obsidian
            "black",  # Mauve
        ]


    def __setup__(self,):
        plt.rcParams['axes.spines.top'] = False
        plt.rcParams['axes.spines.right'] = True
        plt.rcParams['font.family'] = 'Courier New'
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['figure.dpi'] = 200
        

            
    def lineplot(self,df=None, x=None, y=None, label=None, 
                 xlabel=None, ylabel=None, title=None,
                 color_int=0, ax=None,width=15, height=5):
        """ This function creates a line plot of the specified x and y values.
            Args:
                df: Dataframe 
                x: Column name of the x-axis or np.array of x-values
                y: Column name of the y-axis or np.array of y-values
                label: Label of the plot
                xlabel: Label of the x-axis
                ylabel: Label of the y-axis
                title: Title of the plot
                color_int: Integer which determines the color of the plot
                ax: Axis of the plot
                width: Width of the plot
                height: Height of the plot
            Returns:
                Line plot """
        if ax is None:
            fig, ax = plt.subplots(figsize=(width,height))
        # Plot the x and y values
        if df is not None:
            x = df[x]
            y = df[y]
        # plot the data
        ax.plot(x,y,self.colors[color_int],label=label)
        # set title
        ax.set_title(title)
        # set x and y labels
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        # add legend
        ax.legend()
        return ax
    
    def scatterplot(self,x,y, df=None,title=None,xlabel=None,ylabel=None, label=None, 
                    color=0, annotate=False, axs=None, trendline=None,name=None, percentage=False, return_ax=False,
                    **params_dict):
        """ This function creates a scatter plot of the specified x and y values.
            Args:
                df: dataframe
                x: column name for x-axis
                y: column name for y-axis
                title: title of the plot
                xlabel: label of the x-axis
                ylabel: label of the y-axis
                label: label of the plot
                color: color of the plot
                annotate: boolean for whether to annotate the plot
                ax: axis object
            Returns:
                Scatter plot"""
        self.axs = axs
        # Unfolds all the arguments and be accessed as instance variables
        self.__unfold_args__()
        # Create the plot. can be accessed as self.fig and self.axs
        self.__create_fig_ax__()
        # If x and y are specified as column names, they are converted to np.arrays
        self.__remove_df__()
        # Adjust the length of the x and y values to be the same length
        self.__adjust_length__()
        #
        self.__percentage__(percentage)

        # Plot the x and y values
        for i in range(len(self.y)):
            self.axs.scatter(self.x,self.y[i],color=self.colors[i],**params_dict)
        
        # Determine the trendline
        if self.trendline != None:
            for i in range(len(self.y)):
                self.x_pred, self.y_pred, rg_text= self._trendline(method=self.trendline,x=self.x,y=self.y[i]).__main__()
                self.axs.plot(self.x_pred,self.y_pred,color = self.colors[i],linestyle='-.')
            #Annotate only if one y value is passed
            if len(self.y) == 1:
                props = dict(boxstyle='round', facecolor='white', alpha=0.5)
                self.axs.annotate(rg_text,xy=(0.01,1),xycoords='axes fraction',ha='left',va='top',bbox=props)
        # Create the labels, title, etc.
        self.axs = self.__labels_etc__(self.axs)
        #
        self.__twinx__()

        if return_ax == True:
            plt.close(self.axs.figure)

        return self.axs
    def __twinx__(self):
        y1_lim = self.axs.get_ylim()
        print(y1_lim)
        self.axs2 = self.axs.twinx()
        self.axs2.set_ylim(y1_lim)
        y1_axes_format = self.axs.yaxis.get_major_formatter()
        self.axs2.yaxis.set_major_formatter(y1_axes_format)

    def __percentage__(self,percentage):
        if percentage == True:
            for i in range(0,len(self.y)):
                self.y[i] = self.y[i]*100
            self.axs.yaxis.set_major_formatter(PercentFormatter())
        else: 
            pass
    
    def __adjust_length__(self):
        """
        This function adjusts the length of the x and y values to be the same length.
        """
        self.x = self.x[~np.isnan(self.x)]
        for i in range(len(self.y)):
            self.y[i] = self.y[i][~np.isnan(self.y[i])]
        min_y_length = min([len(i) for i in self.y])
        max_y_length = min([len(i) for i in self.y])

        if len(self.x) > min_y_length:
            self.x = self.x[:min_y_length]

        elif len(self.x) < max_y_length:
            for i in range(len(self.y)):
                self.y[i] = self.y[i][:len(self.x)]

    def __create_fig_ax__(self, rows=1, cols=1):   
        if self.axs is None:     
            self.fig, self.axs = plt.subplots(rows, cols, figsize=(self.width, self.height))
        
    
    def __unfold_args__(self,):
        frame = inspect.currentframe().f_back
        args, _, _, values = inspect.getargvalues(frame)
        # Set the instance variables dynamically
        for arg in args:
            if arg != 'self':
                setattr(self, arg, values[arg])
    
    def __remove_df__(self,):
        df, x, y = self.df, self.x, self.y
        self.no_y_label, self.no_label = ['' for i in range(len(y))] , ['' for i in range(len(y))]
        
        # Determine if y is a list or not
        if isinstance(y,list):
            self.y_list_bool = True
        else:
            self.y_list_bool = False

        if self.df is not None:
            self.no_x_label = self.x
            x = self.df[self.x].to_numpy()
            if self.y_list_bool:
                for i in range(len(y)):
                    self.no_y_label[i] = self.y[i]
                    self.no_label[i] = self.y[i]
                    y[i] = self.df[y[i]].to_numpy()
            else:
                y = [self.df[self.y].to_numpy()]
                self.no_y_label = [self.y]
                self.no_label = [self.y]
        else: 
            x = self.x
            y = self.x
            self.no_x_label = ''
            self.no_label = None
            if self.y_list_bool:
                self.no_y_label = ['value']*len(y)
            else: 
                self.no_y_label = ['value']

        self.x, self.y = x, y


    def __labels_etc__(self,ax):
        xlabel, ylabel, title = self.xlabel, self.ylabel, self.title
        if isinstance(ax, list):
            ax = ax[0]

        if xlabel is None:
            xlabel = self.no_x_label
        
        if ylabel is None:
            if len(self.no_y_label) == 1:
                ylabel = self.no_y_label[0]
            else: 
                ylabel = 'value'
        #Set labels and title
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        
        #Set legend
        if self.label is None:
            if self.no_label is not None:
                label = self.no_label
        else:
            label = self.label

        if label is not None:
            print(label)
            if isinstance(label,str):
                label = [label]
            ax.legend(labels=label)

        return ax

    class _trendline:
        def __init__(self, method, x, y):
            self.method = method
            self.x = x
            self.y = y

        def __main__(self):
            if (self.method).lower() == 'ols':
                self.__ols__()
            elif (self.method).lower() == 'poly':
                self.__poly__()
            elif (self.method).lower() == 'moving average':
                self.__moving_average__() 
            return self.x_pred, self.y_pred, self.reg_text
    
        def __moving_average__(self,number_of_points=10):
            # Calculate the moving average
            self.y_pred = np.convolve(self.y, np.ones(number_of_points), 'valid') / number_of_points
            self.x_pred = self.x[:len(self.y_pred)]
            self.reg_text = f'Moving Average: \n  {number_of_points} points'

        def __poly__(self, max_degree=5):
            best_degree = None
            best_error = float('inf')

            for degree in range(1, max_degree + 1):
                # Polynomial regression
                poly = np.polyfit(self.x, self.y, degree)
                y_pred = np.poly1d(poly)(self.x)

            # Calculate the error using cross-validation
            error = np.mean((y_pred - self.y) ** 2)

            if error < best_error:
                best_error = error
                best_degree = degree

            # Fit the polynomial with the best degree
            self.poly = np.polyfit(self.x, self.y, best_degree)

            # Calculate the y values
            self.x_pred = np.linspace(self.x.min(), self.x.max(), 100)
            self.y_pred = np.poly1d(self.poly)(self.x_pred)
            
            # Calculate the R-squared value
            ss_res = np.sum((self.y - np.polyval(self.poly, self.x)) ** 2)
            ss_tot = np.sum((self.y - np.mean(self.y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot)

            self.reg_text = f'Best degree: {best_degree} \nR^2: {r_squared:.2f}'

            
        def __ols__(self):
            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(self.x,self.y)
            print(f'Slope: {slope :.2f}, Intercept: {intercept:.2f}, R-Squared: {r_value**2:.2f},P-Value: {p_value:.2f}, Standard Error: {std_err:.2f}')
            # Calculate the y values
            self.x_pred = np.linspace(self.x.min(),self.x.max(),100)
            self.y_pred = intercept + slope * self.x_pred
            self.reg_text = f'Slope: {slope:.2f} \nIntercept: {intercept:.2f}'
            
