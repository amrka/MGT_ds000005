# In[1]:

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

#========================================================================================================
# In[2]:

experiment_dir = '/home/in/aeed/poldrack_gabmling/' 

subject_list = [
                'sub-01', 'sub-02', 'sub-03', 'sub-04', 'sub-05', 'sub-06', 'sub-08', 'sub-09', 
                'sub-10', 'sub-11', 'sub-13', 'sub-14', 'sub-15', 'sub-16']


session_list = ['run-01',
                'run-02',
                'run-03',]                

                
output_dir  = '/home/in/aeed/poldrack_gabmling/output_MGT_poldrack_preproc_preproc'
working_dir = '/home/in/aeed/poldrack_gabmling/workingdir_MGT_poldrack_preproc_preproc'


preproc = Workflow (name = 'preproc')
preproc.base_dir = opj(experiment_dir, working_dir)


#=====================================================================================================
# In[3]:
#to prevent nipype from iterating over the anat image with each func run, you need seperate
#nodes to select the files
#and this will solve the problem I have for almost 6 months
#but notice that in the sessions, you have to iterate also over subject_id to get the {subject_id} var



# Infosource - a function free node to iterate over the list of subject names
infosource_anat = Node(IdentityInterface(fields=['subject_id']),
                  name="infosource_anat")
infosource_anat.iterables = [('subject_id', subject_list)]



infosource_func = Node(IdentityInterface(fields=['subject_id','session_id']),
                  name="infosource_func")
infosource_func.iterables = [('subject_id', subject_list),
                             ('session_id', session_list)]


#========================================================================================================
# In[4]:
# /home/in/aeed/poldrack_gabmling/ds000005/sub-01/anat/sub-01_T1w.nii.gz
#anatomical images
templates_anat = {
             'anat'     : 'ds000005/{subject_id}/anat/{subject_id}_T1w.nii.gz'
             }

selectfiles_anat = Node(SelectFiles(templates_anat,
                   base_directory=experiment_dir),
                   name="selectfiles_anat")


#sub-01_task-mixedgamblestask_run-01_bold.nii.gz
#functional runs
templates_func = {      
             'bold'    : 'ds000005/{subject_id}/func/{subject_id}_task-mixedgamblestask_{session_id}_bold.nii.gz',
             }

selectfiles_func = Node(SelectFiles(templates_func,
                   base_directory=experiment_dir),
                   name="selectfiles_func")
#========================================================================================================
# In[5]:

datasink = Node(DataSink(), name = 'datasink')
datasink.inputs.container = output_dir
datasink.inputs.base_directory = experiment_dir

substitutions = [('_subject_id_', ''),('_session_id_', '')]

datasink.inputs.substitutions = substitutions

#========================================================================================================
# In[6]:

standard_brain = '/home/in/aeed/fsl/fsl/data/standard/MNI152_T1_1mm_brain.nii.gz' 
standard_mask = '/home/in/aeed/fsl/fsl/data/standard/MNI152_T1_1mm_brain_mask.nii.gz'

TR = 2.0

#=======================================================================================================
# In[7]:

#Remove skull using antsBrainExtraction.sh, i am using the study-based template that I build and remove
#the skull manually using ITKsnap
brain_extraction_anat = Node(fsl.BET(), name='brain_extraction_anat')
brain_extraction_anat.frac = 0.5
brain_extraction_anat.inputs.vertical_gradient = 0.0
brain_extraction_anat.inputs.mask = True


#======================================================================================================
# In[8]:
#Extract one fmri image to use fro brain extraction, the same one you will use for mcflirt as reference
roi = Node(fsl.ExtractROI(), name='extract_one_fMRI_volume')

roi.inputs.t_min = 119
roi.inputs.t_size = 1


#======================================================================================================

#Remove skull of func using antsBrainExtraction.sh, i am using the study-based template that I build and remove
#the skull manually using ITKsnap
brain_extraction_bold = Node(fsl.BET(), name='brain_extraction_bold')
brain_extraction_bold.inputs.frac = 0.5
brain_extraction_bold.inputs.vertical_gradient = 0.0
brain_extraction_bold.inputs.mask = True

#=======================================================================================================
# In[9]:

#use the mask generated from bet bold to remove skull from bold
apply_bet_mask = Node(fsl.ApplyMask(), name='apply_bet_mask')

#========================================================================================================
# In[10]:

## normalizing the anatomical_bias_corrected image to the common anatomical template
## Here only we are calculating the paramters, we apply them later.

reg_T1_2_temp = Node(ants.Registration(), name = 'reg_T1_2_temp')
reg_T1_2_temp.inputs.args='--float'
reg_T1_2_temp.inputs.collapse_output_transforms=True
reg_T1_2_temp.inputs.fixed_image=standard_brain
reg_T1_2_temp.inputs.initial_moving_transform_com=True
reg_T1_2_temp.inputs.num_threads=8
reg_T1_2_temp.inputs.output_inverse_warped_image=True
reg_T1_2_temp.inputs.output_warped_image=True
reg_T1_2_temp.inputs.sigma_units=['vox']*3
reg_T1_2_temp.inputs.transforms= ['Rigid', 'Affine', 'SyN']
reg_T1_2_temp.inputs.winsorize_lower_quantile=0.005
reg_T1_2_temp.inputs.winsorize_upper_quantile=0.995
reg_T1_2_temp.inputs.convergence_threshold=[1e-06]
reg_T1_2_temp.inputs.convergence_window_size=[10]
reg_T1_2_temp.inputs.metric=['MI', 'MI', 'CC']
reg_T1_2_temp.inputs.metric_weight=[1.0]*3
reg_T1_2_temp.inputs.number_of_iterations=[[1000, 500, 250, 100],
                                                 [1000, 500, 250, 100],
                                                 [100, 70, 50, 20]]
reg_T1_2_temp.inputs.radius_or_number_of_bins=[32, 32, 4]
reg_T1_2_temp.inputs.sampling_percentage=[0.25, 0.25, 1]
reg_T1_2_temp.inputs.sampling_strategy=['Regular',
                                              'Regular',
                                              'None']
reg_T1_2_temp.inputs.shrink_factors=[[8, 4, 2, 1]]*3
reg_T1_2_temp.inputs.smoothing_sigmas=[[3, 2, 1, 0]]*3
reg_T1_2_temp.inputs.transform_parameters=[(0.1,),
                                                 (0.1,),
                                                 (0.1, 3.0, 0.0)]
reg_T1_2_temp.inputs.use_histogram_matching=True
reg_T1_2_temp.inputs.write_composite_transform=True
reg_T1_2_temp.inputs.verbose=True
reg_T1_2_temp.inputs.output_warped_image=True
reg_T1_2_temp.inputs.float=True

#========================================================================================================
# In[11]:
#If you do it like this, the pipeline will coregister bold of each session to all the anats of all subjs
# coreg = reg_T1_2_temp.clone(name = 'coreg')
# coreg.inputs.transforms=['Rigid']
# /media/amr/Amr_1TB/NARPS/workingdir_narps_preproc_preproc/preproc/_subject_id_sub-005/brain_extraction_anat/highres001_BrainExtractionBrain.nii.gz

#There will be always an error if nipype submitted coreg before brain extraction
def coreg(bold_image):
  #take brain extracted anat as an input, but do not use it
  #only to force the pipeline to run brain extraction first
    import ants, os, re
    import nipype.interfaces.fsl as fsl
    #the trick is to get the anat image without the solicit from the pipeline
    cwd = os.getcwd()
    subj_no = re.findall('\d+',cwd)[-1]

    img = '/home/in/aeed/poldrack_gabmling/workingdir_MGT_poldrack_preproc_preproc/preproc/_subject_id_sub-{0}/brain_extraction_anat/sub-{0}_T1w_brain.nii.gz'.format(subj_no)

    fixed = ants.image_read(img)
    moving = ants.image_read(bold_image)
    #you have to setup the outprefix, otherwise it will send the output to tmp folder 

    mytx = ants.registration(fixed=fixed , moving=moving, type_of_transform='Rigid', outprefix = 'bold_2_anat_sub-{0}'.format(subj_no))

    mywarpedimage = ants.apply_transforms(fixed=fixed, moving=moving,
                                          transformlist=mytx['fwdtransforms'])

    ants.image_write(image=mywarpedimage, filename='bold_2_anat_sub-{0}.nii.gz'.format(subj_no))

    composite_transform = os.path.abspath('bold_2_anat_sub-{0}0GenericAffine.mat'.format(subj_no))

    warped_image = os.path.abspath('bold_2_anat_sub-{0}.nii.gz'.format(subj_no))

    return composite_transform, warped_image #always you need return


coreg = Node(name = 'coreg',
                  interface = Function(input_names = ['bold_image', 'anat_brain'],
                               output_names = ['composite_transform', 'warped_image'],
                  function = coreg))




#========================================================================================================
# In[12]:

# mcflirt -in ${folder} -out ${folder}_mcf  -refvol example_func -plots -mats  -report;

McFlirt = Node(fsl.MCFLIRT(), name = 'McFlirt')
McFlirt.inputs.save_plots = True
McFlirt.inputs.save_mats = True
McFlirt.inputs.save_rms = True
McFlirt.inputs.ref_vol = 120

#========================================================================================================
# In[13]:

#Getting motion parameters from Mcflirt and plotting them

def Plot_Motion(motion_par, rms_files):

    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.use('Agg') 

    movement = np.loadtxt(motion_par)
    abs_disp = np.loadtxt(rms_files[0])
    rel_disp = np.loadtxt(rms_files[1])
    plt.figure(figsize=(8,10), dpi=300)

    plt.subplot(311)
    plt.title('Translations in mm')
    plt.plot(movement[:,:3])
    plt.legend(['x','y','z'])

    plt.subplot(312)
    plt.title('Rotations in radians')
    plt.plot(movement[:,3:])
    plt.legend(['x','y','z'])
    
    plt.subplot(313)
    plt.title('Displacement in mm')
    plt.plot(abs_disp)
    plt.plot(rel_disp)
    plt.legend(['abs', 'rel'])

    plt.savefig('Motion')


Plot_Motion = Node(name = 'Plot_Motion',
                  interface = Function(input_names = ['motion_par','rms_files'],
                  function = Plot_Motion))



#========================================================================================================
# In[14]:

# apply the trasnfromation to all the EPI volumes

func_2_template = Node(ants.ApplyTransforms(), name = 'func_2_template')
func_2_template.inputs.dimension = 3

func_2_template.inputs.input_image_type = 3
func_2_template.inputs.num_threads = 1
func_2_template.inputs.float = True


#========================================================================================================
# In[15]:

#Use nilearn smoothin, because, as you know, fsl does not support anisotropic smoothing
def nilearn_smoothing(image):
    import nilearn 
    from nilearn.image import smooth_img

    import numpy as np
    import os

    kernel = [6,6,6]



    smoothed_img = smooth_img(image, kernel)
    smoothed_img.to_filename('smoothed_all.nii.gz')

    smoothed_output = os.path.abspath('smoothed_all.nii.gz')
    return  smoothed_output



nilearn_smoothing = Node(name = 'nilearn_smoothing',
                  interface = Function(input_names = ['image'],
                               output_names = ['smoothed_output'],
                  function = nilearn_smoothing))


#========================================================================================================
# In[16]:

#Getting median intensity
Median_Intensity = Node(fsl.ImageStats(), name = 'Median_Intensity')
#Put -k before -p 50
Median_Intensity.inputs.op_string = '-k %s -p 50'

#Scale median intensity 
def Scale_Median_Intensity (median_intensity):
    scaling = 10000/median_intensity
    return scaling

Scale_Median_Intensity = Node(name = 'Scale_Median_Intensity',
                      interface = Function(input_names = ['median_intensity'],
                                           output_names = ['scaling'],
                                           function = Scale_Median_Intensity))
#========================================================================================================
# In[17]:

#Global Intensity Normalization by multiplying by the scaling value
#the grand-mean intensity normalisation factor ( to give a median brain intensity of 10000 )
#grand mean scaling
Intensity_Normalization = Node(fsl.BinaryMaths(), name = 'Intensity_Normalization')
Intensity_Normalization.inputs.operation = 'mul'

#========================================================================================================
# In[18]:

#   fslmaths ${folder}_mcf_2highres_intnorm -bptf 25 -1 -add tempMean ${folder}_mcf_2highres_tempfilt;
# sigma[vol] = filter_width[secs]/(2*TR[secs])
high_pass_filter = Node(fsl.TemporalFilter(), name = 'high_pass_filter')
high_pass_filter.inputs.highpass_sigma = 22.5 #90s / (2*2(TR))
#========================================================================================================
# In[19]

#Get the mean image
Get_Mean_Image = Node(fsl.MeanImage(), name = 'Get_Mean_Image')
Get_Mean_Image.inputs.dimension = 'T'

#Add the mean image to the filtered image
Add_Mean_Image = Node(fsl.BinaryMaths(), name = 'Add_Mean_Image')
Add_Mean_Image.inputs.operation = 'add'



#========================================================================================================
# In[20]:

melodic = Node(fsl.MELODIC(), name = 'Melodic')
melodic.inputs.approach = 'concat'
melodic.inputs.no_bet = True
melodic.inputs.bg_threshold = 10.0
melodic.inputs.tr_sec = 2.00
melodic.inputs.mm_thresh = 0.5
melodic.inputs.out_all = True
melodic.inputs.report = True
melodic.iterables = ('dim', [15,20,25])


#========================================================================================================
# In[21]:


preproc.connect([


              (infosource_anat, selectfiles_anat,[('subject_id','subject_id')]),

              (infosource_func, selectfiles_func, [('subject_id','subject_id'),
                                                   ('session_id','session_id')]),

              (selectfiles_anat, brain_extraction_anat, [('anat','in_file')]),
              (brain_extraction_anat, reg_T1_2_temp, [('out_file','moving_image')]),



              (selectfiles_func, McFlirt, [('bold','in_file')]),

              (McFlirt, Plot_Motion, [('par_file','motion_par'),
                                      ('rms_files','rms_files')]),

              (McFlirt, roi, [('out_file','in_file')]),

              (roi, brain_extraction_bold, [('roi_file','in_file')]),

              (brain_extraction_bold, apply_bet_mask, [('mask_file','mask_file')]),
              (McFlirt, apply_bet_mask, [('out_file','in_file')]),



              (brain_extraction_bold, coreg, [('out_file','bold_image')]),

              (apply_bet_mask, nilearn_smoothing, [('out_file','image')]),


              (apply_bet_mask, Median_Intensity, [('out_file','in_file')]),
              (brain_extraction_bold, Median_Intensity, [('mask_file','mask_file')]),

              (Median_Intensity, Scale_Median_Intensity, [('out_stat','median_intensity')]),

              (Scale_Median_Intensity, Intensity_Normalization, [('scaling','operand_value')]),
              (nilearn_smoothing, Intensity_Normalization, [('smoothed_output','in_file')]),


              (Intensity_Normalization, Get_Mean_Image, [('out_file','in_file')]),
              (Intensity_Normalization, high_pass_filter, [('out_file','in_file')]),

              (high_pass_filter, Add_Mean_Image, [('out_file','in_file')]),
              (Get_Mean_Image, Add_Mean_Image, [('out_file','operand_file')]),

              # #======================================datasink============================================
              # (Add_Mean_Image, datasink, [('out_file','preproc_img')]),
              # (apply_bet_mask, datasink, [('out_file','bold_brain')]),
              # (brain_extraction_bold, datasink, [('mask_file','bold_mask')]),                                   
              # (coreg, datasink, [('composite_transform','func_2_anat_trans')]),
              # (brain_extraction_anat, datasink, [('out_file','anat_brain'),
              #                                    ('mask_file', 'anat_mask')]),
              # (reg_T1_2_temp, datasink, [('composite_transform','anat_2_temp_trans'),
              #                            ('warped_image','anat_2_temp_image')]),

              ])

preproc.write_graph(graph2use='colored', format='png', simple_form=True)

preproc.run(plugin='SLURM',plugin_args={'dont_resubmit_completed_jobs': True, 'max_jobs':50})

