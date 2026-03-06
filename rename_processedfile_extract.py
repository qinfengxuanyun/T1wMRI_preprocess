# import os
# import shutil

# # 设置文件夹路径
# folder_path = "2024.9.7_addDTI_nii2_processed"

# # 遍历主文件夹中的所有子文件夹
# for subject_folder in os.listdir(folder_path):
#     subject_path = os.path.join(folder_path, subject_folder)
    
#     # 检查是否是文件夹
#     if os.path.isdir(subject_path):
#         nii_files = [f for f in os.listdir(subject_path) if f.endswith('.nii')]
        
#         # 如果子文件夹中没有nii文件，打印出子文件夹名字
#         if not nii_files:
#             print(f"子文件夹 {subject_folder} 中没有 .nii 文件")
#         else:
#             # 获取第一个nii文件（假设每个文件夹中只有一个nii文件）
#             nii_file = nii_files[0]
#             nii_file_path = os.path.join(subject_path, nii_file)
            
#             # 目标文件路径，重命名为子文件夹名称
#             new_nii_file_path = os.path.join(folder_path, f"{subject_folder}.nii")
            
#             # 重命名并将文件移动到主文件夹下
#             shutil.move(nii_file_path, new_nii_file_path)
            
#             # 删除子文件夹
#             shutil.rmtree(subject_path)

# print("处理完成！")






# import os
# import shutil

# # 设置文件夹路径
# folder_path = "../ADNI_t1/10.23_T1MRI_nii_preprocessed"

# # 遍历主文件夹中的所有子文件夹
# for subject_folder in os.listdir(folder_path):
#     subject_path = os.path.join(folder_path, subject_folder)
    
#     # 检查是否是文件夹
#     if os.path.isdir(subject_path):
#         nii_file_path = os.path.join(subject_path, 'image_final_normalized.nii')
        
#         # 检查文件是否存在
#         if not os.path.exists(nii_file_path):
#             print(f"子文件夹 {subject_folder} 中没有 image_final_normalized.nii 文件")
#         else:
#             # 目标文件路径，重命名为子文件夹名称
#             new_nii_file_path = os.path.join(folder_path, f"{subject_folder}.nii")
            
#             # 重命名并将文件移动到主文件夹下
#             shutil.move(nii_file_path, new_nii_file_path)
            
#             # 删除子文件夹及其他文件
#             shutil.rmtree(subject_path)

# print("处理完成！")




import os
import shutil

# 设置源文件夹路径和目标文件夹路径
source_folder = os.path.abspath("2025.10.11_PPMI_Prodromal_normalized")
target_folder = os.path.abspath("2025.10.11_PPMI_Prodromal_normalized_usingfiles")

# 创建目标文件夹（如果不存在）
os.makedirs(target_folder, exist_ok=True)

# 遍历源文件夹中的所有子文件夹
for subject_folder in os.listdir(source_folder):
    subject_path = os.path.join(source_folder, subject_folder)
    
    # 检查是否是文件夹
    if os.path.isdir(subject_path):
        nii_file_path = os.path.join(subject_path, 'image_final_normalized.nii')
        
        # 检查文件是否存在
        if not os.path.exists(nii_file_path):
            print(f"子文件夹 {subject_folder} 中没有 image_final_normalized.nii 文件")
        else:
            # 目标文件路径，重命名为子文件夹名称
            new_nii_file_path = os.path.join(target_folder, f"{subject_folder}.nii")
            
            # 处理文件名冲突
            counter = 1
            while os.path.exists(new_nii_file_path):
                new_nii_file_path = os.path.join(target_folder, f"{subject_folder}_{counter}.nii")
                counter += 1
            
            try:
                # 移动文件到目标文件夹
                shutil.move(nii_file_path, new_nii_file_path)
                print(f"文件已从 {nii_file_path} 移动到 {new_nii_file_path}")
            except Exception as e:
                print(f"移动文件 {nii_file_path} 时出错：{e}")

print("处理完成！")

