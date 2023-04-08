import os

folder_path = r"D:\gcbb\xiaomi\EMB\main\arxml\ApplIfDefine\arxml_comm_def"

for filename in os.listdir(folder_path):
    if filename.endswith(".arxml"):
        os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, filename.replace(".arxml", "_emb.arxml")))
