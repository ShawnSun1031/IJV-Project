import numpy as np
import cv2 
import json
import math
import matplotlib.pyplot as plt
import os
import sys

def convertUnit(length, voxelSize):
    numGrid = length / voxelSize
    return numGrid

def make_volume(subject, date, state, voxelLength):
    '''
    the unit using here is millimeter (mm)
    '''
    # model
    modelX = convertUnit(132, voxelLength)
    modelY = convertUnit(35, voxelLength)
    modelZ = convertUnit(35, voxelLength)
    # source
    srcHolderX = convertUnit(20, voxelLength)
    srcHolderY = convertUnit(20, voxelLength)
    srcHolderZ = convertUnit(10, voxelLength)
    irraWinRadius = convertUnit(1.5, voxelLength)
    # detector
    detHolderX = convertUnit(20, voxelLength)
    detHolderY = convertUnit(25, voxelLength)
    detHolderZ = convertUnit(6, voxelLength)
    # prismX = convertUnit(20)  # prismX = detHolderX
    prismY = convertUnit(5, voxelLength)
    prismZ = convertUnit(5, voxelLength)
    # 0.3675
    fiberR = convertUnit(0.3675, voxelLength)

    # start to construct
    # model and air (in the beginning)
    vol = np.ones((int(modelX), int(modelY), int(modelZ)))
    # source
    angle = 9
    center_x = int(modelX//2)
    center_y = int(modelY//2)
    
    source_x = list(range(int(modelX//2-srcHolderX//2),int(modelX//2+srcHolderX//2)))
    source_y = list(range(int(modelY//2-srcHolderY//2),int(modelY//2+srcHolderY//2)))
    rot_source_x, rot_source_y = rotate(source_x, source_y, center_x, center_y, angle=angle)
    for xx, yy in zip(rot_source_x, rot_source_y):
        xx_ceil, yy_ceil = math.ceil(xx), math.ceil(yy)
        xx_floor, yy_floor = math.floor(xx), math.floor(yy)
        vol[xx_ceil,yy_ceil,:int(detHolderZ)] = 2  # holder
        vol[xx_floor,yy_floor,:int(detHolderZ)] = 2  # holder
    
    for x in range(int(modelX//2)-int(np.ceil(irraWinRadius)), int(modelX//2)+int(np.ceil(irraWinRadius))):
        for y in range(int(modelY//2)-int(np.ceil(irraWinRadius)), int(modelY//2)+int(np.ceil(irraWinRadius))):
            isDist1 = np.sqrt((modelX//2-x)**2 + (modelY//2-y)
                            ** 2) < np.ceil(irraWinRadius)
            isDist2 = np.sqrt((modelX//2-(x+1))**2 + (modelY//2-y)
                            ** 2) < np.ceil(irraWinRadius)
            isDist3 = np.sqrt((modelX//2-x)**2 + (modelY//2-(y+1))
                            ** 2) < np.ceil(irraWinRadius)
            isDist4 = np.sqrt((modelX//2-(x+1))**2 +
                            (modelY//2-(y+1))**2) < np.ceil(irraWinRadius)
            if isDist1 or isDist2 or isDist3 or isDist4:
                vol[x][y] = 1  # air
    # detector
    firts_holder_x = list(range(int(modelX//2+srcHolderX//2),int(modelX//2+srcHolderX//2+detHolderX)))
    firts_holder_y = list(range(int(modelY//2-detHolderY//2),int(modelY//2+detHolderY//2)))
    rot_firts_holder_x, rot_firts_holder_y = rotate(firts_holder_x, firts_holder_y, center_x, center_y, angle=angle)
    for xx, yy in zip(rot_firts_holder_x, rot_firts_holder_y):
        xx_ceil, yy_ceil = math.ceil(xx), math.ceil(yy)
        xx_floor, yy_floor = math.floor(xx), math.floor(yy)
        vol[xx_ceil,yy_ceil,:int(detHolderZ)] = 2  # first holder
        vol[xx_floor,yy_floor,:int(detHolderZ)] = 2  # first holder
    
    second_holder_x = list(range(int(modelX//2-srcHolderX//2-detHolderX),int(modelX//2-srcHolderX//2)))
    second_holder_y = list(range(int(modelY//2-detHolderY//2),int(modelY//2+detHolderY//2)))
    rot_second_holder_x, rot_second_holder_y = rotate(second_holder_x, second_holder_y, center_x, center_y, angle=angle)
    for xx, yy in zip(rot_second_holder_x, rot_second_holder_y):
        xx_ceil, yy_ceil = math.ceil(xx), math.ceil(yy)
        xx_floor, yy_floor = math.floor(xx), math.floor(yy)
        vol[xx_ceil,yy_ceil,:int(detHolderZ)] = 2  # second holder
        vol[xx_floor,yy_floor,:int(detHolderZ)] = 2  # second holder
    
    first_prism_x = list(range(int(modelX//2+srcHolderX//2),int(modelX//2+srcHolderX//2+detHolderX)))
    first_prism_y = list(range(int(modelY//2-prismY//2),int(modelY//2+prismY//2)))
    rot_first_prism_x, rot_first_prism_y = rotate(first_prism_x, first_prism_y, center_x, center_y, angle=angle)
    for xx, yy in zip(rot_first_prism_x, rot_first_prism_y): 
        xx_ceil, yy_ceil = math.ceil(xx), math.ceil(yy)
        xx_floor, yy_floor = math.floor(xx), math.floor(yy)
        vol[xx_ceil,yy_ceil,int(detHolderZ-prismZ):int(detHolderZ)] = 3  # first prism
        vol[xx_floor,yy_floor,int(detHolderZ-prismZ):int(detHolderZ)] = 3  # first prism
        
    second_prism_x = list(range(int(modelX//2-srcHolderX//2-detHolderX),int(modelX//2-srcHolderX//2)))
    second_prism_y = list(range(int(modelY//2-prismY//2),int(modelY//2+prismY//2)))
    rot_second_prism_x, rot_second_prism_y = rotate(second_prism_x, second_prism_y, center_x, center_y, angle=angle)
    for xx, yy in zip(rot_second_prism_x, rot_second_prism_y):
        xx_ceil, yy_ceil = math.ceil(xx), math.ceil(yy)
        xx_floor, yy_floor = math.floor(xx), math.floor(yy)
        vol[xx_ceil,yy_ceil,int(detHolderZ-prismZ):int(detHolderZ)] = 3  # second prism
        vol[xx_floor,yy_floor,int(detHolderZ-prismZ):int(detHolderZ)] = 3  # second prism
    
    first_fiber_x = list(range(int(modelX//2+srcHolderX//2),int(modelX//2+srcHolderX//2+detHolderX)))
    first_fiber_y = list(range(int(modelY//2-prismY//2),int(modelY//2+prismY//2)))
    rot_first_fiber_x, rot_first_fiber_y = rotate(first_fiber_x, first_fiber_y, center_x, center_y, angle=angle)
    for xx, yy in zip(rot_first_fiber_x, rot_first_fiber_y):
        xx_ceil, yy_ceil = math.ceil(xx), math.ceil(yy)
        xx_floor, yy_floor = math.floor(xx), math.floor(yy)
        vol[xx_ceil,yy_ceil,:int(detHolderZ-prismZ)] = 0  # first fiber
        vol[xx_floor,yy_floor,:int(detHolderZ-prismZ)] = 0  # first fiber
        
    second_fiber_x = list(range(int(modelX//2-srcHolderX//2-detHolderX),int(modelX//2-srcHolderX//2)))
    second_fiber_y = list(range(int(modelY//2-prismY//2),int(modelY//2+prismY//2)))
    rot_second_fiber_x, rot_second_fiber_y = rotate(second_fiber_x, second_fiber_y, center_x, center_y, angle=angle)
    for xx, yy in zip(rot_second_fiber_x, rot_second_fiber_y):
        xx_ceil, yy_ceil = math.ceil(xx), math.ceil(yy)
        xx_floor, yy_floor = math.floor(xx), math.floor(yy)
        vol[xx_ceil,yy_ceil,:int(detHolderZ-prismZ)] = 0  # first fiber
        vol[xx_floor,yy_floor,:int(detHolderZ-prismZ)] = 0  # first fiber

    # muscle
    vol[:, :, int(detHolderZ):] = 6
    # fat
    fatDepth = int(fat_x*scalePercentage)
    vol[:, :, int(detHolderZ):int(detHolderZ)+fatDepth] = 5
    # skin
    skinDepth = int(skin_x*scalePercentage)
    vol[:, :, int(detHolderZ):int(detHolderZ)+skinDepth] = 4
    # ijv  # 7 for perturbed region
    shiftNumber = np.round(modelY//2 - np.mean(np.round(ijv_pos[1]*scalePercentage).astype(np.int32)), 0).astype(int)
    vol[:, np.round(ijv_pos[1]*scalePercentage).astype(np.int32) + shiftNumber, np.round(ijv_pos[0]*scalePercentage).astype(np.int32)+int(detHolderZ)] = 7 if state == "IJVLarge" else 8
    # cca
    vol[:, np.round(cca_pos[0]*scalePercentage).astype(np.int32) + shiftNumber, np.round(cca_pos[1]*scalePercentage).astype(np.int32)+int(detHolderZ)-4] = 9

    # save voxel 
    vol = vol.astype(np.uint8)
    np.save(file=os.path.join('result', subject, f"{subject}_{date}_{state}_segment.npy"), arr=vol)
    
    return vol

def rotate(vector_x, vector_y, center_x, center_y, angle):
    X, Y = np.meshgrid(vector_x,vector_y)
    angle = math.radians(angle)
    Xr   =  np.cos(angle)*(X-center_x) + np.sin(angle)*(Y-center_y) + center_x    # "cloclwise"
    Yr   = -np.sin(angle)*(X-center_x) + np.cos(angle)*(Y-center_y) + center_y
    Xr = Xr.reshape(-1)
    Yr = Yr.reshape(-1)
    return Xr, Yr

def merge_small_large(small_vol, large_vol):
    # merge large and small file to complete contruction for one segementation
    small = small_vol
    large = large_vol
    cross_area = np.where((large == 7) & (small == 6)) # large == 7 --> area of large IJV, small == 6 --> area of small muscle
    for i in range(0, len(cross_area[0])):
        small[cross_area[0][i], cross_area[1][i], cross_area[2][i]] = 7
    
    return small

if __name__ == "__main__":
    # %% parameters setting
    subject = "HW"
    date = "20230903"
    
    states = ["IJVLarge", "IJVSmall"]
    # %% load pre-process label & plot pre-process result
    os.makedirs(os.path.join("pic", subject), exist_ok=True)
    for state in states:
        with open(os.path.join("blood_vessel_segmentation_line_new.json")) as f:
            file = json.load(f)
            length10mmEdge = file[subject][date]["length10mmEdge"]
            bound = file[subject][date]['bound']
            skin_x = file[subject][date]['skin']['x']
            fat_x = file[subject][date]['fat']['x']
            cca_v = file[subject][date][state]['cca']['v']
        voxelLength = 0.25  # [mm]
        gridNumIn10mm = int(10/voxelLength)
        image = cv2.imread(f'{subject}_{date}_{state}.png', cv2.IMREAD_GRAYSCALE)
        image = image[bound[0]:bound[1]]
        scalePercentage = gridNumIn10mm / (length10mmEdge[1]-length10mmEdge[0])
        resize_Image = cv2.resize(image, (int(np.round(image.shape[1]*scalePercentage)), int(np.round(image.shape[0]*scalePercentage))), interpolation=cv2.INTER_AREA)
        ijv_pos = np.load(os.path.join('result', subject, f'{subject}_{date}_{state}_ijv_pos.npy'))
        cca_pos = np.load(os.path.join('result', subject, f'{subject}_{date}_{state}_cca_pos.npy'))

        vol = make_volume(subject, date, state, voxelLength)
        if state == "IJVLarge":
            large_vol = vol
        elif state == "IJVSmall":
            small_vol = vol
        else:
            raise Exception("Something wrong in your ijv-states setting ! (only IJVLarge or IJVSmall is valid)")
        np.save(os.path.join('result', subject, f'{subject}_{date}_{state}_vol.npy'), vol)
        plt.figure()
        plt.imshow(resize_Image, cmap="gray")
        plt.axhline(y=skin_x*scalePercentage, color='green') 
        plt.axhline(y=fat_x*scalePercentage, color='blue') 
        plt.plot(ijv_pos[1]*scalePercentage, ijv_pos[0]*scalePercentage, "r.", markersize=1)
        plt.plot(cca_pos[0]*scalePercentage, cca_pos[1]*scalePercentage, "r.", markersize=1)
        plt.colorbar()
        plt.savefig(os.path.join("pic", subject, f"{subject}_{date}_{state}_segment_result.png"), dpi=300, format='png', bbox_inches='tight')
        plt.show()
        
    merge_vol = merge_small_large(small_vol=small_vol, 
                                  large_vol=large_vol)
    np.save(os.path.join('result', subject, f'{subject}_{date}_merge_vol.npy'), merge_vol)
    plt.figure()
    plt.imshow(merge_vol[merge_vol.shape[0]//2, :, :])
    plt.show()
    plt.figure()
    plt.imshow(merge_vol[merge_vol.shape[0]//2, :, :].T)
    plt.savefig(os.path.join("pic", subject, "merge_transverse_plane.png"), dpi=300, format='png', bbox_inches='tight')
    plt.show()
    plt.figure()
    plt.imshow(merge_vol[:, :, 0])
    plt.savefig(os.path.join("pic", subject, "merge_sagittal_plane.png"), dpi=300, format='png', bbox_inches='tight')
    plt.show()
    plt.figure()
    plt.imshow(merge_vol[:, merge_vol.shape[1]//2, :].T)
    plt.savefig(os.path.join("pic", subject, "merge_coronal_plane.png"), dpi=300, format='png', bbox_inches='tight')
    plt.show()