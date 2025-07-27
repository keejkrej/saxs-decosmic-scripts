#!/usr/bin/env python3

"""
sa09

==========

super averager for Pilatus detector images

.. module:: sa09
.. autoclass:: Avger
.. autoclass:: Sa

"""

# super averager for Pilatus detector images
# version 09
# This version fixes a critical bug in the grouped median.
# Improved text output a bit to make it clearer.


# author: Kilian Frank 2020-11-05
# no warranty, do not distribute
# license: In the future, this work might be released under the GNU General Public License v3.0 (see license.txt).

# ===== major refactoring =====
# program should be much more object-oriented
# user should be able to perfom multiple averaging operations in one go
# zip/gz input should be via temporary unzipping as long as fabio/PIP issue is not fixed
# input should be a folder (default './')
# preview should not stop the calculations
# algorithms should be gradually made real-time
# 32 bit calculation should be enough, but this must be checked 

# structure:
# list files
# parse arguments / check validity
# load files
# go through queue of operations, decouple preview
# save


# core functionality:
# sum/mean/med/grouped med/dc2d
# one single image/timeseries/waxs (which is like timeseries, but with stitching)

# optional uncertainty calculation
# dc1d will be kept for later
 
# side functionality:
# tif/cbf/edf images should be saved as one big zip/Eigerimage
# zip/Eigerimage shoud be unzipped to images tif/cbf/edf 
# a valid P100K/P300K mask should be saved with a simple command

# if not specified: look for archives, ask if to extract them, then process images individually, delete temp folders at the end
# if archive specified: extract, then process images individually, delete temp folders at the end
# if image specified: ignore archives, process images individually

# idea: iterate over all input folders / all input archives if exist / all input files / all groups / all avgers / all parameter sets (done) / all stitchers

# ===== backlog =====

# (done) negative and nan handling of the image stack
# (done) the other avgers: avg, sum, median, grouped median
# (done) uncertainties (done except for median)
# (done) preview (which does not stop the calculation)
# (done) get image size from file and catch error if detectors are mixed

# Example for inline documentation (will use sphinx later)

#    """
#    Approximate Fibonacci sequence
#
#    Args:
#        n (int): The place in Fibonacci sequence to approximate
#
#    Returns:
#        float: The approximate value in Fibonacci sequence
#    """

# ===== imports =====
from datetime import datetime
import sys
import os
import argparse
from tqdm import tqdm
import numpy as np
import fabio
import bottleneck as bn
import zipfile
import tarfile
import shutil

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import rcParams

# ===== globals =====
version = 8
xhighest_default = 1e-4
ngroups_default = 3
inpath_default = './'
outpath_default = None # writes to the input folder
filetype_default = '.tif'
nan_default = True
uncertainty_default = False
preview_default = True
verbose_level_default = 1
temppath_default = 'sa_temp'

rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial']
rcParams['figure.dpi']= 200
rcParams['axes.linewidth'] = 0.5
rcParams['xtick.major.width'] = 0.5
rcParams['xtick.minor.width'] = 0.5
rcParams['ytick.major.width'] = 0.5
rcParams['ytick.minor.width'] = 0.5
rcParams['lines.linewidth'] = 1.0

# make all these editable in the command line
verbose = True
imagetypes = ['.tif','.cbf','.edf']
archivetypes = ['.zip','.tar.gz']
dtype2d = 'float32'
avgers = ['sum','average','median','decosmic2d']

# ===== helper functions =====
def query_yes_no(question, default='yes'):
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        print(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').")

# ===== WAXS mode =====

# ===== core program =====
class Avger():
    """
    Averager class, can define and run the averaging procedures.
    """
    
    def __init__(self,name,params={},use_uncertainty=False):
        """
        Initializes an averager.

        Args:
            name (string): The name of the averager, must be in the list of known averagers.
            params (dict): Dictionary of parameters specific to the averager.
            use_uncertainty (bool): Whether or not to calculate the variance when averaging.
        """
            
        self.name = name
        self.params = params
        self.use_uncertainty = use_uncertainty
        self.data_avged = None
        self.var_avged = None
        self.success = -1
        self.modestr = None
        
    def run(self,data2d):
        """
        Runs an averager.

        Args:
            data2d (numpy array): The data, which will be averaged along the first dimension.

        Returns:
            numpy array: data_avged, the averaged data.
        """        
        
        if self.name == 'sum':
            self.data_avged = bn.nansum(data2d,axis=0)
            if self.use_uncertainty:
                self.var_avged = self.data_avged
            self.success = 1
            self.modestr = 'SUM'
            
        if self.name == 'average':
            self.data_avged = bn.nanmean(data2d,axis=0)
            if self.use_uncertainty:
                self.var_avged = bn.nanvar(data2d,axis=0)
            self.success = 1
            self.modestr = 'AVG' 
            
        if self.name == 'median':
            nfiles = len(data2d)
            ngroups = self.params['median']            
            
            if ngroups is not None:
                if ngroups > 1:
                    n_per_group, remainder = divmod(nfiles,ngroups)
                    nx_px = data2d.shape[1]
                    ny_px = data2d.shape[2]
                    data2d_groups = np.zeros((ngroups,nx_px,ny_px),dtype=dtype2d)
                    
                    for i in tqdm(range(ngroups)):
                        print('Taking the sum of group %d: Images %d to %d'%(i,i*n_per_group,i*n_per_group+n_per_group))
                        data2d_groups[i,:,:] = bn.nansum(np.where(data2d[i*n_per_group:i*n_per_group+n_per_group,:,:]>=0,data2d[i*n_per_group:i*n_per_group+n_per_group,:,:],np.nan),axis=0)
                    if remainder > 0:
                        if remainder == 1:
                            if verbose:
                                print('One file at the end will be omitted.')
                        else:
                            if verbose:
                                print('%d files at the end will be omitted.'%remainder)
                    if verbose:
                        print('Using the median of %d summed images.'%ngroups)
                    self.data_avged = bn.nanmedian(np.where(data2d_groups>=0,data2d_groups,np.nan),axis=0)
                else:
                    if verbose:
                        print('More than one group of files is required for the median. Skipping.')
            else:
                ngroups = nfiles
                print('Using the median of %d images.'%ngroups)
                self.data_avged = bn.nanmedian(data2d,axis=0)
                
            self.success = 1
            self.modestr = 'MED_OF_%d'%ngroups 
        
        if self.name == 'decosmic2d':
            nfiles = len(data2d)
            xhighest = self.params['decosmic2d']
            
            if xhighest == 0:
                if verbose:
                    print('Averaging all intensity values per pixel.')
                self.data_avged = bn.nanmean(data2d,axis=0)
                if self.use_uncertainty:
                    self.var_avged = bn.nanvar(data2d,axis=0)
                    
            elif xhighest > 0 and xhighest <=1:
                nlowest = int((1-xhighest)*nfiles)
                if nlowest == 0:
                    nlowest = 1
                if nlowest == 1:
                    if verbose:
                        print('Keeping only the lowest intensity values per pixel.')
                    self.data_avged = np.amin(data2d,axis=0)
                    if self.use_uncertainty:
                        self.var_avged = self.data_avged
                else:
                    if nlowest == nfiles:
                        nlowest -= 1
                    if verbose:
                        print('Averaging the lowest %d pixel intensities.'%nlowest)
                    data2d_part = bn.partition(data2d, nlowest, axis=0)[:nlowest]
                    self.data_avged = bn.nanmean(data2d_part,axis=0)
                    if self.use_uncertainty:
                        self.var_avged = bn.nanvar(data2d_part,axis=0)
            else: 
                print('xhighest must be between 0 and 1. Skipping.')
                self.success = 0
            self.success = 1
            self.modestr = 'DC2D_%.E'%xhighest
        
        return

class Sa():
    """
    Superaverager class. Defines the paths and image formats and keeps track of the inputs, averagers, stitchers, and outputs.
    """
    
    def __init__(self,args=None):
        """
        Initializes a superaverager instance.

        Args:
            args (argparse args object): Arguments passed from the command line.
        """
                
        self.args = args
        self.inpath = None
        self.filelist = None
        self.archivelist = None        
        self.nimages = None
        self.narchives = None
        self.nypx = None
        self.nxpx = None
        self.avgers = []
        self.use_archive = False
        self.temppath = None
        return
        
    def list_files(self):
        """
        Lists all files in inpath if they match filetype. Both must be specified in the superaverager instance.
        """
        
        self.filelist = sorted([x for x in os.listdir(self.inpath) if os.path.isfile(os.path.join(self.inpath,x)) and x.endswith(self.args.filetype)])
        self.nimages = len(self.filelist)
        return
        
    def list_archives(self):
        """
        Lists all archives in inpath if they match filetype. Both must be specified in the superaverager instance. 
        
        As it is now, it is redundant to list_files.
        """
        # could be checked via is_zipfile and is_tarfile
        self.archivelist = sorted([x for x in os.listdir(self.inpath) if os.path.isfile(os.path.join(self.inpath,x)) and x.endswith(self.args.filetype)])
        self.narchives = len(self.archivelist)
        return
        
    def pilatusfiles(self):
        """
        Keeps only the entries in filelist for which the filename reads "ct" before the last underscore.
        """
        
        # keeps only files that match the pilatus naming convention
        # second last part of the name must be ct
        
        self.filelist = sorted([x for x in self.filelist if x.split('_')[-2] == 'ct' ])
        self.nimages = len(self.filelist)
        return
            
    def extract_archive(self,filename):
        """
        Extracts an archive into a temporary folder. The folder will be reused, if existing, and only overwritten if confirmed.
        
        Args:
            filename (string): The name of the archive file which to extract.
        """
        
        self.temppath = os.path.join(self.inpath,temppath_default+'_'+filename)
        
        self.use_existing_temppath = False
        if os.path.exists(self.temppath):
            self.use_existing_temppath = query_yes_no('Path '+self.temppath+' exists already. Continue without extracting?',default='yes')
        if not self.use_existing_temppath:
            if os.path.exists(self.temppath):        
                shutil.rmtree(self.temppath)
            if self.args.verbose > 0:
                print('Created temporary folder %s.'%self.temppath)
            with zipfile.ZipFile(os.path.join(self.inpath,filename), 'r') as zip_ref:            
                zip_ref.extractall(self.temppath)
            
        self.inpath = self.temppath
        self.args.filetype = '.'+os.listdir(self.inpath)[0].split('.')[-1] # crude hack
        return
    
    def load_files(self):
        """
        Loads the (Pilatus) files specified in the filelist into a numpy array (data2d), the first dimension being the image number.
        """
        
        if self.filelist is None:
            self.list_files()
            self.pilatusfiles()
        
        data = fabio.open(os.path.join(self.inpath,self.filelist[0])).data
        self.nypx, self.nxpx = data.shape[0],data.shape[1]
        self.data2d = np.zeros((self.nimages,data.shape[0],data.shape[1]),dtype = dtype2d)
        self.data2d[0] = data
        
        for i,fn in tqdm(enumerate(self.filelist[1:]),unit=' images',initial=1,total=self.nimages):
            data = fabio.open(os.path.join(self.inpath,fn)).data
            if data.shape == (self.nypx,self.nxpx):
                self.data2d[i+1,:] = data
            else:
                if self.args.verbose > 0:
                    print('Image with a different size detected. Sort the images and run the program again.')
                self.data2d[i+1,:] = np.nan
        return
        
    def save_file(self,outfn,data_avged):
        """
        Saves the averaged image file. Asks before overwriting.
        
        Args:
            outfn (string): Filename under which to save.
            data_avged (numpy array): Averaged image data.
        """
        
        overwrite = True
        if os.path.isfile(os.path.join(self.args.outpath,outfn)):
            overwrite = query_yes_no('File '+outfn+' exists and will be overwritten. Continue?',default='yes')
        if overwrite:
            img = fabio.tifimage.tifimage(data_avged)
            img.save(os.path.join(self.args.outpath,outfn))
            if self.args.verbose > 0:
                print('File '+outfn+' was written.')
        else:
            if self.args.verbose > 0:
                print('Output file was not written.')
        return
    
    def manage_input(self):
        """
        Conducts the listing and loading of archive files and image files.
        """
        
        if self.args.verbose > 0:
            print('Starting file input...')

        if self.args.filetype in archivetypes or self.args.filetype in [x[1:] for x in archivetypes]:
            self.use_archive = True
            self.list_archives()
            if self.args.verbose > 0:
                print('%d archives of type %s found.'%(self.narchives,self.args.filetype))
            if self.args.verbose > 0:
                print('Extracting images...')
            self.extract_archive(self.archivelist[0])

        if self.args.filetype in imagetypes or self.args.filetype in [x[1:] for x in imagetypes]:
            self.list_files()
            self.pilatusfiles()
            if self.args.verbose > 0:
                print('%d Pilatus images of type %s found.'%(self.nimages,self.args.filetype))
        
        if self.nimages > 0:
            if self.args.verbose > 0:
                print('Loading images...')
            self.load_files()
        else:
            if self.args.verbose > 0:
                print('No images of type %s found. Exiting.'%(self.args.filetype))
                sys.exit(0)
        
        if self.args.verbose > 0:
            print('File input finished.')
            
        return
        
    def manage_avgers(self):
        """
        Creates a queue of the requested averagers and their settings. Then runs the averagers and shows a preview, if desired.
        """
        
        if self.args.verbose > 0:
            print('Starting averaging...')
            
        if self.args.negative_to_nan:
            self.data2d = np.where(self.data2d>=0,self.data2d,np.nan) # index the nonnegative values, make the others nan
        
        self.avgers = []
        
        for i,avger_name in enumerate(avgers):
            if hasattr(self.args,avger_name):
                vals = getattr(self.args,avger_name)    
                if isinstance(vals,bool):
                    if vals is True:
                        self.avgers.append(Avger(name=avger_name,params={avger_name:vals},use_uncertainty=self.args.uncertainty))
                elif vals is not None:
                    for val in vals:
                        self.avgers.append(Avger(name=avger_name,params={avger_name:val},use_uncertainty=self.args.uncertainty))
        for i,avger in enumerate(self.avgers):
            if self.args.verbose > 0:
                print('Running %s with %s...'%(avger.name,', '.join(map(str, avger.params.items()))))
            
            # run the averager
            avger.run(self.data2d)
            
            if avger.success == 1:
                if self.args.verbose > 0:
                    print('%s finished.'%(avger.name))
            
            if self.args.preview:
                fig,ax = plt.subplots()
                im = ax.imshow(avger.data_avged,origin='lower',interpolation='nearest',norm=LogNorm())
                plt.axis('off')
                
                divider = make_axes_locatable(ax)
                cax = divider.append_axes('right', size='5%', pad=0.05)                
                cbar = fig.colorbar(im, cax=cax, orientation='vertical')
                cbar.set_label('cts/s/px')
                
                ax.set_title(', '.join(map(str, avger.params.items())))
                plt.tight_layout()
                plt.show(block = False)
        
        if avger.success == 1:
            if self.args.verbose > 0:
                print('Averaging finished.')
            
        if self.args.preview:
            plt.show()
        return
        
    def manage_stitchers(self):
        """
        Controls the stitching of multiple averaged images into a larger image, e.g. for WAXS. (not implemented yet)
        """
        
        if self.args.verbose > 0:
            print('Starting stitching...')
            
        if self.args.verbose > 0:
            print('Stitching finished.')
        return
        
    def manage_output(self):
        """
        Conducts the file output. For every averager and parameter set run, an output file can be saved. Asks before overwriting. If an archive was extracted, the temporary folder will be removed.
        """
        
        if self.args.verbose > 0:
            print('Starting file output...')
            
        for i,avger in enumerate(self.avgers):
            if avger.success == 1:
                outfn = self.filelist[0].split(self.args.filetype)[0]+'_to_'+self.filelist[-1].split(self.args.filetype)[0].split('_')[-1]+'_'+avger.modestr+self.args.filetype
                # careful here if there are multiple groups, like for a timeseries
                self.save_file(outfn,avger.data_avged)
                if self.args.uncertainty and avger.var_avged is not None:
                    outfn = self.filelist[0].split(self.args.filetype)[0]+'_to_'+self.filelist[-1].split(self.args.filetype)[0].split('_')[-1]+'_'+avger.modestr+'_VAR'+self.args.filetype
                    self.save_file(outfn,avger.var_avged)
            
        if self.use_archive and not self.use_existing_temppath:
            shutil.rmtree(self.temppath)
            if self.args.verbose > 0:
                print('Deleted temporary folder %s.'%self.temppath)            
        if avger.success == 1:
            if self.args.verbose > 0:
                print('File output finished.')
        return
    
    def __del__(self):
        """
        Deletes the superaverager instance.
        """
        return

# ===== main program =====
def superavg():
    """
    Main program. Runs the superaverager according to the arguments specified in the command line
    
    Args:
        --inpaths (list): Paths where to find the images or image archives.
        --outpath (string): Path where to save the averaged images.
        --filetype (string): Type of image files to look for.
        --sum (bool): Whether to calculate and save the sum of the found images.
        --average (bool): Whether to calculate the average (arithmetic mean) of the found images.
        --median (int): Specifies the number of summed images which are calculated, before taking the median of the summed images.
        --decosmic2d (float): Specifies the fraction of high intensity pixels which will be discarded for removing cosmic background.
        
        --negative_to_nan (bool): Whether to ignore negative pixel intensities in the averaging.
        --uncertainty (bool): Whether to calculate and save also the variance per pixel of the found images.
        --preview (bool): Whether to show a preview of the averaged images.
        --verbose (int): Degree of how many status messages to show.
    """
    
    print('You are running superavg version %d.'%version)
    now = datetime.now() # current date and time
    print('Program started at %s.'%now.strftime("%Y-%m-%d, %H:%M:%S"))
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-inp','--inpaths',type=str, help='path where to find the images or image archives',default=inpath_default, nargs='*')
    parser.add_argument('-outp','--outpath',type=str, help='path where to save the images or image archives',default=outpath_default)
    parser.add_argument('-type','--filetype',type=str, help='type of images or archives to look for',default=filetype_default)
    
    parser.add_argument('-sum','--sum', action='store_true', help='sum of images',default=False)
    parser.add_argument('-avg','--average', action='store_true', help='average of images',default=False)
    parser.add_argument('-med','--median',type=int, help='number of groups to take the median from',default=None,nargs='*')
    parser.add_argument('-dc2d','--decosmic2d',type=float, help='fraction of highest intensity pixels to omit',default=None,nargs='*')
    
    parser.add_argument('-nan','--negative_to_nan', action='store_true', help="replace negative pixel intensities by nan and don't consider them",default=nan_default)
    parser.add_argument('-u','--uncertainty', action='store_true', help='calculate the variance per pixel',default=uncertainty_default)
    parser.add_argument('-p','--preview', action='store_true', help='show preview of the averaged images',default=preview_default)
    parser.add_argument('-v','--verbose',type=int, help='level of output messages to show',default=verbose_level_default)
    
    args = parser.parse_args()    
    
    
    # catch exceptions of type "avger specified but no parameter value given"
    if args.median is not None and len(args.median) == 0:
        args.median = [ngroups_default]
        if args.verbose > 0:
            print('Using the default value of %.E for median.'%ngroups_default)    
    
    if args.decosmic2d is not None and len(args.decosmic2d) == 0:
        args.decosmic2d = [xhighest_default]
        if args.verbose > 0:
            print('Using the default value of %.E for decosmic2d.'%xhighest_default)
                
    if not args.outpath:
        save_to_inpath = True
    else:
        save_to_inpath = False
    
    sa = Sa(args)
    
    for i,inpath in enumerate(sa.args.inpaths):
        sa.inpath = inpath
        if save_to_inpath:
            sa.args.outpath = inpath
        sa.manage_input()
        sa.manage_avgers()
        # sa.manage_stitchers()
        sa.manage_output()
    
    now = datetime.now() # current date and time
    print('Program ended at %s.'%now.strftime("%Y-%m-%d, %H:%M:%S"))
    
    return

# ===== run the main program =====
if __name__ == "__main__":    
    superavg()
