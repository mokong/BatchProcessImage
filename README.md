# [BatchProcessImage](https://mokong.github.io/2019/09/15/%E6%89%B9%E9%87%8F%E5%9B%BE%E7%89%87%E5%8E%8B%E7%BC%A9&%E6%9B%BF%E6%8D%A2/#more)
批量压缩图片，批量替换图片

---
title: 批量图片压缩 & 替换
date: 2019-09-15 10:15
tags: 技术
---

## 背景
最近产品提了个需求，要求把包压缩一下，而项目是OC&Swift混编，这期还加上了RN，还要包不能增大。脑壳疼。。。。他则不上天呢。但需求出来了，还是要做的。所以就想了下面几个方法：

1. 先用[LSUnusedResources](https://github.com/tinymind/LSUnusedResources)分析项目中无用的图片和类，删除；
2. 然后对项目中的图片进行压缩替换；
3. 再接着分析[linkMap](https://stackoverflow.com/questions/32003262/find-size-contributed-by-each-external-library-on-ios)文件，找出大的文件进行优化。
4. [基于clang插件的一种iOS包大小瘦身方案](https://blog.csdn.net/fishmai/article/details/81603088)

## 实现
这篇就是关于第二步的，项目里大约有1600多张图片，之前几次压缩都是按大小排序，然后把大于10kb的图片一个个上传到[tinypng](https://tinypng.com/)上压缩，再下载替换。tinypng web最多支持一次20张，每次上传压缩，然后等，就问问烦不烦。。。。

so，这次我终于受不了，我要找批量压缩的，还真给我搜到了[图片批量压缩脚本(Python)](https://github.com/GcsSloop/TinyPng)，这种使用方式GitHub上已经写得很清楚了，可以500张批量压缩，然后有一个输出文件夹：

使用这个脚本的时候，要注意：
 1. 安装Python
 2. 安装click和tinify
   ```
   pip install click // 安装click库
   pip install --upgrade tinify // 安装tinify库
   ```
然后使用脚本，GitHub里那位大佬脚本print函数没更新，贴一下我更新后的：

``` Python
#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import os.path
import click
import tinify

tinify.key = "Your API Key"		# API KEY
version = "1.0.1"				# 版本

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
		toFilePath = path+"/tiny" 		# 输出路径
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
			break									# 仅遍历当前目录

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
	print ("结束!")

if __name__ == "__main__":
    run()
```

Yeah，使用了这个脚本之后，图片可以批量压缩了，但是压缩之后的图片是生成在一个独立文件夹，我需要批量替换，but，我图片的目录不确定，换句话说，我不知道这些文件具体在哪个目录下面。。。。oh no。

so，这是你比我的，开动脑壳，我就想能不能做到我在读取图片压缩的之后直接替换；又或者，写一个单独的批量替换的脚本，因为大的目录确定，压缩前后图片名字没有变化，这么做应该可行，说干就干
使用的时候，把Python文件里TargetPath改成要替换的总目录，SourcePath改成上个脚本执行后压缩后图片的目录，然后运行，binggo，done
原理：
1. 读取指定目录&子目录下所有文件
2. 判断是不是图片，是就存到数组里
3. 读取Target目录和Source目录，然后遍历用'/'分割，取最后一个，判断是否相等，相等就写入

``` Python
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
```
