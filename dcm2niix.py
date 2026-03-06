# import os
# import subprocess

# def convert_dicom_to_nifti(dicom_root, nifti_root):
#     # 获取顶层目录下的所有被试者文件夹
#     subject_folders = [os.path.join(dicom_root, d) for d in os.listdir(dicom_root) if os.path.isdir(os.path.join(dicom_root, d))]
    
#     for subject_folder in subject_folders:
#         subject_id = os.path.basename(subject_folder)
#         output_folder = os.path.join(nifti_root, subject_id)
        
#         # 创建输出目录（如果不存在）
#         os.makedirs(output_folder, exist_ok=True)
        
#         # 运行dcm2niix命令
#         command = ['dcm2niix', '-o', output_folder, subject_folder]
#         try:
#             subprocess.run(command, check=True)
#             print(f'Converted {subject_folder} to {output_folder}')
#         except subprocess.CalledProcessError as e:
#             print(f'Error converting {subject_folder}: {e}')

# if __name__ == '__main__':
#     # 定义DICOM文件所在的根目录和输出的NIfTI文件根目录
#     dicom_root = '021s4718'
#     nifti_root = '021s4718nii'
    
#     # 调用函数进行批量转换
#     convert_dicom_to_nifti(dicom_root, nifti_root)





import os
import subprocess

def convert_dicom_to_nifti(dicom_root, nifti_root):
    # 获取顶层目录下的所有被试者文件夹
    subject_folders = [os.path.join(dicom_root, d) for d in os.listdir(dicom_root) if os.path.isdir(os.path.join(dicom_root, d))]
    
    for subject_folder in subject_folders:
        subject_id = os.path.basename(subject_folder)
        
        # 获取被试者文件夹中的所有子文件夹
        for root, dirs, files in os.walk(subject_folder):
            for dir in dirs:
                dcm_folder = os.path.join(root, dir)
                if any(file.endswith('.dcm') for file in os.listdir(dcm_folder)):
                    output_folder = os.path.join(nifti_root, subject_id)
                    
                    # 创建输出目录（如果不存在）
                    os.makedirs(output_folder, exist_ok=True)
                    
                    # 运行dcm2niix命令
                    command = ['dcm2niix', '-z', 'n', '-o', output_folder, dcm_folder]
                    try:
                        subprocess.run(command, check=True)
                        print(f'Converted {dcm_folder} to {output_folder}')
                    except subprocess.CalledProcessError as e:
                        print(f'Error converting {dcm_folder}: {e}')
                    break  # 只处理第一个包含.dcm文件的子文件夹

if __name__ == '__main__':
    # 定义DICOM文件所在的根目录和输出的NIfTI文件根目录
    dicom_root = '2025.10.11_PPMI_Prodromal'
    nifti_root = '2025.10.11_PPMI_Prodromal_nii'
    
    # 调用函数进行批量转换
    convert_dicom_to_nifti(dicom_root, nifti_root)














# import os
# import shutil

# # 定义顶级目录
# top_dir = r'E:\ADNI3_DTI\AD_add_DTI'

# # 遍历顶级目录下的所有子目录
# for root, dirs, files in os.walk(top_dir):
#     for dir_name in dirs:
#         # 检查是否是目标目录Axial_DTI
#         if dir_name == 'Axial_DTI':
#             axial_dti_path = os.path.join(root, dir_name)
#             print(f'Found Axial_DTI directory: {axial_dti_path}')
            
#             # 遍历Axial_DTI目录下的所有子目录
#             for sub_dir in os.listdir(axial_dti_path):
#                 sub_dir_path = os.path.join(axial_dti_path, sub_dir)
                
#                 # 检查是否是日期命名的目录
#                 if os.path.isdir(sub_dir_path) and sub_dir.count('_') == 3:
#                     print(f'Found date-named directory: {sub_dir_path}')
                    
#                     # 遍历日期目录下的所有子目录
#                     for nested_dir in os.listdir(sub_dir_path):
#                         nested_dir_path = os.path.join(sub_dir_path, nested_dir)
                        
#                         # 检查是否是文件夹
#                         if os.path.isdir(nested_dir_path):
#                             # 获取aaa的名称
#                             aaa_name = os.path.basename(root)
#                             print(f'Found nested directory: {nested_dir_path}, will rename and move to {aaa_name}')
                            
#                             # 生成新的目标路径
#                             new_path = os.path.join(top_dir, aaa_name)
                            
#                             # 创建目标路径（如果不存在）
#                             if not os.path.exists(new_path):
#                                 os.makedirs(new_path)
#                                 print(f'Created new directory: {new_path}')
                            
#                             # 重命名并移动子目录
#                             new_nested_dir_path = os.path.join(new_path, aaa_name)
#                             shutil.move(nested_dir_path, new_nested_dir_path)
#                             print(f'Moved {nested_dir_path} to {new_nested_dir_path}')

#             # 为了防止重复遍历，我们可以中断当前目录的遍历
#             break





# import os
# import shutil

# def move_files_and_cleanup(base_dir):
#     # 遍历目录树
#     for root, dirs, files in os.walk(base_dir, topdown=False):
#         # 输出当前遍历的目录
#         print(f"Checking directory: {root}")
        
#         # 检查是否是目标文件夹（文件夹名以'I'开头）
#         if any(file.startswith('A') for file in files):
#             # 获取父文件夹路径
#             parent_dir = os.path.abspath(os.path.join(root, "../../.."))
#             print(f"Parent directory: {parent_dir}")

#             # 确保父目录存在
#             if not os.path.exists(parent_dir):
#                 print(f"Parent directory {parent_dir} does not exist. Skipping...")
#                 continue

#             # 移动文件到父文件夹
#             for file in files:
#                 src_file = os.path.join(root, file)
#                 dest_file = os.path.join(parent_dir, file)
#                 print(f"Moving {src_file} to {dest_file}")
#                 shutil.move(src_file, dest_file)

#             # 移除目标文件夹
#             print(f"Removing directory: {root}")
#             shutil.rmtree(root)

#             # 检查并删除空的父文件夹
#             current_dir = os.path.dirname(root)
#             while current_dir != base_dir and not os.listdir(current_dir):
#                 print(f"Removing empty directory: {current_dir}")
#                 os.rmdir(current_dir)
#                 current_dir = os.path.dirname(current_dir)

# # 定义基目录
# base_dir = r'E:\ADNI3_DTI\\NC_zjy_add_DTI_Download1\ADNI'

# # 执行函数
# move_files_and_cleanup(base_dir)

