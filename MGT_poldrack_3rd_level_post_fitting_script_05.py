from nipype import config
cfg = dict(execution={'remove_unnecessary_outputs': False})
config.update_config(cfg)

import nipype.interfaces.fsl as fsl
import nipype.interfaces.afni as afni
import nipype.interfaces.ants as ants
import nipype.interfaces.spm as spm

from nipype.interfaces.utility import IdentityInterface, Function, Select, Merge
from os.path import join as opj
from nipype.interfaces.io import SelectFiles, DataSink
from nipype.pipeline.engine import Workflow, Node, MapNode

import numpy as np
import os, re
import matplotlib.pyplot as plt
from nipype.interfaces.matlab import MatlabCommand
MatlabCommand.set_default_paths('/Users/amr/Downloads/spm12')
MatlabCommand.set_default_matlab_cmd("matlab -nodesktop -nosplash")

# import nipype.interfaces.matlab as mlab
# mlab.MatlabCommand.set_default_matlab_cmd("matlab -nodesktop -nosplash")
# mlab.MatlabCommand.set_default_paths('/home/amr/Documents/MATLAB/toolbox/spm8')

#==========================================================================================================================================================
# In[2]:

experiment_dir = '/Users/amr/Documents/mixed_gambling_poldrack_2007/' 


task_list = ['gain','loss']

              




contrast_list = ['cope1',
                'cope2']

                
output_dir  = '/Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level_post_fitting'
working_dir = '/Users/amr/Documents/mixed_gambling_poldrack_2007/workingdir_MGT_poldrack_proc_3rd_level_post_fitting'


proc_3rd_level = Workflow (name = 'proc_3rd_level')
proc_3rd_level.base_dir = opj(experiment_dir, working_dir)


#==========================================================================================================================================================
# In[3]:
#to prevent nipype from iterating over the anat image with each func run-, you need seperate
#nodes to select the files
#and this will solve the problem I have for almost 6 months
#but notice that in the sessions, you have to iterate also over subject_id to get the {subject_id} var



# Infosource - a function free node to iterate over the list of subject names

infosource = Node(IdentityInterface(fields=['tasks', 'contrasts' ]),
                  name="infosource")
infosource.iterables = [('tasks', task_list),
                        ('contrasts', contrast_list)]


#==========================================================================================================================================================
# In[4]:
# sub-001_task-MGT_run--02_bold.nii.gz, sub-001_task-MGT_run--02_sbref.nii.gz
#/preproc_img/run--04sub-119/smoothed_all_maths_filt_maths.nii.gz
#functional run-s

standard_brain = '/usr/local/fsl/data/standard/MNI152_T1_1mm_brain.nii.gz'
standard_mask = '/usr/local/fsl/data/standard/MNI152_T1_1mm_brain_mask.nii.gz'



templates = {


          'contrast'           :  '/Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/{tasks}_stat_flameo_positive_and_negative/+/{contrasts}.nii.gz',

        }



selectfiles = Node(SelectFiles(templates,
                              base_directory=experiment_dir),
                              name="selectfiles")
#==========================================================================================================================================================
# In[5]:

datasink = Node(DataSink(), name = 'datasink')
datasink.inputs.container = output_dir
datasink.inputs.base_directory = experiment_dir

substitutions = [('_tasks_', ''),('_contrasts_', '')]

datasink.inputs.substitutions = substitutions

#==========================================================================================================================================================
#Smooth estimation
def smooth_est(contrast):
     import nipype.interfaces.fsl as fsl
     import os
     standard_mask = '/usr/local/fsl/data/standard/MNI152_T1_1mm_brain_mask.nii.gz'

     smooth_est = fsl.SmoothEstimate()
     smooth_est.inputs.dof = 15
     smooth_est.inputs.mask_file = standard_mask


     if contrast[-53:-49] == 'gain':
          res4d = '/Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/gain_stat_flameo/+/res4d.nii.gz'
     elif contrast[-53:-49] == 'loss':
          res4d = '/Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/loss_stat_flameo/+/res4d.nii.gz'

     print(res4d)


     smooth_est.inputs.residual_fit_file = res4d
     smooth_est_outputs = smooth_est.run()


     dlh = smooth_est_outputs.outputs.dlh
     volume = smooth_est_outputs.outputs.volume
     resels = smooth_est_outputs.outputs.resels


     return dlh, volume, resels

smooth_est = Node(name = 'smooth_est',
                  interface = Function(input_names = ['contrast'],
                  output_names = ['dlh', 'volume', 'resels'],
                  function = smooth_est))

#==========================================================================================================================================================
#mask zstat1

mask_zstat = Node(fsl.ApplyMask(), name='mask_zstat')
mask_zstat.inputs.mask_file = standard_mask
mask_zstat.inputs.out_file = 'thresh_zstat.nii.gz'


#==========================================================================================================================================================
#cluster copes1
cluster_copes = Node(fsl.model.Cluster(), name='cluster')

#cluster_copes.inputs.threshold = 3.1
cluster_copes.iterables = ('threshold', [2.3, 3.1])
cluster_copes.inputs.pthreshold = 0.001
cluster_copes.inputs.connectivity = 26

cluster_copes.inputs.out_threshold_file = 'thresh_zstat.nii.gz'
cluster_copes.inputs.out_index_file = 'cluster_mask_zstat'
cluster_copes.inputs.out_localmax_txt_file = 'lmax_zstat_std.txt'
cluster_copes.inputs.use_mm = True

#==========================================================================================================================================================
#overlay thresh_zstat1

overlay_cope = Node(fsl.Overlay(), name='overlay')
overlay_cope.inputs.auto_thresh_bg = True
overlay_cope.inputs.stat_thresh = (3.1,10)
overlay_cope.inputs.transparency = True
overlay_cope.inputs.out_file = 'rendered_thresh_zstat.nii.gz'
overlay_cope.inputs.show_negative_stats = True
overlay_cope.inputs.background_image = standard_brain

#==========================================================================================================================================================
#generate pics thresh_zstat1

slicer_cope = Node(fsl.Slicer(), name='slicer')
slicer_cope.inputs.sample_axial = 2
slicer_cope.inputs.image_width = 2000
slicer_cope.inputs.out_file = 'rendered_thresh_zstat.png'











proc_3rd_level.connect([


              (infosource, selectfiles, [('tasks','tasks'),
                                         ('contrasts','contrasts')]),



              (selectfiles, smooth_est, [('contrast','contrast')]),
 

              (selectfiles, mask_zstat, [('contrast','in_file')]),


              (mask_zstat, cluster_copes, [('out_file','in_file')]),
              (smooth_est, cluster_copes, [('volume','volume'),
                                           ('dlh','dlh')]),

              (selectfiles, cluster_copes, [('contrast','cope_file')]),


              (cluster_copes, overlay_cope, [('threshold_file','stat_image')]),

              (overlay_cope, slicer_cope, [('out_file','in_file')]),


              # (slicer_cope, datasink, [('out_file','cope2_activation_pic')]),

              # (cope2_2ndlevel__template, datasink, [('output_image','cope2_2ndlevel_2_template')]),


              ])

proc_3rd_level.write_graph(graph2use='colored', format='png', simple_form=True)

proc_3rd_level.run('MultiProc', plugin_args={'n_procs': 8})





