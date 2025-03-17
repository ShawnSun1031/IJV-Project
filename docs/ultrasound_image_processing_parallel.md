# Ultrasound Image Processing
## 1. get ultrasound image by screenshot to video
you need to find to geometry structure one for IJV systolic (IJV small), one for IJV diastolic (IJV large).

![](https://hackmd.io/_uploads/B13STWjl6.png)
![](https://hackmd.io/_uploads/HyNITWjlT.png)

## 2. S1_ijv_model_find_tissue.py
labeling each tissue type (skin, fat, muscle, ijv, cca)

1. for skin and fat, we find a boundary(straight line) to decide skin and fat.
2. for ijv, using GUI to get the region of IJV
3. for cca, we use circle equation to determine the region of cca
![](https://hackmd.io/_uploads/B19a0Zogp.png)

As the figure shown above, the from z=0 to green line is the skin area, from green line to blue line is fat area ... vice and versa.

Basically, how to run ***S1_ijv_model_find_tissue.py*** is according to ***blood_vessel_segmentation_line_new.json*** as shown below.

```
{
	"HW":{
		"20230903":{
			"bound": [3, 650],
			"length10mmEdge": [215, 445],
			"skin":{
				"__comment__": "axis-0 of imagee is x for line.",
				"x": 35
			},
			"fat":{
				"__comment__": "axis-0 of imagee is x for line.",
				"x":70
			},
			"IJVLarge":{
				"cca":{
					"__comment__":"[x, y, radius]",
					"v": [470, 500, 100]
				}
			},
			"IJVSmall":{
				"cca":{
					"__comment__":"[x, y, radius]",
					"v": [470, 500, 100]
				}
			}
		}
	}
}
```
** json file is a dictionary structure, if you don't know you can see the link https://tw.alphacamp.co/blog/json

** bound --> clip the image to what we want.

** length10mmEdge --> scale bar

## S2_ijv_model_seg_construct.py
1. make sure `subject` and `date` is synchronous with ***S1_ijv_model_find_tissue.py***
2. run the program

Then you will success to get the voxel file (*vol.npy) 

## S3_plot_3D_ijv_model.py
1. make sure `subject` and `date` is synchronous with ***S1_ijv_model_find_tissue.py***
2. run the program 

## Reference
To analyze ultrasound image by using **ImageJ**, please view [this document](https://hackmd.io/@aMXX54b3ToSm3kTNB_LuWQ/rJqy986g6).

---

**TODO :**     
oblique IJV model --> https://stackoverflow.com/questions/48818373/interpolate-between-two-images

https://stackoverflow.com/questions/59690451/how-to-turn-ct-segmentation-into-3d-model-in-python
