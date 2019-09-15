#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import os.path
import click
import tinify
import shutil

tinify.key = "Your API KEY"		# API KEY
version = "1.0.1"				# 版本

TargetPath = 'Your Target Path' # 要拷贝到哪个目录
SourcePath = 'Your Source Path' # 从哪个目录拷贝

# 压缩的核心
def compress_core(inputFile, outputFile, img_width):
	source = tinify.from_file(inputFile)
	if img_width is not -1:
		resized = source.resize(method = "scale", width  = img_width)
		resized.to_file(outputFile)
	else:
		source.to_file(outputFile)

# 压缩一个文件夹下的图片
def compress_path(path, width):
	print ("compress_path-------------------------------------")
	if not os.path.isdir(path):
		print ("这不是一个文件夹，请输入文件夹的正确路径!")
		return
	else:
		fromFilePath = path 			# 源路径
		toFilePath = SourcePath 		# 输出路径
		print ("fromFilePath=%s" %fromFilePath)
		print ("toFilePath=%s" %toFilePath)

		for root, dirs, files in os.walk(fromFilePath):
			print ("root = %s" %root)
			print ("dirs = %s" %dirs)
			print ("files= %s" %files)
			for name in files:
				fileName, fileSuffix = os.path.splitext(name)
				if fileSuffix == '.png' or fileSuffix == '.jpg' or fileSuffix == '.jpeg':
					toFullPath = toFilePath + root[len(fromFilePath):]
					toFullName = toFullPath + '/' + name
					if os.path.isdir(toFullPath):
						pass
					else:
						os.mkdir(toFullPath)
					compress_core(root + '/' + name, toFullName, width)
			# break									# 仅遍历当前目录

# 仅压缩指定文件
def compress_file(inputFile, width):
	print ("compress_file-------------------------------------")
	if not os.path.isfile(inputFile):
		print ("这不是一个文件，请输入文件的正确路径!")
		return
	print ("file = %s" %inputFile)
	dirname  = os.path.dirname(inputFile)
	basename = os.path.basename(inputFile)
	fileName, fileSuffix = os.path.splitext(basename)
	if fileSuffix == '.png' or fileSuffix == '.jpg' or fileSuffix == '.jpeg':
		compress_core(inputFile, dirname+"/tiny_"+basename, width)
	else:
		print ("不支持该文件类型!")

# 判断是否是图片
def is_img(ext):
    ext = ext.lower()
    if ext in ['.jpg', '.png', '.jpeg', '.bmp']:
        return True
    else:
        return False

# 获取指定目录下所有图片
def get_img_files(dir):
    py_files = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            pre, suf = os.path.splitext(file)
            if is_img(suf):
                py_files.append(os.path.join(root, file))
    return py_files

# 批处理替换
def batch_replace_img():
    TargetFiles = get_img_files(TargetPath)
    SourceFiles = get_img_files(SourcePath)

    for target in TargetFiles:
        for source in SourceFiles:
            targetName = target.split('/')[-1]
            sourceName = source.split('/')[-1]
            if targetName == sourceName:
                shutil.copyfile(source, target)

@click.command()
@click.option('-f', "--file",  type=str,  default=None,  help="单个文件压缩")
@click.option('-d', "--dir",   type=str,  default=None,  help="被压缩的文件夹")
@click.option('-w', "--width", type=int,  default=-1,    help="图片宽度，默认不变")
def run(file, dir, width):
	print ("GcsSloop TinyPng V%s" %(version))
	if file is not None:
		compress_file(file, width)				# 仅压缩一个文件
		pass
	elif dir is not None:
		compress_path(dir, width)				# 压缩指定目录下的文件
		pass
	else:
		compress_path(os.getcwd(), width)		# 压缩当前目录下的文件
	print ("压缩结束!")

if __name__ == "__main__":
    # run(None, TargetPath, None)
    compress_path(TargetPath, -1)
    batch_replace_img()
    print("替换结束")
