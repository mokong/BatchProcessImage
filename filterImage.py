import os
import shutil

# 判断是否是图片
def is_img(ext):
    ext = ext.lower()
    if ext in ['.jpg', '.png', '.jpeg', '.bmp']:
        return True
    else:
        return False

TargetPath = 'Your Target Path' # 要拷贝到哪个目录
SourcePath = 'Your Source Path' # 从哪个目录拷贝

# 获取指定目录下所有图片
def get_img_files(dir):
    py_files = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            pre, suf = os.path.splitext(file)
            if is_img(suf):
                py_files.append(os.path.join(root, file))
    return py_files

TargetFiles = get_img_files(TargetPath)
SourceFiles = get_img_files(SourcePath)

for target in TargetFiles:
    for source in SourceFiles:
        targetName = target.split('/')[-1]
        sourceName = source.split('/')[-1]
        if targetName == sourceName:
            shutil.copyfile(source, target)
