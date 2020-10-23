import random
import copy

Agent_Num,Task_Num=7,15
Step=50
e,a,r,gamma=0.998,0.1,70,0.9
Table=[[0,0,0,0,0,0,0,0,0,0,0,0],[0,1,1,1,1,1,1,2,1,1,1,0],[0,1,0,2,0,1,0,0,1,0,1,0],[0,2,0,1,0,1,0,0,1,0,1,0],
       [0,1,0,1,1,2,1,1,1,1,1,0],[0,1,1,1,0,0,0,1,0,0,2,0],[0,1,0,1,1,1,1,1,1,0,1,0],[0,1,0,0,0,1,0,0,2,0,1,0],
       [0,1,0,1,1,1,2,1,1,1,1,0],[0,2,0,1,0,0,1,0,0,0,1,0],[0,1,1,1,2,1,1,1,1,2,1,0],[0,0,0,0,0,0,0,0,0,0,0,0]]
access=[(i,j) for i in range(1,11) for j in range(1,11) if Table[i][j]]
gentask=[(i,j) for i in range(1,11) for j in range(1,11) if Table[i][j]==2]
diff=[(1,0),(0,1),(-1,0),(0,-1)]
Dist=lambda loc,tar: abs(loc[0]-tar[0])+abs(loc[1]-tar[1])

def task_generate():
    start,end=random.choice(gentask),random.choice(gentask)
    while start==end: end=random.choice(gentask)
    return (start,end)

def update_tables():
    for i in range(1,11):
        for j in range(1,11):
            Table2[i][j]=Table[i][j]
            Table_nex[i][j]=Table[i][j]
    for agent in Agents: Table2[agent.loc[0]][agent.loc[1]]=agent.id+10

class Agent:
    ID=0
    def __init__(self,loc):
        self.id=Agent.ID
        Agent.ID+=1
        self.loc=loc
        self.target=None
        self.task=None
        self.state="fetch"
        self.nex=None #次に行きたいとこ
        self.priority=0
        self.pushing=None
        self.pushed=False
        self.wait=False

    def select_task_random(self):
        self.task=task_generate()
        self.target,self.state=self.task[0],"fetch"
        if self.target==self.loc: self.target,self.state=self.task[1],"deliver" 
    
    def learn(self):
        rnd=random.random()
        if rnd<e: index=random.randint(0,len(connection[self.loc])-1)
        else:
            lis=q_table[self.target][self.loc]  
            index=lis.index(max(lis))
        next_loc=connection[self.loc][index]
        if next_loc==self.target: td=r-q_table[self.target][self.loc][index]
        else: td=-1+gamma*(max(q_table[self.target][next_loc]))-q_table[self.target][self.loc][index]
        q_table[self.target][self.loc][index]=q_table[self.target][self.loc][index]+a*td
        self.loc=next_loc
        if self.loc==self.target:
            if self.state=="fetch": self.target,self.state=self.task[1],"deliver"
            else: self.select_task_random()

    def select_task(self):
        taskid,M=0,0
        for i,task in enumerate(Tasks):
           Q=max(q_table[task[0]][self.loc])
           if Q>M: M,taskid=Q,i
        self.task=Tasks.pop(taskid)
        Tasks.append(task_generate())
        self.target,self.state=self.task[0],"fetch"
        if self.target==self.loc: self.target,self.state=self.task[1],"deliver" 

    def prior(self):
        self.priority=self.id #tentative

    def decide(self):
        if self.pushed:
            M=0
            for pos,val in zip(connection[self.loc],q_table[self.target][self.loc]):
                if Table_nex[pos[0]][pos[1]]<10 and self.pushing.loc!=pos:
                    if val>M: M,self.nex=val,pos
            if M==0:
                self.wait=True
                self.nex=self.loc
                agent=self
                while agent.pushed:
                    agent=agent.pushing
                    Table_nex[agent.nex[0]][agent.nex[1]]=Table[agent.nex[0]][agent.nex[1]]
                    agent.wait=True
                    agent.nex=agent.loc
                    Table_nex[agent.loc[0]][agent.loc[1]]=agent.id+10
            elif Table2[self.nex[0]][self.nex[1]]>=10:
                agent=Agents[Table2[self.nex[0]][self.nex[1]]-10]
                if agent.priority>=self.priority: return
                agent.pushing=self
                agent.pushed=True
                agent.priority=self.priority
                ids.remove(agent.id)
                ids.insert(0,agent.id)
        else:
            M=0
            for pos,val in zip(connection[self.loc],q_table[self.target][self.loc]):
                if Table_nex[pos[0]][pos[1]]<10:
                    if val>M: M,self.nex=val,pos #later
            if M==0:
                self.wait=True
                self.nex=self.loc
            elif Table2[self.nex[0]][self.nex[1]]>=10:
                agent=Agents[Table2[self.nex[0]][self.nex[1]]-10]
                if agent.priority>=self.priority: return
                agent.pushing=self
                agent.pushed=True
                agent.priority=self.priority
                ids.remove(agent.id)
                ids.insert(0,agent.id)

        Table_nex[self.nex[0]][self.nex[1]]=self.id+10

    def move(self):
        self.loc=self.nex
        if self.loc==self.target:
            if self.state=="fetch": self.target,self.state=self.task[1],"deliver"
            else: self.select_task()
        #reset
        self.pushed=False
        self.wait=False
        self.pushing=None

##learn q_table###
connection,q_table={},{}
for pos in access:
    connection[pos]=[(pos[0]+diff[i][0],pos[1]+diff[i][1]) for i in range(4) if Table[pos[0]+diff[i][0]][pos[1]+diff[i][1]]]
for target in gentask:
    tmp={}
    for key,val in connection.items(): tmp[key]=[19-Dist(pos,target) for pos in val]
    q_table[target]=tmp
learn_agent=Agent(random.choice(gentask))
learn_agent.select_task_random()
for _ in range(120000):
    learn_agent.learn()
    e*=0.998

##test##
Agent.ID=0
Agents=[Agent(loc) for loc in random.sample(gentask,Agent_Num)]
Tasks=[task_generate() for _ in range(Task_Num)]
Table2=copy.deepcopy(Table)
Table_nex=copy.deepcopy(Table)
ids=[i for i in range(Agent_Num)]
for agent in Agents: agent.select_task()
for step in range(Step):
    update_tables()
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