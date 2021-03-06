import random
import copy

Agent_Num,Task_Num=2,15
Step=50
Table=[[0,0,0,0,0,0,0,0,0,0,0,0],[0,1,1,1,1,1,1,2,1,1,1,0],[0,1,0,2,0,1,0,0,1,0,1,0],[0,2,0,1,0,1,0,0,1,0,1,0],
       [0,1,0,1,1,2,1,1,1,1,1,0],[0,1,1,1,0,0,0,1,0,0,2,0],[0,1,0,1,1,1,1,1,1,0,1,0],[0,1,0,0,0,1,0,0,2,0,1,0],
       [0,1,0,1,1,1,2,1,1,1,1,0],[0,2,0,1,0,0,1,0,0,0,1,0],[0,1,1,1,2,1,1,1,1,2,1,0],[0,0,0,0,0,0,0,0,0,0,0,0]]
access=[(i,j) for i in range(12) for j in range(12) if Table[i][j]]
gentask=[(i,j) for i in range(12) for j in range(12) if Table[i][j]==2]

def task_generate():
    start,end=random.choice(gentask),random.choice(gentask)
    while start==end: end=random.choice(gentask)
    return (start,end)

def update():
    for i in range(12):
        for j in range(12): Table2[i][j],Table_nex[i][j]=Table[i][j],Table[i][j]
    for agent in Agents:
        agent.pushed,agent.wait,agent.pushing=False,False,None
        agent.limited,agent.go=False,None
        Table2[agent.loc[0]][agent.loc[1]]=agent.id+10

class Agent:
    ID=0
    def __init__(self,loc):
        self.id=Agent.ID
        Agent.ID+=1
        self.loc=loc
        self.target=None
        self.task=None
        self.state="fetch"
        self.nex=None
        self.priority=0
        self.pushing=None
        self.pushed=False
        self.wait=False
        self.limited=False
        self.go=None

    def select_task_random(self):
        self.task=task_generate()
        self.target,self.state=self.task[0],"fetch"
        if self.target==self.loc: self.target,self.state=self.task[1],"deliver" 
    
    def learn(self):
        rnd=random.random()
        if rnd<e: index=random.randint(0,len(connection[self.loc])-1)
        else:
            lis=list(q_table[self.target][self.loc].values())
            index=lis.index(max(lis))
        next_loc=connection[self.loc][index]
        if next_loc==self.target: td=r-q_table[self.target][self.loc][next_loc]
        else: td=-1+gamma*(max(q_table[self.target][next_loc].values()))-q_table[self.target][self.loc][next_loc]
        q_table[self.target][self.loc][next_loc]+=a*td
        self.loc=next_loc
        if self.loc==self.target:
            if self.state=="fetch": self.target,self.state=self.task[1],"deliver"
            else: self.select_task_random()

    def select_task(self):
        taskid,M=0,0
        for i,task in enumerate(Tasks):
            if task[0]==self.loc:
                taskid=i
                break
            Q=q_table[task[0]][self.loc][0][1]
            if Q>M: M,taskid=Q,i
        self.task=Tasks.pop(taskid)
        Tasks.append(task_generate())
        self.target,self.state=self.task[0],"fetch"
        if self.target==self.loc: self.target,self.state=self.task[1],"deliver" 

    def prior(self): #prirityはNNで決める
        self.priority=self.id/10
        first=q_table[self.target][self.loc][0]
        second=q_table[self.target][self.loc][1]
        if first[1]>10 and first[1]>1.6*second[1]:
            self.priority+=first[1]
            self.limited=True
            self.go=first[0]

    def decide(self):
        if self.pushed:
            for pos,val in q_table[self.target][self.loc]:
                if Table_nex[pos[0]][pos[1]]<10 and self.pushing.loc!=pos:
                    self.nex=pos
                    break
            if self.nex==self.loc:
                self.wait=True
                agent=self
                while agent.pushed:
                    agent=agent.pushing
                    Table_nex[agent.nex[0]][agent.nex[1]]=Table[agent.nex[0]][agent.nex[1]]
                    agent.wait,agent.nex=True,agent.loc
                    Table_nex[agent.loc[0]][agent.loc[1]]=agent.id+10
        else:
            if self.limited:
                if Table_nex[self.go[0]][self.go[1]]<10: self.nex=self.go
                else: pass
            else:
                for pos,val in q_table[self.target][self.loc]:
                    if Table_nex[pos[0]][pos[1]]<10:
                        self.nex=pos
                        break
            if self.nex==self.loc: self.wait=True
        
        if (not self.wait) and Table2[self.nex[0]][self.nex[1]]>=10:
            agent=Agents[Table2[self.nex[0]][self.nex[1]]-10]
            if agent.priority<self.priority:
                agent.pushing,agent.pushed,agent.priority=self,True,self.priority
                ids.remove(agent.id)
                ids.insert(0,agent.id)

        Table_nex[self.nex[0]][self.nex[1]]=self.id+10

    def move(self):
        self.loc=self.nex
        if self.loc==self.target:
            if self.state=="fetch": self.target,self.state=self.task[1],"deliver"
            else: self.select_task()

connection,q_table={},{}
e,a,r,gamma=0.998,0.06,50,0.9
diff=[(1,0),(0,1),(-1,0),(0,-1)]
Dist=lambda loc,tar: abs(loc[0]-tar[0])+abs(loc[1]-tar[1])
for pos in access: connection[pos]=[(pos[0]+diff[i][0],pos[1]+diff[i][1]) for i in range(4) if Table[pos[0]+diff[i][0]][pos[1]+diff[i][1]]]
for target in gentask:
    tmp={}
    for key,val in connection.items(): tmp[key]={pos:19-Dist(pos,target) for pos in val}
    q_table[target]=tmp
learn_agent=Agent(random.choice(gentask))
learn_agent.select_task_random()
for _ in range(1000000):
    learn_agent.learn()
    e*=0.998
for pos in gentask:
    dic=q_table[pos]
    for key,val in dic.items(): dic[key]=sorted(val.items(),key=lambda x:x[1],reverse=True)
    visited=set()
    loop=set()
    for i in range(12):
        for j in range(12):
            now=(i,j)
            if (not Table[i][j]) or (now in visited): continue
            line=set()
            while True:
                line.add(now)
                if now==pos or (now in visited):
                    for k in line: visited.add(k)
                    break
                now=q_table[pos][now][0][0]
                if now in line:
                    for k in line: loop.add(k)
                    break
    while loop:
        delete=set()
        for k in loop:
            adj=q_table[pos][k]
            for i,loc in enumerate(adj):
                if loc[0] in visited:
                    tmp=adj[0]
                    adj[0]=adj[i]
                    adj[i]=tmp
                    delete.add(k)
                    visited.add(k)
                    break
        for d in delete: loop.remove(d)

Agent.ID=0
Agents=[Agent(loc) for loc in random.sample(gentask,Agent_Num)]
Tasks=[task_generate() for _ in range(Task_Num)]
Table2=copy.deepcopy(Table)
Table_nex=copy.deepcopy(Table)
for agent in Agents: agent.select_task()
for step in range(Step):
    update()
    ids=[i for i in range(Agent_Num)]
    for agent in Agents: agent.prior()
    ids.sort(key=lambda x:Agents[x].priority,reverse=True)
    for _ in range(Agent_Num):
        agent=Agents[ids.pop(0)]
        agent.decide()
    for agent in Agents: agent.move()

    locate=[]
    for agent in Agents:
        if agent.state=="deliver": locate.append("1,"+str(agent.loc[0])+","+str(agent.loc[1])+".")
        else: locate.append("0,"+str(agent.loc[0])+","+str(agent.loc[1])+".")
    with open('./csvs/path'+str(step),'w') as file: file.writelines(locate)