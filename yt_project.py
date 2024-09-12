import numpy as np
import argparse
import cv2
import os
import argparse
import sys

prototxt = "model/colorization_deploy_v2.prototxt"
points = "model/pts_in_hull.npy"
model = "model/colorization_release_v2.caffemodel"



# Simulate command-line argumentsi78
#sys.argv = ['yt_project.py', '-i', 'path_to_your_image.jpg']
#sys.argv = ['yt_project.py', '-i', "images/sleep.jpeg"]

# Now, set up your argparse as before
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", type=str, required=True, help="Input to black and white img path")
args = vars(ap.parse_args())

# You can now access your image path as follows
image_path = args['image']



#Loading Model
net=cv2.dnn.readNetFromCaffe(prototxt,model)
pts=np.load(points)


class8=net.getLayerId("class8_ab")
conv8=net.getLayerId("conv8_313_rh")
pts=pts.transpose().reshape(2,313,1,1)
net.getLayer(class8).blobs=[pts.astype("float32")]
net.getLayer(conv8).blobs=[np.full([1,313], 2.606, dtype="float32")]


# image=cv2.imread(args['image'])
# scaled=image.astype("float32")/255
# lab=cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)
image_path = args['image']
image = cv2.imread(image_path)

# Check if the image was successfully loaded
if image is None:
    print(f"Error: Unable to load image at path '{image_path}'. Check the file path and try again.")
else:
    # Proceed with image processing
    scaled = image.astype("float32") / 255
    lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)


resized = cv2.resize(lab, (224,224))
l=cv2.split(resized)[0]
l-=50     #hyper paramater


print("Colouring the image")
net.setInput(cv2.dnn.blobFromImage(l))
ab=net.forward()[0,:,:,:].transpose((1,2,0))

ab=cv2.resize(ab, (image.shape[1], image.shape[0]))

l=cv2.split(lab)[0]
colorized = np.concatenate((l[:,:,np.newaxis],ab), axis=2)

colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
colorized = np.clip(colorized, 0, 1)

colorized = (255*colorized).astype("uint8")

# import pickle
# f=open('imgpkl.pickle', 'wb')
# pickle.dump(svn, f)

import pickle

# Save the colorized image to a pickle file
output_pickle_path = 'colorized_image.pickle'  # Specify your output pickle file path
with open(output_pickle_path, 'wb') as f:
    pickle.dump(colorized, f)

print(f"Colorized image saved to {output_pickle_path}")


# cv2.imshow("Original",image)
# cv2.imshow("Colorized",colorized)
# cv2.waitKey(0)

