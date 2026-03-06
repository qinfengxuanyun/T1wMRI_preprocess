# import os
# import nibabel as nib
# import numpy as np

# def convert_nii_to_npy(input_folder, output_folder):
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)

#     for root, _, files in os.walk(input_folder):
#         for file in files:
#             if file.endswith('.nii') or file.endswith('.nii.gz'):
#                 nii_path = os.path.join(root, file)
#                 npy_path = os.path.join(output_folder, os.path.splitext(file)[0] + '.npy')

#                 # 读取 NIfTI 文件
#                 img = nib.load(nii_path)
#                 image_data = img.get_fdata()

#                 # 保存为 .npy 文件
#                 np.save(npy_path, image_data)
#                 print(f"Converted {nii_path} to {npy_path}")

# # 示例使用
# input_folder = 'newdataset\\t1MRI-N4cropped'
# output_folder = 'newdataset\\t1MRI-N4cropped_npy'
# convert_nii_to_npy(input_folder, output_folder)



import os
import nibabel as nib
import numpy as np

def nii_to_npy(input_folder, output_folder):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有文件
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.nii') or file.endswith('.nii.gz'):
                nii_path = os.path.join(root, file)
                npy_path = os.path.join(output_folder, os.path.splitext(file)[0] + '.npy')

                # 读取 NIfTI 文件
                img = nib.load(nii_path)
                image_data = img.get_fdata()

                # 转换为 float32 类型
                image_data = image_data.astype(np.float32)

                # 保存为 .npy 文件
                np.save(npy_path, image_data)
                print(f"Converted {nii_path} to {npy_path}")

# 示例使用 
input_folder = '2025.10.11_PPMI_Prodromal_normalized_usingfiles'
output_folder = '2025.10.11_PPMI_Prodromal_normalized_usingfiles_npy'
nii_to_npy(input_folder, output_folder)



# import os
# import nibabel as nib
# import numpy as np
# # 读取 NIfTI 文件
# img = nib.load('AAL\\aal116_template_80.nii')
# image_data = img.get_fdata()

# # 转换为 float32 类型
# image_data = image_data.astype(np.int16)

# # 保存为 .npy 文件
# np.save('AAL\\aal116_template_80.npy', image_data)




# import numpy as np
# import nibabel as nib

# def npy_to_nii(npy_file, nii_file, affine=None):
#     # 加载 .npy 文件
#     data = np.load(npy_file)
    
#     # 如果没有提供仿射矩阵，使用单位矩阵
#     if affine is None:
#         affine = np.eye(4)
    
#     # 创建 Nifti1Image 对象
#     nii_image = nib.Nifti1Image(data, affine)
    
#     # 保存为 .nii 文件
#     nib.save(nii_image, nii_file)
#     print(f"Saved {npy_file} as {nii_file}")

# # 示例使用
# npy_file = '../UKB/1000532.npy'
# nii_file = '../UKB/1000532.nii'
# npy_to_nii(npy_file, nii_file)



# import numpy as np

# # 加载 .npy 文件
# file_path = '003_S_4136\\003_S_4136.npy'  # 替换为你的 .npy 文件路径
# data = np.load(file_path)

# # 打印形状
# print("数据的形状:", data.shape)




