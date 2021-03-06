import re
import sys
import os
from os.path import join, basename, isfile, isdir
import argparse
import nibabel as nb
import numpy as np
from scipy import stats



def nosmoothFisherPostMelodicGLM_bp2mni (subject, side, sside, hemi, downsample):
    
    mni = 'mni_brain_${downsample}.nii.gz'.format(downsample=downsample)
    thal = 'masks/{hemi}_thalamus_HOSC_60_{downsample}.nii.gz'.format(hemi=hemi, downsample=downsample)
    
    melodicDir='rsFC_ICA_cmd/{downsample}_{side}_masked'.format(downsample=downsample, side=side)
    
    subject_dir = join(subject, 'DualRegression_TemporalICA')
    if not os.path.exists(subject_dir):
        print('\ creating subject_dir for ' + subject)
        os.mkdir(subject_dir)

    spatial = join(subject_dir, 'SpatialRegression_Stage1')
    if not os.path.exists(spatial):
        os.mkdir(spatial)
    
    pattern = join(subject_dir, 'rsFC_pattern')
    if not os.path.exists(pattern):
        os.mkdir(pattern)
    
    temporal = join(subject_dir, 'TemporalRegression_Stage2')
    if not os.path.exists(temporal):
        os.mkdir(temporal)
    
    subject_map = join(subject, 'REST/Preprocess/bp2mni_{downsample}.nii.gz'.format(downsample=downsample))
    
    spatial_dir = join(spatial, '{downsample}_{side}_nosmooth_auto_bp2mni'.format(downsample=downsample, side=side))
    if not os.path.exists(spatial_dir):
        print('\ creating spatial regression directory for ' + subject)
        os.mkdir(spatial_dir)

    pattern_dir = join(pattern, '{downsample}_{side}_nosmooth_auto_bp2mni'.format(downsample=downsample, side=side))
    if not os.path.exists(pattern_dir):
        print('\ creating rsFC pattern directory for ' + subject)
        os.mkdir(pattern_dir)
    
    temporal_dir = join(temporal, '{downsample}_{side}_nosmooth_auto_bp2mni'.format(downsample=downsample, side=side))
    if not os.path.exists(temporal_dir):
        print('\ creating temporal directory for ' + subject)
        os.mkdir(temporal_dir)


    mmthreshImg = join(melodicDir, 'melodic_IC.nii.gz')
            
    stage_1 = join(spatial_dir, '{subject}_stage1'.format(subject=subject))
    if not os.path.exists(stage_1):
        print(subject + 'running with fisher input dual regression stage 1 for ' + mmthreshImg)
        command = 'fsl_glm -i {subject_map} -d {mmthreshImg} -m {thal} -o {stage_1}'.format(subject_map=subject_map, mmthreshImg=mmthreshImg, thal=thal, stage_1=stage_1)
        os.popen(command).read()

    pattern_stage_1 = join(pattern_dir, '{subject}_pattern_stage1'.format(subject=subject))
    if not os.path.exists(pattern_stage_1):
        print(subject + 'running with fisher input dual regression stage 1 for rsFC pattern')
        command = 'fsl_glm -i {subject_map} -d {mmthreshImg} -o {pattern_stage_1}'.format(subject_map=subject_map, mmthreshImg=mmthreshImg, pattern_stage_1=pattern_stage_1)
        os.popen(command).read()

    stage_1_demean = join(spatial_dir, '{subject}_stage1_demeaned'.format(subject=subject))
    if not os.path.exists(stage_1_demean):
        print(subject + 'running with fisher input dual regression stage 1 demean for ' + mmthreshImg)
        command = 'fsl_glm -i {subject_map} -d {mmthreshImg} -m {thal} -o {stage_1_demean} --demean'.format(subject_map=subject_map, mmthreshImg=mmthreshImg, thal=thal, stage_1_demean=stage_1_demean)
        os.popen(command).read()
        
    pattern_stage_1_demean = join(pattern_dir, '{subject}_pattern_stage1_demeaned'.format(subject=subject))
    if not os.path.exists(pattern_stage_1_demean):
        print(subject + 'running with fisher input dual regression stage 1 demean for rsFC pattern')
        command = 'fsl_glm -i {subject_map} -d {mmthreshImg} -o {pattern_stage_1_demean} --demean'.format(subject_map=subject_map, mmthreshImg=mmthreshImg, pattern_stage_1_demean=pattern_stage_1_demean)
        os.popen(command).read()
        

    stage_2 = join(temporal_dir, '{subject}_stage2.nii.gz'.format(subject=subject))
    z_stage_2 = join(temporal_dir, 'z_{subject}_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(z_stage_2):
        print(subject + 'running with fisher input glm stage 2 for ' + mmthreshImg)
        input_d = stage_1
        command = 'fsl_glm -i {subject_map} -d {input_d} -m {thal} -o {stage_2} --out_z={z_stage_2}'.format(subject_map=subject_map, input_d=input_d, thal=thal, stage_2=stage_2, z_stage_2=z_stage_2)
        os.popen(command).read()

    pattern_stage_2 = join(pattern_dir, '{subject}_pattern_stage2.nii.gz'.format(subject=subject))
    z_pattern_stage_2 = join(pattern_dir, 'z_{subject}_pattern_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(z_pattern_stage_2):
        print(subject + 'running with fisher input glm stage 2 for rsFC pattern')
        input_d = pattern_stage_1
        command = 'fsl_glm -i {subject_map} -d {input_d} -o {pattern_stage_2} --out_z={z_pattern_stage_2}'.format(subject_map=subject_map, input_d=input_d, pattern_stage_2=pattern_stage_2, z_pattern_stage_2=z_pattern_stage_2)
        os.popen(command).read()
            
    stage_2_demean = join(temporal_dir, '{subject}_stage2_demeaned.nii.gz'.format(subject=subject))
    z_stage_2_demean = join(temporal_dir, 'z_{subject}_stage2_demeaned.nii.gz'.format(subject=subject))
    if not os.path.exists(z_stage_2_demean):
        print(subject + 'running with fisher input glm stage 2 demean for ' + mmthreshImg)
        input_d = stage_1_demean
        command = 'fsl_glm -i {subject_map} -d {input_d} -m {thal} -o {stage_2_demean} --out_z={z_stage_2_demean} --demean'.format(subject_map=subject_map, input_d=input_d, thal=thal, stage_2_demean=stage_2_demean, z_stage_2_demean=z_stage_2_demean)
        os.popen(command).read()

    pattern_stage_2_demean = join(pattern_dir, '{subject}_pattern_stage2_demeaned.nii.gz'.format(subject=subject))
    z_pattern_stage_2_demean = join(pattern_dir, 'z_{subject}_pattern_stage2_demeaned.nii.gz'.format(subject=subject))        
    if not os.path.exists(z_pattern_stage_2_demean):
        print(subject + ' running with fisher input glm stage 2 demean for rsFC pattern' + mmthreshImg)
        input_d = pattern_stage_1_demean
        command = 'fsl_glm -i {subject_map} -d {input_d} -o {pattern_stage_2_demean} --out_z={z_pattern_stage_2_demean} --demean'.format(subject_map=subject_map, input_d=input_d, pattern_stage_2_demean=pattern_stage_2_demean, z_pattern_stage_2_demean=z_pattern_stage_2_demean)
        os.popen(command).read()

    thresholded = join(temporal_dir, 'z2.3_{subject}_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded):
        print(subject + ' thresholding dual regression output for ' + mmthreshImg)
        command = 'fslmaths {z_stage_2} -thr 2.3 {thresholded}'.format(z_stage_2=z_stage_2, thresholded=thresholded)
        os.popen(command).read()
    
    thresholded_output = join(temporal_dir, 'z2.3_{subject}_stage2_demeaned.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded_output):
        print(subject + ' thresholding dual regression output for ' + mmthreshImg)
        command = 'fslmaths {z_stage_2_demean} -thr 2.3 {thresholded_output}'.format(z_stage_2_demean=z_stage_2_demean, thresholded_output=thresholded_output)
        os.popen(command).read()

    thresholded_pattern = join(pattern_dir, 'z2.3_{subject}_pattern_stage2_demeaned.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded_pattern):
        print(subject + ' thresholding wmSC pattern for ' + mmthreshImg)
        command = 'fslmaths {z_pattern_stage_2_demean} -thr 2.3 {thresholded_pattern}'.format(z_pattern_stage_2_demean=z_pattern_stage_2_demean, thresholded_pattern=thresholded_pattern)
        os.popen(command).read()


    thresholded_pat = join(pattern_dir, 'z2.3_{subject}_pattern_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded_pat):
        print(subject + ' thresholding wmSC pattern for ' + mmthreshImg)
        command = 'fslmaths {z_pattern_stage_2} -thr 2.3 {thresholded_pat}'.format(z_pattern_stage_2=z_pattern_stage_2, thresholded_pat=thresholded_pat)
        os.popen(command).read()



def nosmoothFisherPostMelodicGLM_RSFC (subject, side, sside, hemi, downsample):
    
    mni = 'mni_brain_${downsample}.nii.gz'.format(downsample=downsample)
    thal = 'masks/{hemi}_thalamus_HOSC_60_{downsample}.nii.gz'.format(hemi=hemi, downsample=downsample)
    
    melodicDir='rsFC_ICA_cmd/{downsample}_{side}_masked'.format(downsample=downsample, side=side)
    
    subject_dir = join(subject, 'DualRegression_TemporalICA')
    if not os.path.exists(subject_dir):
        print('\ creating subject_dir for ' + subject)
        os.mkdir(subject_dir)

    spatial = join(subject_dir, 'SpatialRegression_Stage1')
    if not os.path.exists(spatial):
        os.mkdir(spatial)
    
    pattern = join(subject_dir, 'rsFC_pattern')
    if not os.path.exists(pattern):
        os.mkdir(pattern)
    
    temporal = join(subject_dir, 'TemporalRegression_Stage2')
    if not os.path.exists(temporal):
        os.mkdir(temporal)
    
    subject_map = join(subject, 'RSFC/{sside}_{downsample}_fisherZ.nii.gz'.format(sside=sside, downsample=downsample))    
    
    spatial_dir = join(spatial, '{downsample}_{side}_nosmooth_auto'.format(downsample=downsample, side=side))
    if not os.path.exists(spatial_dir):
        print('\ creating spatial regression directory for ' + subject)
        os.mkdir(spatial_dir)

    pattern_dir = join(pattern, '{downsample}_{side}_nosmooth_auto'.format(downsample=downsample, side=side))
    if not os.path.exists(pattern_dir):
        print('\ creating rsFC pattern directory for ' + subject)
        os.mkdir(pattern_dir)
    
    temporal_dir = join(temporal, '{downsample}_{side}_nosmooth_auto'.format(downsample=downsample, side=side))
    if not os.path.exists(temporal_dir):
        print('\ creating temporal directory for ' + subject)
        os.mkdir(temporal_dir)


    mmthreshImg = join(melodicDir, 'melodic_IC.nii.gz')
            
    stage_1 = join(spatial_dir, '{subject}_stage1'.format(subject=subject))
    if not os.path.exists(stage_1):
        print(subject + 'running with fisher input dual regression stage 1 for ' + mmthreshImg)
        command = 'fsl_glm -i {subject_map} -d {mmthreshImg} -m {thal} -o {stage_1}'.format(subject_map=subject_map, mmthreshImg=mmthreshImg, thal=thal, stage_1=stage_1)
        os.popen(command).read()

    pattern_stage_1 = join(pattern_dir, '{subject}_pattern_stage1'.format(subject=subject))
    if not os.path.exists(pattern_stage_1):
        print(subject + 'running with fisher input dual regression stage 1 for rsFC pattern')
        command = 'fsl_glm -i {subject_map} -d {mmthreshImg} -o {pattern_stage_1}'.format(subject_map=subject_map, mmthreshImg=mmthreshImg, pattern_stage_1=pattern_stage_1)
        os.popen(command).read()

    stage_1_demean = join(spatial_dir, '{subject}_stage1_demeaned'.format(subject=subject))
    if not os.path.exists(stage_1_demean):
        print(subject + 'running with fisher input dual regression stage 1 demean for ' + mmthreshImg)
        command = 'fsl_glm -i {subject_map} -d {mmthreshImg} -m {thal} -o {stage_1_demean} --demean'.format(subject_map=subject_map, mmthreshImg=mmthreshImg, thal=thal, stage_1_demean=stage_1_demean)
        os.popen(command).read()
        
    pattern_stage_1_demean = join(pattern_dir, '{subject}_pattern_stage1_demeaned'.format(subject=subject))
    if not os.path.exists(pattern_stage_1_demean):
        print(subject + 'running with fisher input dual regression stage 1 demean for rsFC pattern')
        command = 'fsl_glm -i {subject_map} -d {mmthreshImg} -o {pattern_stage_1_demean} --demean'.format(subject_map=subject_map, mmthreshImg=mmthreshImg, pattern_stage_1_demean=pattern_stage_1_demean)
        os.popen(command).read()
        

    stage_2 = join(temporal_dir, '{subject}_stage2.nii.gz'.format(subject=subject))
    z_stage_2 = join(temporal_dir, 'z_{subject}_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(z_stage_2):
        print(subject + 'running with fisher input glm stage 2 for ' + mmthreshImg)
        input_d = stage_1
        command = 'fsl_glm -i {subject_map} -d {input_d} -m {thal} -o {stage_2} --out_z={z_stage_2}'.format(subject_map=subject_map, input_d=input_d, thal=thal, stage_2=stage_2, z_stage_2=z_stage_2)
        os.popen(command).read()

    pattern_stage_2 = join(pattern_dir, '{subject}_pattern_stage2.nii.gz'.format(subject=subject))
    z_pattern_stage_2 = join(pattern_dir, 'z_{subject}_pattern_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(z_pattern_stage_2):
        print(subject + 'running with fisher input glm stage 2 for rsFC pattern')
        input_d = pattern_stage_1
        command = 'fsl_glm -i {subject_map} -d {input_d} -o {pattern_stage_2} --out_z={z_pattern_stage_2}'.format(subject_map=subject_map, input_d=input_d, pattern_stage_2=pattern_stage_2, z_pattern_stage_2=z_pattern_stage_2)
        os.popen(command).read()
            
    stage_2_demean = join(temporal_dir, '{subject}_stage2_demeaned.nii.gz'.format(subject=subject))
    z_stage_2_demean = join(temporal_dir, 'z_{subject}_stage2_demeaned.nii.gz'.format(subject=subject))
    if not os.path.exists(z_stage_2_demean):
        print(subject + 'running with fisher input glm stage 2 demean for ' + mmthreshImg)
        input_d = stage_1_demean
        command = 'fsl_glm -i {subject_map} -d {input_d} -m {thal} -o {stage_2_demean} --out_z={z_stage_2_demean} --demean'.format(subject_map=subject_map, input_d=input_d, thal=thal, stage_2_demean=stage_2_demean, z_stage_2_demean=z_stage_2_demean)
        os.popen(command).read()

    pattern_stage_2_demean = join(pattern_dir, '{subject}_pattern_stage2_demeaned.nii.gz'.format(subject=subject))
    z_pattern_stage_2_demean = join(pattern_dir, 'z_{subject}_pattern_stage2_demeaned.nii.gz'.format(subject=subject))        
    if not os.path.exists(z_pattern_stage_2_demean):
        print(subject + ' running with fisher input glm stage 2 demean for rsFC pattern' + mmthreshImg)
        input_d = pattern_stage_1_demean
        command = 'fsl_glm -i {subject_map} -d {input_d} -o {pattern_stage_2_demean} --out_z={z_pattern_stage_2_demean} --demean'.format(subject_map=subject_map, input_d=input_d, pattern_stage_2_demean=pattern_stage_2_demean, z_pattern_stage_2_demean=z_pattern_stage_2_demean)
        os.popen(command).read()

    thresholded = join(temporal_dir, 'z2.3_{subject}_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded):
        print(subject + ' thresholding dual regression output for ' + mmthreshImg)
        command = 'fslmaths {z_stage_2} -thr 2.3 {thresholded}'.format(z_stage_2=z_stage_2, thresholded=thresholded)
        os.popen(command).read()
    
    thresholded_output = join(temporal_dir, 'z2.3_{subject}_stage2_demeaned.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded_output):
        print(subject + ' thresholding dual regression output for ' + mmthreshImg)
        command = 'fslmaths {z_stage_2_demean} -thr 2.3 {thresholded_output}'.format(z_stage_2_demean=z_stage_2_demean, thresholded_output=thresholded_output)
        os.popen(command).read()

    thresholded_pattern = join(pattern_dir, 'z2.3_{subject}_pattern_stage2_demeaned.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded_pattern):
        print(subject + ' thresholding wmSC pattern for ' + mmthreshImg)
        command = 'fslmaths {z_pattern_stage_2_demean} -thr 2.3 {thresholded_pattern}'.format(z_pattern_stage_2_demean=z_pattern_stage_2_demean, thresholded_pattern=thresholded_pattern)
        os.popen(command).read()


    thresholded_pat = join(pattern_dir, 'z2.3_{subject}_pattern_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded_pat):
        print(subject + ' thresholding wmSC pattern for ' + mmthreshImg)
        command = 'fslmaths {z_pattern_stage_2} -thr 2.3 {thresholded_pat}'.format(z_pattern_stage_2=z_pattern_stage_2, thresholded_pat=thresholded_pat)
        os.popen(command).read()



def fisherPostMelodicGLM_re_bp2mni (subject, side, sside, hemi, downsample, spatialsmooth):
    
    mni = 'mni_brain_{downsample}.nii.gz'.format(downsample=downsample)
    thal = 'masks/{side}_thalamus_HOSC_60_{downsample}.nii.gz'.format(side=side, downsample=downsample)
    melodicDir='rsFC_ICA_cmd/{downsample}_{side}_{spatialsmooth}_masked'.format(downsample=downsample, side=side, spatialsmooth=spatialsmooth)

    re_dir = join(subject, 're_DualRegression_TemporalICA')
    if not os.path.exists(re_dir):
        os.mkdir(re_dir)

    subject_dir = join(re_dir, 'bp2mni')
    if not os.path.exists(subject_dir):
        os.mkdir(subject_dir)

    spatial = join(subject_dir, 'SpatialRegression_Stage1')
    if not os.path.exists(spatial):
        os.mkdir(spatial)
    
    pattern = join(subject_dir, 'rsFC_pattern')
    if not os.path.exists(pattern):
        os.mkdir(pattern)
    
    temporal = join(subject_dir, 'TemporalRegression_Stage2')
    if not os.path.exists(temporal):
        os.mkdir(temporal)
   
    subject_map = join(subject, 'REST/Preprocess/bp2mni_{downsample}.nii.gz'.format(downsample=downsample))
    
    spatial_dir = join(spatial, '{downsample}_{side}_{spatialsmooth}_auto'.format(downsample=downsample, side=side, spatialsmooth=spatialsmooth))
    if not os.path.exists(spatial_dir):
        print('\ creating spatial regression directory for ' + subject)
        os.mkdir(spatial_dir)

    pattern_dir = join(pattern, '{downsample}_{side}_{spatialsmooth}_auto'.format(downsample=downsample, side=side, spatialsmooth=spatialsmooth))
    if not os.path.exists(pattern_dir):
        print('\ creating rsFC pattern directory for ' + subject)
        os.mkdir(pattern_dir)
    
    temporal_dir = join(temporal, '{downsample}_{side}_{spatialsmooth}_auto'.format(downsample=downsample, side=side, spatialsmooth=spatialsmooth))
    if not os.path.exists(temporal_dir):
        print('\ creating temporal directory for ' + subject)
        os.mkdir(temporal_dir)

    mmthreshImg = join(melodicDir, 'melodic_IC.nii.gz')
            
    stage_1 = join(spatial_dir, '{subject}_stage1'.format(subject=subject))
    if not os.path.exists(stage_1):
        print(subject + 'running with fisher input dual regression stage 1 for ' + mmthreshImg)
        command = 'fsl_glm -i {subject_map} -d {mmthreshImg} -m {thal} -o {stage_1}'.format(subject_map=subject_map, mmthreshImg=mmthreshImg, thal=thal, stage_1=stage_1)
        os.popen(command).read()

    pattern_stage_1 = join(pattern_dir, '{subject}_pattern_stage1'.format(subject=subject))
    if not os.path.exists(pattern_stage_1):
        print(subject + 'running with fisher input dual regression stage 1 for rsFC pattern')
        command = 'fsl_glm -i {subject_map} -d {mmthreshImg} -o {pattern_stage_1}'.format(subject_map=subject_map, mmthreshImg=mmthreshImg, pattern_stage_1=pattern_stage_1)
        os.popen(command).read()

    stage_1_demean = join(spatial_dir, '{subject}_stage1_demeaned'.format(subject=subject))
    if not os.path.exists(stage_1_demean):
        print(subject + 'running with fisher input dual regression stage 1 demean for ' + mmthreshImg)
        command = 'fsl_glm -i {subject_map} -d {mmthreshImg} -m {thal} -o {stage_1_demean} --demean'.format(subject_map=subject_map, mmthreshImg=mmthreshImg, thal=thal, stage_1_demean=stage_1_demean)
        os.popen(command).read()
        
    pattern_stage_1_demean = join(pattern_dir, '{subject}_pattern_stage1_demeaned'.format(subject=subject))
    if not os.path.exists(pattern_stage_1_demean):
        print(subject + 'running with fisher input dual regression stage 1 demean for rsFC pattern')
        command = 'fsl_glm -i {subject_map} -d {mmthreshImg} -o {pattern_stage_1_demean} --demean'.format(subject_map=subject_map, mmthreshImg=mmthreshImg, pattern_stage_1_demean=pattern_stage_1_demean)
        os.popen(command).read()
        

    stage_2 = join(temporal_dir, '{subject}_stage2.nii.gz'.format(subject=subject))
    z_stage_2 = join(temporal_dir, 'z_{subject}_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(z_stage_2):
        print(subject + 'running with fisher input glm stage 2 for ' + mmthreshImg)
        input_d = stage_1
        command = 'fsl_glm -i {subject_map} -d {input_d} -m {thal} -o {stage_2} --out_z={z_stage_2}'.format(subject_map=subject_map, input_d=input_d, thal=thal, stage_2=stage_2, z_stage_2=z_stage_2)
        os.popen(command).read()

    pattern_stage_2 = join(pattern_dir, '{subject}_pattern_stage2.nii.gz'.format(subject=subject))
    z_pattern_stage_2 = join(pattern_dir, 'z_{subject}_pattern_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(z_pattern_stage_2):
        print(subject + 'running with fisher input glm stage 2 for rsFC pattern')
        input_d = pattern_stage_1
        command = 'fsl_glm -i {subject_map} -d {input_d} -o {pattern_stage_2} --out_z={z_pattern_stage_2}'.format(subject_map=subject_map, input_d=input_d, pattern_stage_2=pattern_stage_2, z_pattern_stage_2=z_pattern_stage_2)
        os.popen(command).read()
            
    stage_2_demean = join(temporal_dir, '{subject}_stage2_demeaned.nii.gz'.format(subject=subject))
    z_stage_2_demean = join(temporal_dir, 'z_{subject}_stage2_demeaned.nii.gz'.format(subject=subject))
    if not os.path.exists(z_stage_2_demean):
        print(subject + 'running with fisher input glm stage 2 demean for ' + mmthreshImg)
        input_d = stage_1_demean
        command = 'fsl_glm -i {subject_map} -d {input_d} -m {thal} -o {stage_2_demean} --out_z={z_stage_2_demean} --demean'.format(subject_map=subject_map, input_d=input_d, thal=thal, stage_2_demean=stage_2_demean, z_stage_2_demean=z_stage_2_demean)
        os.popen(command).read()

    pattern_stage_2_demean = join(pattern_dir, '{subject}_pattern_stage2_demeaned.nii.gz'.format(subject=subject))
    z_pattern_stage_2_demean = join(pattern_dir, 'z_{subject}_pattern_stage2_demeaned.nii.gz'.format(subject=subject))        
    if not os.path.exists(z_pattern_stage_2_demean):
        print(subject + ' running with fisher input glm stage 2 demean for rsFC pattern' + mmthreshImg)
        input_d = pattern_stage_1_demean
        command = 'fsl_glm -i {subject_map} -d {input_d} -o {pattern_stage_2_demean} --out_z={z_pattern_stage_2_demean} --demean'.format(subject_map=subject_map, input_d=input_d, pattern_stage_2_demean=pattern_stage_2_demean, z_pattern_stage_2_demean=z_pattern_stage_2_demean)
        os.popen(command).read()

    thresholded = join(temporal_dir, 'z2.3_{subject}_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded):
        print(subject + ' thresholding dual regression output for ' + mmthreshImg)
        command = 'fslmaths {z_stage_2} -thr 2.3 {thresholded}'.format(z_stage_2=z_stage_2, thresholded=thresholded)
        os.popen(command).read()
        
    thresholded_output = join(temporal_dir, 'z2.3_{subject}_stage2_demeaned.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded_output):
        print(subject + ' thresholding dual regression output for ' + mmthreshImg)
        command = 'fslmaths {z_stage_2_demean} -thr 2.3 {thresholded_output}'.format(z_stage_2_demean=z_stage_2_demean, thresholded_output=thresholded_output)
        os.popen(command).read()

    thresholded_pat = join(pattern_dir, 'z2.3_{subject}_pattern_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded_pat):
        print(subject + ' thresholding wmSC pattern for ' + mmthreshImg)
        command = 'fslmaths {z_pattern_stage_2} -thr 2.3 {thresholded_pat}'.format(z_pattern_stage_2=z_pattern_stage_2, thresholded_pat=thresholded_pat)
        os.popen(command).read()

    thresholded_pattern = join(pattern_dir, 'z2.3_{subject}_pattern_stage2_demeaned.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded_pattern):
        print(subject + ' thresholding wmSC pattern for ' + mmthreshImg)
        command = 'fslmaths {z_pattern_stage_2_demean} -thr 2.3 {thresholded_pattern}'.format(z_pattern_stage_2_demean=z_pattern_stage_2_demean, thresholded_pattern=thresholded_pattern)
        os.popen(command).read()



def nosmoothFisherPostMelodicGLM_re_bp2mni (subject, side, sside, hemi, downsample):
    
    thal = 'masks/{side}_thalamus_HOSC_60_{downsample}.nii.gz'.format(side=side, downsample=downsample)
    
    melodicDir='rsFC_ICA_cmd/re_{downsample}_{side}_masked'.format(downsample=downsample, side=side)
    
    re_dir = join(subject, 're_DualRegression_TemporalICA')
    if not os.path.exists(re_dir):
        os.mkdir(re_dir)

    subject_dir = join(re_dir, 'bp2mni')
    if not os.path.exists(subject_dir):
        os.mkdir(subject_dir)

    spatial = join(subject_dir, 'SpatialRegression_Stage1')
    if not os.path.exists(spatial):
        os.mkdir(spatial)
    
    pattern = join(subject_dir, 'rsFC_pattern')
    if not os.path.exists(pattern):
        os.mkdir(pattern)
    
    temporal = join(subject_dir, 'TemporalRegression_Stage2')
    if not os.path.exists(temporal):
        os.mkdir(temporal)
    
    subject_map = '{subject}/REST/Preprocess/with_spatial_smoothing/bp2mni_{downsample}.nii.gz'.format(subject=subject, downsample=downsample)
    
    spatial_dir = join(spatial, 're_{downsample}_{side}_auto'.format(downsample=downsample, side=side))
    if not os.path.exists(spatial_dir):
        os.mkdir(spatial_dir)

    pattern_dir = join(pattern, 're_{downsample}_{side}_auto'.format(downsample=downsample, side=side))
    if not os.path.exists(pattern_dir):
        os.mkdir(pattern_dir)
    
    temporal_dir = join(temporal, 're_{downsample}_{side}_auto'.format(downsample=downsample, side=side))
    if not os.path.exists(temporal_dir):
        os.mkdir(temporal_dir)


    melodicImg = join(melodicDir, 'melodic_IC.nii.gz')
            
    stage_1 = join(spatial_dir, '{subject}_stage1'.format(subject=subject))
    if not os.path.exists(stage_1):
        print(subject + 'running with fisher input dual regression stage 1 for ' + melodicImg)
        command = 'fsl_glm -i {subject_map} -d {melodicImg} -m {thal} -o {stage_1}'.format(subject_map=subject_map, melodicImg=melodicImg, thal=thal, stage_1=stage_1)
        os.popen(command).read()

    pattern_stage_1 = join(pattern_dir, '{subject}_pattern_stage1'.format(subject=subject))
    if not os.path.exists(pattern_stage_1):
        print(subject + 'running with fisher input dual regression stage 1 for rsFC pattern')
        command = 'fsl_glm -i {subject_map} -d {melodicImg} -o {pattern_stage_1}'.format(subject_map=subject_map, melodicImg=melodicImg, pattern_stage_1=pattern_stage_1)
        os.popen(command).read()

    stage_1_demean = join(spatial_dir, '{subject}_stage1_demeaned'.format(subject=subject))
    if not os.path.exists(stage_1_demean):
        print(subject + 'running with fisher input dual regression stage 1 demean for ' + melodicImg)
        command = 'fsl_glm -i {subject_map} -d {melodicImg} -m {thal} -o {stage_1_demean} --demean'.format(subject_map=subject_map, melodicImg=melodicImg, thal=thal, stage_1_demean=stage_1_demean)
        os.popen(command).read()
        
    pattern_stage_1_demean = join(pattern_dir, '{subject}_pattern_stage1_demeaned'.format(subject=subject))
    if not os.path.exists(pattern_stage_1_demean):
        print(subject + 'running with fisher input dual regression stage 1 demean for rsFC pattern')
        command = 'fsl_glm -i {subject_map} -d {melodicImg} -o {pattern_stage_1_demean} --demean'.format(subject_map=subject_map, melodicImg=melodicImg, pattern_stage_1_demean=pattern_stage_1_demean)
        os.popen(command).read()
        

    stage_2 = join(temporal_dir, '{subject}_stage2.nii.gz'.format(subject=subject))
    z_stage_2 = join(temporal_dir, 'z_{subject}_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(z_stage_2):
        print(subject + 'running with fisher input glm stage 2 for ' + melodicImg)
        input_d = stage_1
        command = 'fsl_glm -i {subject_map} -d {input_d} -m {thal} -o {stage_2} --out_z={z_stage_2}'.format(subject_map=subject_map, input_d=input_d, thal=thal, stage_2=stage_2, z_stage_2=z_stage_2)
        os.popen(command).read()

    pattern_stage_2 = join(pattern_dir, '{subject}_pattern_stage2.nii.gz'.format(subject=subject))
    z_pattern_stage_2 = join(pattern_dir, 'z_{subject}_pattern_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(z_pattern_stage_2):
        print(subject + 'running with fisher input glm stage 2 for rsFC pattern')
        input_d = pattern_stage_1
        command = 'fsl_glm -i {subject_map} -d {input_d} -o {pattern_stage_2} --out_z={z_pattern_stage_2}'.format(subject_map=subject_map, input_d=input_d, pattern_stage_2=pattern_stage_2, z_pattern_stage_2=z_pattern_stage_2)
        os.popen(command).read()
            
    stage_2_demean = join(temporal_dir, '{subject}_stage2_demeaned.nii.gz'.format(subject=subject))
    z_stage_2_demean = join(temporal_dir, 'z_{subject}_stage2_demeaned.nii.gz'.format(subject=subject))
    if not os.path.exists(z_stage_2_demean):
        print(subject + 'running with fisher input glm stage 2 demean for ' + melodicImg)
        input_d = stage_1_demean
        command = 'fsl_glm -i {subject_map} -d {input_d} -m {thal} -o {stage_2_demean} --out_z={z_stage_2_demean} --demean'.format(subject_map=subject_map, input_d=input_d, thal=thal, stage_2_demean=stage_2_demean, z_stage_2_demean=z_stage_2_demean)
        os.popen(command).read()

    pattern_stage_2_demean = join(pattern_dir, '{subject}_pattern_stage2_demeaned.nii.gz'.format(subject=subject))
    z_pattern_stage_2_demean = join(pattern_dir, 'z_{subject}_pattern_stage2_demeaned.nii.gz'.format(subject=subject))        
    if not os.path.exists(z_pattern_stage_2_demean):
        print(subject + ' running with fisher input glm stage 2 demean for rsFC pattern' + melodicImg)
        input_d = pattern_stage_1_demean
        command = 'fsl_glm -i {subject_map} -d {input_d} -o {pattern_stage_2_demean} --out_z={z_pattern_stage_2_demean} --demean'.format(subject_map=subject_map, input_d=input_d, pattern_stage_2_demean=pattern_stage_2_demean, z_pattern_stage_2_demean=z_pattern_stage_2_demean)
        os.popen(command).read()

    thresholded = join(temporal_dir, 'z2.3_{subject}_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded):
        print(subject + ' thresholding dual regression output for ' + melodicImg)
        command = 'fslmaths {z_stage_2} -thr 2.3 {thresholded}'.format(z_stage_2=z_stage_2, thresholded=thresholded)
        os.popen(command).read()
    
    thresholded_output = join(temporal_dir, 'z2.3_{subject}_stage2_demeaned.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded_output):
        print(subject + ' thresholding dual regression output for ' + melodicImg)
        command = 'fslmaths {z_stage_2_demean} -thr 2.3 {thresholded_output}'.format(z_stage_2_demean=z_stage_2_demean, thresholded_output=thresholded_output)
        os.popen(command).read()

    thresholded_pattern = join(pattern_dir, 'z2.3_{subject}_pattern_stage2_demeaned.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded_pattern):
        print(subject + ' thresholding wmSC pattern for ' + melodicImg)
        command = 'fslmaths {z_pattern_stage_2_demean} -thr 2.3 {thresholded_pattern}'.format(z_pattern_stage_2_demean=z_pattern_stage_2_demean, thresholded_pattern=thresholded_pattern)
        os.popen(command).read()


    thresholded_pat = join(pattern_dir, 'z2.3_{subject}_pattern_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded_pat):
        print(subject + ' thresholding wmSC pattern for ' + melodicImg)
        command = 'fslmaths {z_pattern_stage_2} -thr 2.3 {thresholded_pat}'.format(z_pattern_stage_2=z_pattern_stage_2, thresholded_pat=thresholded_pat)
        os.popen(command).read()



def fisherPostMelodicGLM_re_RSFC (subject, side, sside, hemi, downsample, spatialsmooth):
    
    mni = 'mni_brain_{downsample}.nii.gz'.format(downsample=downsample)
    thal = 'masks/{side}_thalamus_HOSC_60_{downsample}.nii.gz'.format(side=side, downsample=downsample)
    melodicDir='rsFC_ICA_cmd/{downsample}_{side}_{spatialsmooth}_masked'.format(downsample=downsample, side=side, spatialsmooth=spatialsmooth)

    re_dir = join(subject, 're_DualRegression_TemporalICA')
    if not os.path.exists(re_dir):
        os.mkdir(re_dir)

    subject_dir = join(re_dir, 'RSFC')
    if not os.path.exists(subject_dir):
        os.mkdir(subject_dir)

    spatial = join(subject_dir, 'SpatialRegression_Stage1')
    if not os.path.exists(spatial):
        os.mkdir(spatial)
    
    pattern = join(subject_dir, 'rsFC_pattern')
    if not os.path.exists(pattern):
        os.mkdir(pattern)
    
    temporal = join(subject_dir, 'TemporalRegression_Stage2')
    if not os.path.exists(temporal):
        os.mkdir(temporal)
   
    subject_map = join(subject, 'RSFC/{sside}_{downsample}_fisherZ_s3.nii.gz'.format(sside=sside, downsample=downsample))    
    
    spatial_dir = join(spatial, '{downsample}_{side}_{spatialsmooth}_auto'.format(downsample=downsample, side=side, spatialsmooth=spatialsmooth))
    if not os.path.exists(spatial_dir):
        os.mkdir(spatial_dir)

    pattern_dir = join(pattern, '{downsample}_{side}_{spatialsmooth}_auto'.format(downsample=downsample, side=side, spatialsmooth=spatialsmooth))
    if not os.path.exists(pattern_dir):
        os.mkdir(pattern_dir)
    
    temporal_dir = join(temporal, '{downsample}_{side}_{spatialsmooth}_auto'.format(downsample=downsample, side=side, spatialsmooth=spatialsmooth))
    if not os.path.exists(temporal_dir):
        os.mkdir(temporal_dir)

    melodicImg = join(melodicDir, 'melodic_IC.nii.gz')
            
    stage_1 = join(spatial_dir, '{subject}_stage1'.format(subject=subject))
    if not os.path.exists(stage_1):
        print(subject + 'running with fisher input dual regression stage 1 for ' + melodicImg)
        command = 'fsl_glm -i {subject_map} -d {melodicImg} -m {thal} -o {stage_1}'.format(subject_map=subject_map, melodicImg=melodicImg, thal=thal, stage_1=stage_1)
        os.popen(command).read()

    pattern_stage_1 = join(pattern_dir, '{subject}_pattern_stage1'.format(subject=subject))
    if not os.path.exists(pattern_stage_1):
        print(subject + 'running with fisher input dual regression stage 1 for rsFC pattern')
        command = 'fsl_glm -i {subject_map} -d {melodicImg} -o {pattern_stage_1}'.format(subject_map=subject_map, melodicImg=melodicImg, pattern_stage_1=pattern_stage_1)
        os.popen(command).read()

    stage_1_demean = join(spatial_dir, '{subject}_stage1_demeaned'.format(subject=subject))
    if not os.path.exists(stage_1_demean):
        print(subject + 'running with fisher input dual regression stage 1 demean for ' + melodicImg)
        command = 'fsl_glm -i {subject_map} -d {melodicImg} -m {thal} -o {stage_1_demean} --demean'.format(subject_map=subject_map, melodicImg=melodicImg, thal=thal, stage_1_demean=stage_1_demean)
        os.popen(command).read()
        
    pattern_stage_1_demean = join(pattern_dir, '{subject}_pattern_stage1_demeaned'.format(subject=subject))
    if not os.path.exists(pattern_stage_1_demean):
        print(subject + 'running with fisher input dual regression stage 1 demean for rsFC pattern')
        command = 'fsl_glm -i {subject_map} -d {melodicImg} -o {pattern_stage_1_demean} --demean'.format(subject_map=subject_map, melodicImg=melodicImg, pattern_stage_1_demean=pattern_stage_1_demean)
        os.popen(command).read()
        

    stage_2 = join(temporal_dir, '{subject}_stage2.nii.gz'.format(subject=subject))
    z_stage_2 = join(temporal_dir, 'z_{subject}_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(z_stage_2):
        print(subject + 'running with fisher input glm stage 2 for ' + melodicImg)
        input_d = stage_1
        command = 'fsl_glm -i {subject_map} -d {input_d} -m {thal} -o {stage_2} --out_z={z_stage_2}'.format(subject_map=subject_map, input_d=input_d, thal=thal, stage_2=stage_2, z_stage_2=z_stage_2)
        os.popen(command).read()

    pattern_stage_2 = join(pattern_dir, '{subject}_pattern_stage2.nii.gz'.format(subject=subject))
    z_pattern_stage_2 = join(pattern_dir, 'z_{subject}_pattern_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(z_pattern_stage_2):
        print(subject + 'running with fisher input glm stage 2 for rsFC pattern')
        input_d = pattern_stage_1
        command = 'fsl_glm -i {subject_map} -d {input_d} -o {pattern_stage_2} --out_z={z_pattern_stage_2}'.format(subject_map=subject_map, input_d=input_d, pattern_stage_2=pattern_stage_2, z_pattern_stage_2=z_pattern_stage_2)
        os.popen(command).read()
            
    stage_2_demean = join(temporal_dir, '{subject}_stage2_demeaned.nii.gz'.format(subject=subject))
    z_stage_2_demean = join(temporal_dir, 'z_{subject}_stage2_demeaned.nii.gz'.format(subject=subject))
    if not os.path.exists(z_stage_2_demean):
        print(subject + 'running with fisher input glm stage 2 demean for ' + melodicImg)
        input_d = stage_1_demean
        command = 'fsl_glm -i {subject_map} -d {input_d} -m {thal} -o {stage_2_demean} --out_z={z_stage_2_demean} --demean'.format(subject_map=subject_map, input_d=input_d, thal=thal, stage_2_demean=stage_2_demean, z_stage_2_demean=z_stage_2_demean)
        os.popen(command).read()

    pattern_stage_2_demean = join(pattern_dir, '{subject}_pattern_stage2_demeaned.nii.gz'.format(subject=subject))
    z_pattern_stage_2_demean = join(pattern_dir, 'z_{subject}_pattern_stage2_demeaned.nii.gz'.format(subject=subject))        
    if not os.path.exists(z_pattern_stage_2_demean):
        print(subject + ' running with fisher input glm stage 2 demean for rsFC pattern' + melodicImg)
        input_d = pattern_stage_1_demean
        command = 'fsl_glm -i {subject_map} -d {input_d} -o {pattern_stage_2_demean} --out_z={z_pattern_stage_2_demean} --demean'.format(subject_map=subject_map, input_d=input_d, pattern_stage_2_demean=pattern_stage_2_demean, z_pattern_stage_2_demean=z_pattern_stage_2_demean)
        os.popen(command).read()

    thresholded = join(temporal_dir, 'z2.3_{subject}_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded):
        print(subject + ' thresholding dual regression output for ' + melodicImg)
        command = 'fslmaths {z_stage_2} -thr 2.3 {thresholded}'.format(z_stage_2=z_stage_2, thresholded=thresholded)
        os.popen(command).read()
        
    thresholded_output = join(temporal_dir, 'z2.3_{subject}_stage2_demeaned.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded_output):
        print(subject + ' thresholding dual regression output for ' + melodicImg)
        command = 'fslmaths {z_stage_2_demean} -thr 2.3 {thresholded_output}'.format(z_stage_2_demean=z_stage_2_demean, thresholded_output=thresholded_output)
        os.popen(command).read()

    thresholded_pat = join(pattern_dir, 'z2.3_{subject}_pattern_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded_pat):
        print(subject + ' thresholding wmSC pattern for ' + melodicImg)
        command = 'fslmaths {z_pattern_stage_2} -thr 2.3 {thresholded_pat}'.format(z_pattern_stage_2=z_pattern_stage_2, thresholded_pat=thresholded_pat)
        os.popen(command).read()

    thresholded_pattern = join(pattern_dir, 'z2.3_{subject}_pattern_stage2_demeaned.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded_pattern):
        print(subject + ' thresholding wmSC pattern for ' + melodicImg)
        command = 'fslmaths {z_pattern_stage_2_demean} -thr 2.3 {thresholded_pattern}'.format(z_pattern_stage_2_demean=z_pattern_stage_2_demean, thresholded_pattern=thresholded_pattern)
        os.popen(command).read()



def nosmoothFisherPostMelodicGLM_re_RSFC (subject, side, sside, hemi, downsample):
    
    thal = 'masks/{side}_thalamus_HOSC_60_{downsample}.nii.gz'.format(side=side, downsample=downsample)
    
    melodicDir='rsFC_ICA_cmd/re_{downsample}_{side}_masked'.format(downsample=downsample, side=side)
    
    re_dir = join(subject, 're_DualRegression_TemporalICA')
    if not os.path.exists(re_dir):
        os.mkdir(re_dir)

    subject_dir = join(re_dir, 'RSFC')
    if not os.path.exists(subject_dir):
        os.mkdir(subject_dir)

    spatial = join(subject_dir, 'SpatialRegression_Stage1')
    if not os.path.exists(spatial):
        os.mkdir(spatial)
    
    pattern = join(subject_dir, 'rsFC_pattern')
    if not os.path.exists(pattern):
        os.mkdir(pattern)
    
    temporal = join(subject_dir, 'TemporalRegression_Stage2')
    if not os.path.exists(temporal):
        os.mkdir(temporal)
    
    subject_map = '{subject}/RSFC/with_spatial_smoothing/{sside}_{downsample}_fisherZ.nii.gz'.format(subject=subject, sside=sside, downsample=downsample)
    
    spatial_dir = join(spatial, 're_{downsample}_{side}_auto'.format(downsample=downsample, side=side))
    if not os.path.exists(spatial_dir):
        os.mkdir(spatial_dir)

    pattern_dir = join(pattern, 're_{downsample}_{side}_auto'.format(downsample=downsample, side=side))
    if not os.path.exists(pattern_dir):
        os.mkdir(pattern_dir)
    
    temporal_dir = join(temporal, 're_{downsample}_{side}_auto'.format(downsample=downsample, side=side))
    if not os.path.exists(temporal_dir):
        os.mkdir(temporal_dir)


    melodicImg = join(melodicDir, 'melodic_IC.nii.gz')
            
    stage_1 = join(spatial_dir, '{subject}_stage1'.format(subject=subject))
    if not os.path.exists(stage_1):
        print(subject + 'running with fisher input dual regression stage 1 for ' + melodicImg)
        command = 'fsl_glm -i {subject_map} -d {melodicImg} -m {thal} -o {stage_1}'.format(subject_map=subject_map, melodicImg=melodicImg, thal=thal, stage_1=stage_1)
        os.popen(command).read()

    pattern_stage_1 = join(pattern_dir, '{subject}_pattern_stage1'.format(subject=subject))
    if not os.path.exists(pattern_stage_1):
        print(subject + 'running with fisher input dual regression stage 1 for rsFC pattern')
        command = 'fsl_glm -i {subject_map} -d {melodicImg} -o {pattern_stage_1}'.format(subject_map=subject_map, melodicImg=melodicImg, pattern_stage_1=pattern_stage_1)
        os.popen(command).read()

    stage_1_demean = join(spatial_dir, '{subject}_stage1_demeaned'.format(subject=subject))
    if not os.path.exists(stage_1_demean):
        print(subject + 'running with fisher input dual regression stage 1 demean for ' + melodicImg)
        command = 'fsl_glm -i {subject_map} -d {melodicImg} -m {thal} -o {stage_1_demean} --demean'.format(subject_map=subject_map, melodicImg=melodicImg, thal=thal, stage_1_demean=stage_1_demean)
        os.popen(command).read()
        
    pattern_stage_1_demean = join(pattern_dir, '{subject}_pattern_stage1_demeaned'.format(subject=subject))
    if not os.path.exists(pattern_stage_1_demean):
        print(subject + 'running with fisher input dual regression stage 1 demean for rsFC pattern')
        command = 'fsl_glm -i {subject_map} -d {melodicImg} -o {pattern_stage_1_demean} --demean'.format(subject_map=subject_map, melodicImg=melodicImg, pattern_stage_1_demean=pattern_stage_1_demean)
        os.popen(command).read()
        

    stage_2 = join(temporal_dir, '{subject}_stage2.nii.gz'.format(subject=subject))
    z_stage_2 = join(temporal_dir, 'z_{subject}_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(z_stage_2):
        print(subject + 'running with fisher input glm stage 2 for ' + melodicImg)
        input_d = stage_1
        command = 'fsl_glm -i {subject_map} -d {input_d} -m {thal} -o {stage_2} --out_z={z_stage_2}'.format(subject_map=subject_map, input_d=input_d, thal=thal, stage_2=stage_2, z_stage_2=z_stage_2)
        os.popen(command).read()

    pattern_stage_2 = join(pattern_dir, '{subject}_pattern_stage2.nii.gz'.format(subject=subject))
    z_pattern_stage_2 = join(pattern_dir, 'z_{subject}_pattern_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(z_pattern_stage_2):
        print(subject + 'running with fisher input glm stage 2 for rsFC pattern')
        input_d = pattern_stage_1
        command = 'fsl_glm -i {subject_map} -d {input_d} -o {pattern_stage_2} --out_z={z_pattern_stage_2}'.format(subject_map=subject_map, input_d=input_d, pattern_stage_2=pattern_stage_2, z_pattern_stage_2=z_pattern_stage_2)
        os.popen(command).read()
            
    stage_2_demean = join(temporal_dir, '{subject}_stage2_demeaned.nii.gz'.format(subject=subject))
    z_stage_2_demean = join(temporal_dir, 'z_{subject}_stage2_demeaned.nii.gz'.format(subject=subject))
    if not os.path.exists(z_stage_2_demean):
        print(subject + 'running with fisher input glm stage 2 demean for ' + melodicImg)
        input_d = stage_1_demean
        command = 'fsl_glm -i {subject_map} -d {input_d} -m {thal} -o {stage_2_demean} --out_z={z_stage_2_demean} --demean'.format(subject_map=subject_map, input_d=input_d, thal=thal, stage_2_demean=stage_2_demean, z_stage_2_demean=z_stage_2_demean)
        os.popen(command).read()

    pattern_stage_2_demean = join(pattern_dir, '{subject}_pattern_stage2_demeaned.nii.gz'.format(subject=subject))
    z_pattern_stage_2_demean = join(pattern_dir, 'z_{subject}_pattern_stage2_demeaned.nii.gz'.format(subject=subject))        
    if not os.path.exists(z_pattern_stage_2_demean):
        print(subject + ' running with fisher input glm stage 2 demean for rsFC pattern' + melodicImg)
        input_d = pattern_stage_1_demean
        command = 'fsl_glm -i {subject_map} -d {input_d} -o {pattern_stage_2_demean} --out_z={z_pattern_stage_2_demean} --demean'.format(subject_map=subject_map, input_d=input_d, pattern_stage_2_demean=pattern_stage_2_demean, z_pattern_stage_2_demean=z_pattern_stage_2_demean)
        os.popen(command).read()

    thresholded = join(temporal_dir, 'z2.3_{subject}_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded):
        print(subject + ' thresholding dual regression output for ' + melodicImg)
        command = 'fslmaths {z_stage_2} -thr 2.3 {thresholded}'.format(z_stage_2=z_stage_2, thresholded=thresholded)
        os.popen(command).read()
    
    thresholded_output = join(temporal_dir, 'z2.3_{subject}_stage2_demeaned.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded_output):
        print(subject + ' thresholding dual regression output for ' + melodicImg)
        command = 'fslmaths {z_stage_2_demean} -thr 2.3 {thresholded_output}'.format(z_stage_2_demean=z_stage_2_demean, thresholded_output=thresholded_output)
        os.popen(command).read()

    thresholded_pattern = join(pattern_dir, 'z2.3_{subject}_pattern_stage2_demeaned.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded_pattern):
        print(subject + ' thresholding wmSC pattern for ' + melodicImg)
        command = 'fslmaths {z_pattern_stage_2_demean} -thr 2.3 {thresholded_pattern}'.format(z_pattern_stage_2_demean=z_pattern_stage_2_demean, thresholded_pattern=thresholded_pattern)
        os.popen(command).read()


    thresholded_pat = join(pattern_dir, 'z2.3_{subject}_pattern_stage2.nii.gz'.format(subject=subject))
    if not os.path.exists(thresholded_pat):
        print(subject + ' thresholding wmSC pattern for ' + melodicImg)
        command = 'fslmaths {z_pattern_stage_2} -thr 2.3 {thresholded_pat}'.format(z_pattern_stage_2=z_pattern_stage_2, thresholded_pat=thresholded_pat)
        os.popen(command).read()


    

if __name__== "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--subject', '-subj', nargs=1, type=str)
	parser.add_argument('--side', '-side', nargs=1, help = 'left, right, or bi', type=str)
	parser.add_argument('--sside', '-sside', nargs=1, help = 'L, R or Bi', type=str)
	parser.add_argument('--hemi', '-hemi', nargs=1, help = 'lh or rh', type=str)
	parser.add_argument('--downsample', '-ds', nargs=1,  help = 'e.g., ds3; none if no downsampling', type=str)
        parser.add_argument('--spatialsmooth', '-fwhm', nargs=1,  help = 'e.g., fwhm6', type=str)
	args = parser.parse_args()

        nosmoothFisherPostMelodicGLM_bp2mni(args.subject[0], args.side[0], args.sside[0], args.hemi[0], args.downsample[0])
        #nosmoothFisherPostMelodicGLM_RSFC(args.subject[0], args.side[0], args.sside[0], args.hemi[0], args.downsample[0])
        fisherPostMelodicGLM_re_bp2mni(args.subject[0], args.side[0], args.sside[0], args.hemi[0], args.downsample[0], args.spatialsmooth[0])
        nosmoothFisherPostMelodicGLM_re_bp2mni(args.subject[0], args.side[0], args.sside[0], args.hemi[0], args.downsample[0])
        #fisherPostMelodicGLM_re_RSFC(args.subject[0], args.side[0], args.sside[0], args.hemi[0], args.downsample[0], args.spatialsmooth[0])
        #nosmoothFisherPostMelodicGLM_re_RSFC(args.subject[0], args.side[0], args.sside[0], args.hemi[0], args.downsample[0])
