from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.animation as anm

fig=plt.figure(figsize=(6,9))
plt.axis("off")
ims=[]
for i in range(50):
    name="./maps/Step"+str(i)+".png"
    tmp=Image.open(name)
    ims.append([plt.imshow(tmp)])
ani=anm.ArtistAnimation(fig,ims,interval=250)
ani.save("test.gif")
