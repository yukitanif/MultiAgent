import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import colors

Table=[[0,0,0,0,0,0,0,0,0,0,0,0],[0,1,1,1,1,1,1,2,1,1,1,0],[0,1,0,2,0,1,0,0,1,0,1,0],[0,2,0,1,0,1,0,0,1,0,1,0],
       [0,1,0,1,1,2,1,1,1,1,1,0],[0,1,1,1,0,0,0,1,0,0,2,0],[0,1,0,1,1,1,1,1,1,0,1,0],[0,1,0,0,0,1,0,0,2,0,1,0],
       [0,1,0,1,1,1,2,1,1,1,1,0],[0,2,0,1,0,0,1,0,0,0,1,0],[0,1,1,1,2,1,1,1,1,2,1,0],[0,0,0,0,0,0,0,0,0,0,0,0]]

lis=list(colors.BASE_COLORS.values())
for k in range(50):
    filename="./csvs/path"+str(k)
    fig=plt.figure()
    ax=plt.axes()
    for i in range(12):
        for j in range(12):
            if Table[i][j]==2:
                r=patches.Rectangle(xy=(i-0.5,j-0.5),width=1,height=1,fc='#FADBDA')
                ax.add_patch(r)
            elif Table[i][j]==1:
                r=patches.Rectangle(xy=(i-0.5,j-0.5),width=1,height=1,fc='#ffffff')
                ax.add_patch(r)
            else:
                r=patches.Rectangle(xy=(i-0.5,j-0.5),width=1,height=1,fc='#000000')
                ax.add_patch(r)
    with open(filename) as f:
        tmp=f.readline()
        tmp=list(tmp.split("."))
        for j in range(7):
            state,x,y=map(int,tmp[j].split(","))
            if state:
                c=patches.Circle(xy=(x,y),radius=0.4,fc=lis[j])
                ax.add_patch(c)
            else:
                c=patches.Circle(xy=(x,y),radius=0.4,ec=lis[j],fill=False)
                ax.add_patch(c)
    plt.axis("scaled")
    plt.title("Step"+str(k))
    plt.savefig("./maps/Step"+str(k)+".png")
    plt.close()
