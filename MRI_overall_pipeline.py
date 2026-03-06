import os
import nibabel as nib
import SimpleITK as sitk
import ants
import numpy as np
import time
from pyrobex.robex import robex

# 去颅骨处理
def remove_skull(input_nii, output_nii):
    try:
        # 读取输入图像
        image = nib.load(input_nii)
        
        # 去颅骨处理
        stripped, mask = robex(image)
        
        # 创建输出目录（如果不存在）
        os.makedirs(os.path.dirname(output_nii), exist_ok=True)
        
        # 保存去颅骨后的图像
        nib.save(stripped, output_nii)
        print(f'Skull stripping completed and saved to {output_nii}')
    except Exception as e:
        print(f'Error during skull stripping: {e}')

# 非线性配准处理
def ants_nonelinear_registration(input_nii, output_nii, ref_nii):
    s_t = time.time()
    # 加载源图像和目标图像
    fixed_image = ants.image_read(ref_nii)  # 目标图像
    moving_image = ants.image_read(input_nii)  # 需要配准的源图像

    # 使用ANTs的非线性配准
    registration = ants.registration(fixed=fixed_image, moving=moving_image, type_of_transform='SyN')

    # 获取配准后的图像
    registered_image = registration['warpedmovout']

    # 保存配准后的图像
    ants.image_write(registered_image, output_nii)
    print(f'Successfully registered {input_nii} to {ref_nii} and saved to {output_nii}')

# N4偏场校正
def n4_bias_field_correction(input_nii, output_nii):
    try:
        # 读取输入图像
        image = sitk.ReadImage(input_nii)
        
        # 进行N4偏场校正
        corrector = sitk.N4BiasFieldCorrectionImageFilter()
        corrected_image = corrector.Execute(image)
        
        # 创建输出目录（如果不存在）
        os.makedirs(os.path.dirname(output_nii), exist_ok=True)
        
        # 保存校正后的图像
        sitk.WriteImage(corrected_image, output_nii)
        print(f'N4 bias field correction completed and saved to {output_nii}')
    except Exception as e:
        print(f'Error during N4 bias field correction: {e}')

# 图像裁剪
def crop_image_to_target_shape(image, target_shape=(160, 192, 160)):
    # 找到非零值的边界框
    mask = image > 0
    coords = np.array(np.nonzero(mask))
    min_coords = np.min(coords, axis=1)
    max_coords = np.max(coords, axis=1)
    
    # 计算当前脑组织范围
    current_shape = max_coords - min_coords + 1
    
    # 确保目标形状足够大
    if any(current_shape[i] > target_shape[i] for i in range(3)):
        raise ValueError("Target shape is too small to fit the brain tissue.")
    
    # 计算每个维度上的裁剪起始点
    crop_start = [0, 0, 0]
    crop_end = [0, 0, 0]
    for i in range(3):
        crop_start[i] = min_coords[i] - (target_shape[i] - current_shape[i]) // 2
        crop_end[i] = crop_start[i] + target_shape[i]
        
        # 如果起始点或结束点超出了图像边界，则调整它们
        if crop_start[i] < 0:
            crop_start[i] = 0
            crop_end[i] = target_shape[i]
        if crop_end[i] > image.shape[i]:
            crop_end[i] = image.shape[i]
            crop_start[i] = crop_end[i] - target_shape[i]
    
    # 裁剪图像
    cropped_image = image[crop_start[0]:crop_end[0], 
                          crop_start[1]:crop_end[1], 
                          crop_start[2]:crop_end[2]]
    
    return cropped_image

# 归一化到[0, 1]
def normalize_to_01(image):
    "Normalize image to range [0, 1]"
    image = image.astype(np.float32)
    min_val = np.min(image)
    print(f'Min value: {min_val}')
    max_val = np.max(image)
    if max_val > min_val:
        ret = (image - min_val) / (max_val - min_val)
    else:
        ret = image * 0.
    return ret

# 批量处理函数，整合了去颅骨、配准、N4校正、裁剪和归一化
def batch_processing_with_cropping_and_normalization(sMRI_root, output_root, ref_nii, target_shape=(160, 192, 160)):
    # 获取顶层目录下的所有被试者文件夹
    subject_folders = [os.path.join(sMRI_root, d) for d in os.listdir(sMRI_root) if os.path.isdir(os.path.join(sMRI_root, d))]
    
    if not os.path.exists(output_root):
        os.makedirs(output_root)
    
    for subject_folder in subject_folders:
        subject_id = os.path.basename(subject_folder)
        nii_files = [f for f in os.listdir(subject_folder) if f.endswith('.nii')]
        
        if not nii_files:
            print(f'No .nii files found in {subject_folder}, skipping.')
            continue
        
        for nii_file in nii_files:
            input_nii = os.path.join(subject_folder, nii_file)
            stripped_nii = os.path.join(output_root, subject_id, 'image_stripped.nii')
            registered_nii = os.path.join(output_root, subject_id, 'image_registered.nii')
            normalized_nii = os.path.join(output_root, subject_id, 'image_normalized.nii')
            cropped_nii = os.path.join(output_root, subject_id, 'image_cropped.nii')
            final_nii = os.path.join(output_root, subject_id, 'image_final_normalized.nii')
            
            # 1. 去颅骨处理
            remove_skull(input_nii, stripped_nii)
            
            # 2. 非线性配准
            ants_nonelinear_registration(stripped_nii, registered_nii, ref_nii)
            
            # 3. N4偏场校正
            n4_bias_field_correction(registered_nii, normalized_nii)
            
            # 4. 裁剪图像
            img = nib.load(normalized_nii)
            image_data = img.get_fdata().astype(np.float32)  # 确保数据类型一致
            
            try:
                cropped_image = crop_image_to_target_shape(image_data, target_shape)
                cropped_img = nib.Nifti1Image(cropped_image, img.affine)
                nib.save(cropped_img, cropped_nii)
                print(f'Cropped and saved image for subject: {subject_id}')
            except ValueError as e:
                print(f'Cannot crop image for subject: {subject_folder}, error: {e}')
                continue
            
            # 5. 归一化图像
            normalized_image_data = normalize_to_01(cropped_image)
            final_normalized_image = nib.Nifti1Image(normalized_image_data, img.affine)
            nib.save(final_normalized_image, final_nii)
            print(f'Final normalized image saved for subject: {subject_id}')

if __name__ == '__main__':
    # 定义sMRI文件所在的根目录和输出的根目录
    sMRI_root = '2025.10.11_PPMI_Prodromal_nii'
    output_root = '2025.10.11_PPMI_Prodromal_normalized'
    fsl_dir = os.getenv("FSLDIR")
    ref_nii = f"{fsl_dir}/data/standard/MNI152_T1_1mm_brain.nii.gz"
    
    # 批量处理：去颅骨、配准、N4偏场校正、裁剪和归一化
    print(f'Processing dataset: {sMRI_root}')
    batch_processing_with_cropping_and_normalization(sMRI_root, output_root, ref_nii)







# import os
# import nibabel as nib
# import SimpleITK as sitk
# import ants
# import numpy as np
# import time
# from pyrobex.robex import robex

# # 去颅骨处理
# def remove_skull(input_nii, output_nii):
#     try:
#         image = nib.load(input_nii)
#         stripped, mask = robex(image)
#         os.makedirs(os.path.dirname(output_nii), exist_ok=True)
#         nib.save(stripped, output_nii)
#         print(f'Skull stripping completed and saved to {output_nii}')
#     except Exception as e:
#         print(f'Error during skull stripping: {e}')

# # 非线性配准处理
# def ants_nonelinear_registration(input_nii, output_nii, ref_nii):
#     s_t = time.time()
#     fixed_image = ants.image_read(ref_nii)
#     moving_image = ants.image_read(input_nii)
#     registration = ants.registration(fixed=fixed_image, moving=moving_image, type_of_transform='SyN')
#     registered_image = registration['warpedmovout']
#     ants.image_write(registered_image, output_nii)
#     print(f'Successfully registered {input_nii} to {ref_nii} and saved to {output_nii}')

# # N4偏场校正
# def n4_bias_field_correction(input_nii, output_nii):
#     try:
#         image = sitk.ReadImage(input_nii)
#         corrector = sitk.N4BiasFieldCorrectionImageFilter()
#         corrected_image = corrector.Execute(image)
#         os.makedirs(os.path.dirname(output_nii), exist_ok=True)
#         sitk.WriteImage(corrected_image, output_nii)
#         print(f'N4 bias field correction completed and saved to {output_nii}')
#     except Exception as e:
#         print(f'Error during N4 bias field correction: {e}')

# # 图像resize
# def resize_image(image, target_shape=(80, 96, 80)):
#     # 使用SimpleITK进行resize
#     image_sitk = sitk.GetImageFromArray(image)
#     original_size = image_sitk.GetSize()
    
#     # 计算缩放因子
#     new_size = target_shape
#     resampler = sitk.ResampleImageFilter()
#     resampler.SetSize(new_size)
#     resampler.SetOutputSpacing([s / n for s, n in zip(original_size, new_size)])  # 计算新的spacing

#     resized_image = resampler.Execute(image_sitk)
#     return sitk.GetArrayFromImage(resized_image)

# # 归一化到[0, 1]
# def normalize_to_01(image):
#     image = image.astype(np.float32)
#     min_val = np.min(image)
#     max_val = np.max(image)
#     if max_val > min_val:
#         ret = (image - min_val) / (max_val - min_val)
#     else:
#         ret = image * 0.
#     return ret

# # 批量处理函数，整合了去颅骨、配准、N4校正、resize和归一化
# def batch_processing_with_resizing_and_normalization(sMRI_root, output_root, ref_nii, target_shape=(80, 96, 80)):
#     subject_folders = [os.path.join(sMRI_root, d) for d in os.listdir(sMRI_root) if os.path.isdir(os.path.join(sMRI_root, d))]
    
#     if not os.path.exists(output_root):
#         os.makedirs(output_root)
    
#     for subject_folder in subject_folders:
#         subject_id = os.path.basename(subject_folder)
#         nii_files = [f for f in os.listdir(subject_folder) if f.endswith('.nii')]
        
#         if not nii_files:
#             print(f'No .nii files found in {subject_folder}, skipping.')
#             continue
        
#         for nii_file in nii_files:
#             input_nii = os.path.join(subject_folder, nii_file)
#             stripped_nii = os.path.join(output_root, subject_id, 'image_stripped.nii')
#             registered_nii = os.path.join(output_root, subject_id, 'image_registered.nii')
#             normalized_nii = os.path.join(output_root, subject_id, 'image_normalized.nii')
#             resized_nii = os.path.join(output_root, subject_id, 'image_resized.nii')
#             final_nii = os.path.join(output_root, subject_id, 'image_final_normalized.nii')
            
#             # 1. 去颅骨处理
#             remove_skull(input_nii, stripped_nii)
            
#             # 2. 非线性配准
#             ants_nonelinear_registration(stripped_nii, registered_nii, ref_nii)
            
#             # 3. N4偏场校正
#             n4_bias_field_correction(registered_nii, normalized_nii)
            
#             # 4. resize图像
#             img = nib.load(normalized_nii)
#             image_data = img.get_fdata().astype(np.float32)
#             resized_image = resize_image(image_data, target_shape)
#             resized_img = nib.Nifti1Image(resized_image, img.affine)
#             nib.save(resized_img, resized_nii)
#             print(f'Resized image for subject: {subject_id}')
            
#             # 5. 归一化图像
#             normalized_image_data = normalize_to_01(resized_image)
#             final_normalized_image = nib.Nifti1Image(normalized_image_data, img.affine)
#             nib.save(final_normalized_image, final_nii)
#             print(f'Final normalized image saved for subject: {subject_id}')

# if __name__ == '__main__':
#     sMRI_root = '../ADNI_t1/10.23_T1MRI_nii'
#     output_root = '../ADNI_t1/10.23_T1MRI_nii_preprocessed'
#     ref_nii = 'MNI152_T1_1mm_brain.nii.gz'
    
#     # 批量处理：去颅骨、配准、N4偏场校正、resize和归一化
#     print(f'Processing dataset: {sMRI_root}')
#     batch_processing_with_resizing_and_normalization(sMRI_root, output_root, ref_nii)










# import os
# import nibabel as nib
# import SimpleITK as sitk
# import ants
# import numpy as np
# import time
# from pyrobex.robex import robex

# # 去颅骨处理
# def remove_skull(input_nii, output_nii):
#     try:
#         image = nib.load(input_nii)
#         stripped, mask = robex(image)
#         os.makedirs(os.path.dirname(output_nii), exist_ok=True)
#         nib.save(stripped, output_nii)
#         print(f'Skull stripping completed and saved to {output_nii}')
#     except Exception as e:
#         print(f'Error during skull stripping: {e}')
#         return False
#     return True

# # 非线性配准处理
# def ants_nonelinear_registration(input_nii, output_nii, ref_nii):
#     try:
#         fixed_image = ants.image_read(ref_nii)
#         moving_image = ants.image_read(input_nii)
#         registration = ants.registration(fixed=fixed_image, moving=moving_image, type_of_transform='SyN')
#         registered_image = registration['warpedmovout']
#         ants.image_write(registered_image, output_nii)
#         print(f'Successfully registered {input_nii} to {ref_nii} and saved to {output_nii}')
#     except Exception as e:
#         print(f'Error during registration: {e}')
#         return False
#     return True

# # N4偏场校正
# def n4_bias_field_correction(input_nii, output_nii):
#     try:
#         image = sitk.ReadImage(input_nii)
#         corrector = sitk.N4BiasFieldCorrectionImageFilter()
#         corrected_image = corrector.Execute(image)
#         os.makedirs(os.path.dirname(output_nii), exist_ok=True)
#         sitk.WriteImage(corrected_image, output_nii)
#         print(f'N4 bias field correction completed and saved to {output_nii}')
#     except Exception as e:
#         print(f'Error during N4 bias field correction: {e}')
#         return False
#     return True

# # 图像resize
# def resize_image(image, target_shape=(80, 96, 80)):
#     image_sitk = sitk.GetImageFromArray(image)
#     original_size = image_sitk.GetSize()
#     new_size = target_shape
#     resampler = sitk.ResampleImageFilter()
#     resampler.SetSize(new_size)
#     resampler.SetOutputSpacing([s / n for s, n in zip(original_size, new_size)])
#     resized_image = resampler.Execute(image_sitk)
#     return sitk.GetArrayFromImage(resized_image)

# # 归一化到[0, 1]
# def normalize_to_01(image):
#     image = image.astype(np.float32)
#     min_val = np.min(image)
#     max_val = np.max(image)
#     if max_val > min_val:
#         ret = (image - min_val) / (max_val - min_val)
#     else:
#         ret = image * 0.
#     return ret

# # 批量处理函数，整合了去颅骨、配准、N4校正、resize和归一化
# def batch_processing_with_resizing_and_normalization(sMRI_root, output_root, ref_nii, target_shape=(80, 96, 80)):
#     subject_folders = [os.path.join(sMRI_root, d) for d in os.listdir(sMRI_root) if os.path.isdir(os.path.join(sMRI_root, d))]
#     if not os.path.exists(output_root):
#         os.makedirs(output_root)
    
#     failed_files = []  # 记录失败的文件

#     for subject_folder in subject_folders:
#         subject_id = os.path.basename(subject_folder)
#         nii_files = [f for f in os.listdir(subject_folder) if f.endswith('.nii')]
        
#         if not nii_files:
#             print(f'No .nii files found in {subject_folder}, skipping.')
#             continue
        
#         for nii_file in nii_files:
#             input_nii = os.path.join(subject_folder, nii_file)
#             stripped_nii = os.path.join(output_root, subject_id, 'image_stripped.nii')
#             registered_nii = os.path.join(output_root, subject_id, 'image_registered.nii')
#             normalized_nii = os.path.join(output_root, subject_id, 'image_normalized.nii')
#             resized_nii = os.path.join(output_root, subject_id, 'image_resized.nii')
#             final_nii = os.path.join(output_root, subject_id, 'image_final_normalized.nii')
            
#             # 1. 去颅骨处理
#             if not remove_skull(input_nii, stripped_nii):
#                 failed_files.append(input_nii)
#                 continue
            
#             # 2. 非线性配准
#             if not ants_nonelinear_registration(stripped_nii, registered_nii, ref_nii):
#                 failed_files.append(stripped_nii)
#                 continue
            
#             # 3. N4偏场校正
#             if not n4_bias_field_correction(registered_nii, normalized_nii):
#                 failed_files.append(registered_nii)
#                 continue
            
#             # 4. resize图像
#             img = nib.load(normalized_nii)
#             image_data = img.get_fdata().astype(np.float32)
#             try:
#                 resized_image = resize_image(image_data, target_shape)
#                 resized_img = nib.Nifti1Image(resized_image, img.affine)
#                 nib.save(resized_img, resized_nii)
#                 print(f'Resized image for subject: {subject_id}')
#             except Exception as e:
#                 print(f'Error during resizing for subject: {subject_id}, file: {normalized_nii}, error: {e}')
#                 failed_files.append(normalized_nii)
#                 continue
            
#             # 5. 归一化图像
#             normalized_image_data = normalize_to_01(resized_image)
#             final_normalized_image = nib.Nifti1Image(normalized_image_data, img.affine)
#             nib.save(final_normalized_image, final_nii)
#             print(f'Final normalized image saved for subject: {subject_id}')

#     # 输出所有失败的文件名
#     if failed_files:
#         print("Failed files:")
#         for failed_file in failed_files:
#             print(failed_file)

# if __name__ == '__main__':
#     sMRI_root = '2024.9.7_addMRI_nii'
#     output_root = '../ADNI_t1/10.23_T1MRI_nii_preprocessed'
#     ref_nii = 'MNI152_T1_1mm_brain.nii.gz'
    
#     print(f'Processing dataset: {sMRI_root}')
#     batch_processing_with_resizing_and_normalization(sMRI_root, output_root, ref_nii)
