"""
Interactive program for online calculation of the laser beam profile from picture.
"""

import streamlit as st
import cv2
from PIL import Image
import numpy as np
from zipfile import ZipFile
import tempfile
import os
import pandas as pd


# width of displayed picture
width = 100

st.write("# Specle contrast from picture")


uploaded_files = st.sidebar.file_uploader("Choose grey files with speckles", 
                                          type = ['png', 'jpg', 'bmp', 'tif'], 
                                          accept_multiple_files=True)
for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read()

st.sidebar.write(""" Source code is located [here](https://github.com/Alex-beam/Beam-profiler).   
                 Contact me by [email](mailto:akorom@mail.ru).""")

st.image(uploaded_files, width=width)


st.write("Processed images:")


imgs = []
imgs_g = []
imgs_contrast = []
file_names = []

for uploaded_file in uploaded_files:   
    
    img = np.array(Image.open(uploaded_file))
    imgs.append(img)

delta = st.number_input(label = "Select size of final picture in pxl", 
                min_value=10,
                max_value=2000,
                value=400) // 2

st.write("Cropped images in middle:")

for uploaded_file, img in zip(uploaded_files, imgs):   
    # st.image(img, width=width)

    img_g, *_ = cv2.split(img)
    
    # Calculate the center of mass coordinates
    center_x = img_g.shape[1]//2
    center_y = img_g.shape[0]//2
    # print(center_x,center_y)
    
    # Cropping
    x1 = int(center_x - delta)
    x2 = int(center_x + delta)
    y1 = int(center_y - delta)
    y2 = int(center_y + delta)

    if x1 > 0 and x2 < img_g.shape[1] and y1 > 0 and y2 < img_g.shape[0]:
        img_g = img_g[y1:y2,x1:x2]
        # st.image(img, width=width)
    else:
        st.write('Unsuccessful cropping! Image is too small')
    
    file_names.append(uploaded_file.name)

    C = np.std(img_g) / np.mean(img_g)

    imgs_contrast.append(C)
    imgs_g.append(img_g)

st.image(imgs_g, width=width)


st.write("Colorized images:")
imgs_cmap = []

for img_g in imgs_g:
    
    img_cmap = cv2.cvtColor(cv2.applyColorMap(img_g, 2), cv2.COLOR_BGR2RGB)
    imgs_cmap.append(img_cmap)

st.image(imgs_cmap, width=width)

imgs_cmap = []

for img_g in imgs_g:
    
    img_cmap = cv2.applyColorMap(img_g, 2)
    imgs_cmap.append(img_cmap)


df_names = pd.DataFrame(file_names, columns=['file_name'])
df_contrasts = pd.DataFrame(imgs_contrast, columns=['contrast'])
df = pd.concat([df_names, df_contrasts], axis=1)                    

st.write("Contrasts in files:")
st.write(df)
# Creating new images and zip file

extension = st.selectbox("Choose the extension of new image files", ['png', 'jpg', 'tif'])

with tempfile.TemporaryDirectory() as temp_dir_name:

    df.to_csv(temp_dir_name + r"/" + "contrasts.csv")
    for uploaded_file, img_g, img_cmap, C in zip(uploaded_files, imgs_g, imgs_cmap, imgs_contrast):  
        str_c = str(round(C, 3))
        cv2.imwrite(temp_dir_name + r"/" + '.'.join(uploaded_file.name.split('.')[:-1]) + "_grey_C_" + str_c + "." + extension, img_g)
        cv2.imwrite(temp_dir_name + r"/" + '.'.join(uploaded_file.name.split('.')[:-1]) + "_color_C_" + str_c + "." + extension, img_cmap)


    path = os.getcwd()
    os.chdir(temp_dir_name)

    file_paths = []

    for f in os.scandir():
        if f.is_file():
            file_paths.append(f.path)

    # writing files to a zipfile 
    with ZipFile(temp_dir_name + r"/contrast.zip", "w") as zip: 
        # writing each file one by one 
        for file in file_paths: 
            zip.write(file)


    with open(temp_dir_name + r"/contrast.zip", "rb") as file:
        btn = st.download_button(
                label="Download new pictures in zip",
                data=file,
                file_name="contrast.zip",
                )
    
    os.chdir(path)
        
     