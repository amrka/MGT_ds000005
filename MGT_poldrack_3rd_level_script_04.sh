#!/bin/bash

# calc(){ awk "BEGIN { print "$*" }"; }

# move to parent directory
cd /home/in/aeed/poldrack_gabmling

#create an output for 3rd level
mkdir -p output_MGT_poldrack_proc_3rd_level/{copes1,varcopes1,copes2,varcopes2} 
cd output_MGT_poldrack_proc_3rd_level


#seperate the files from each group based on whether they are even or odd

for folder in /home/in/aeed/poldrack_gabmling/ds000005/sub-*;do

	no=`echo ${folder:end-2}`


	#mod 5%2=1 => odd, 4%2=0 => even 

	cp /home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_2nd_level/cope1_2ndlevel_2_template/sub-${no}/cope1_2ndlevel_2_standard_brain.nii.gz \
	/home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_3rd_level/copes1/cope1_sub-${no}.nii.gz

	cp /home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_2nd_level/varcope1_2ndlevel_2_template/sub-${no}/varcope1_2ndlevel_2_standard_brain.nii.gz \
	/home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_3rd_level/varcopes1/varcope1_sub-${no}.nii.gz


	cp /home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_2nd_level/cope2_2ndlevel_2_template/sub-${no}/cope2_2ndlevel_2_standard_brain.nii.gz \
	/home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_3rd_level/copes2/cope2_sub-${no}.nii.gz

	cp /home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_2nd_level/varcope2_2ndlevel_2_template/sub-${no}/varcope2_2ndlevel_2_standard_brain.nii.gz \
	/home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_3rd_level/varcopes2/varcope2_sub-${no}.nii.gz

done


#==============================================================================================================================

#combine cope1&2 and varcope1&2 
fslmerge -t /home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_3rd_level/gain_group_cope1.nii.gz \
/home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_3rd_level/copes1/cope1_sub-*

fslchfiletype NIFTI /home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_3rd_level/gain_group_cope1.nii.gz

fslmerge -t /home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_3rd_level/gain_group_varcope1.nii.gz \
/home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_3rd_level/varcopes1/varcope1_sub-*


fslmerge -t /home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_3rd_level/loss_group_cope2.nii.gz \
/home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_3rd_level/copes2/cope2_sub-*


fslchfiletype NIFTI /home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_3rd_level/loss_group_cope2.nii.gz

fslmerge -t /home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_3rd_level/loss_group_varcope2.nii.gz \
/home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_3rd_level/varcopes2/varcope2_sub-*



cd /home/in/aeed/poldrack_gabmling/output_MGT_poldrack_proc_3rd_level/


cp /usr/local/fsl/data/standard/MNI152_T1_1mm_brain_mask.nii.gz /Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/MNI152_T1_1mm_brain_mask.nii.gz
fslchfiletype NIFTI /Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/MNI152_T1_1mm_brain_mask.nii.gz

################################################################################
#the rest is done locally not on the cluster


mkdir gain_stat_flameo_positive_and_negative
mkdir loss_stat_flameo_positive_and_negative





flameo \
--cope=/Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/gain_group_cope1.nii \
--vc=/Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/gain_group_varcope1.nii.gz \
--mask=/Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/MNI152_T1_1mm_brain_mask.nii \
--ld=/Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/gain_stat_flameo_positive_and_negative/ \
--dm=/Users/amr/Documents/mixed_gambling_poldrack_2007/one_sample_ttest_16sub_MGT_poldrack_positive_and_negative.mat \
--cs=/Users/amr/Documents/mixed_gambling_poldrack_2007/one_sample_ttest_16sub_MGT_poldrack_positive_and_negative.grp \
--tc=/Users/amr/Documents/mixed_gambling_poldrack_2007/one_sample_ttest_16sub_MGT_poldrack_positive_and_negative.con \
--runmode=flame1



flameo \
--cope=/Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/loss_group_cope2.nii \
--vc=/Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/loss_group_varcope2.nii.gz \
--mask=/Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/MNI152_T1_1mm_brain_mask.nii \
--ld=/Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/loss_stat_flameo_positive_and_negative/ \
--dm=/Users/amr/Documents/mixed_gambling_poldrack_2007/one_sample_ttest_16sub_MGT_poldrack_positive_and_negative.mat \
--cs=/Users/amr/Documents/mixed_gambling_poldrack_2007/one_sample_ttest_16sub_MGT_poldrack_positive_and_negative.grp \
--tc=/Users/amr/Documents/mixed_gambling_poldrack_2007/one_sample_ttest_16sub_MGT_poldrack_positive_and_negative.con \
--runmode=flame1





mkdir gain_stat_randomise

mkdir loss_stat_randomise



randomise \
-i /Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/gain_group_cope1.nii \
-o /Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/gain_stat_randomise/gain_positive_and_negative \
-m /Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/MNI152_T1_1mm_brain_mask.nii \
-d /Users/amr/Documents/mixed_gambling_poldrack_2007/one_sample_ttest_16sub_MGT_poldrack_positive_and_negative.mat \
-t /Users/amr/Documents/mixed_gambling_poldrack_2007/one_sample_ttest_16sub_MGT_poldrack_positive_and_negative.con \
-e /Users/amr/Documents/mixed_gambling_poldrack_2007/one_sample_ttest_16sub_MGT_poldrack_positive_and_negative.grp \
-n 1000 -T -c 3.1 --uncorrp --film -x


randomise \
-i /Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/loss_group_cope2.nii \
-o /Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/loss_stat_randomise/loss_positive_and_negative \
-m /Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/MNI152_T1_1mm_brain_mask.nii \
-d /Users/amr/Documents/mixed_gambling_poldrack_2007/one_sample_ttest_16sub_MGT_poldrack_positive_and_negative.mat \
-t /Users/amr/Documents/mixed_gambling_poldrack_2007/one_sample_ttest_16sub_MGT_poldrack_positive_and_negative.con \
-e /Users/amr/Documents/mixed_gambling_poldrack_2007/one_sample_ttest_16sub_MGT_poldrack_positive_and_negative.grp \
-n 10000 -T -c 3.1 --uncorrp --film -x





mkdir /Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/gain_stat_palm
mkdir /Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/loss_stat_palm


palm \
-i /Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/gain_group_cope1.nii \
-o /Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/gain_stat_palm/gain \
-m /Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/MNI152_T1_1mm_brain_mask.nii \
-d /Users/amr/Documents/mixed_gambling_poldrack_2007/one_sample_ttest_16sub_MGT_poldrack_positive_and_negative.mat \
-t /Users/amr/Documents/mixed_gambling_poldrack_2007/one_sample_ttest_16sub_MGT_poldrack_positive_and_negative.con \
-vg /Users/amr/Documents/mixed_gambling_poldrack_2007/one_sample_ttest_16sub_MGT_poldrack_positive_and_negative.grp \
-n 5000 -T -C 3.1 -ise -corrcon -save1-p



palm \
-i /Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/loss_group_cope2.nii \
-o /Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/loss_stat_palm/loss \
-m /Users/amr/Documents/mixed_gambling_poldrack_2007/output_MGT_poldrack_proc_3rd_level/MNI152_T1_1mm_brain_mask.nii \
-d /Users/amr/Documents/mixed_gambling_poldrack_2007/one_sample_ttest_16sub_MGT_poldrack_positive_and_negative.mat \
-t /Users/amr/Documents/mixed_gambling_poldrack_2007/one_sample_ttest_16sub_MGT_poldrack_positive_and_negative.con \
-vg /Users/amr/Documents/mixed_gambling_poldrack_2007/one_sample_ttest_16sub_MGT_poldrack_positive_and_negative.grp \
-n 5000 -T -C 3.1 -ise -corrcon -save1-p

