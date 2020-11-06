import random
import copy

Agent_Num,Task_Num=5,15
Step=50000
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
        for j in range(12):
            Table2[i][j]=Table[i][j]
            Table_nex[i][j]=Table[i][j]
    for agent in Agents:
        Table2[agent.loc[0]][agent.loc[1]]=agent.id+10
        agent.pushed=False
        agent.wait=False
        agent.pushing=None
        agent.path=[]

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
        self.path=[]

    def select_task_random(self):
        self.task=task_generate()
        self.target,self.state=self.task[0],"fetch"
        if self.target==self.loc: self.target,self.state=self.task[1],"deliver" 
    
    def learn(self):
        if random.random()<e: index=random.randint(0,len(connection[self.loc])-1) #ランダム行動
        else:
            lis=list(q_table[self.target][self.loc].values()) #greedy行動
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
            
    def reserve(self):
        tmp=self.loc
        for i in range(3): #3step分のマスを予定(≠予約)する
            self.path.append(tmp)
            if tmp==self.target: break
            tmp=q_table[self.target][tmp][0][0]

    def prior(self):
        self.priority=self.id/10
        """for pos in connection[self.loc]:
            if Table2[pos[0]][pos[1]]>=10: #接触しているエージェントがいるなら
                self.priority+=1000
                break
        for pos in connection[self.loc]: #周りの空きマスが大きいと優先度低くする
            if Table[pos[0]][pos[1]]: self.priority-=100
        self.priority+=q_table[self.target][self.loc][0][1]"""
                         
    def decide(self):
        if self.pushed: #priorityの高いagentから押されている時
            for pos,val in q_table[self.target][self.loc]: #避けられる対象の場所の中から
                if Table_nex[pos[0]][pos[1]]<10: #その場所を既に予約しているagentがいなく、押しているagentのいる場所と行きたい場所以外
                    if pos not in self.pushing.path or self.pushing.path[-1]==self.path[1]:
                        self.nex=pos
                        break
            if self.nex==self.loc: #上の条件に該当する場所が無いなら
                for pos,val in q_table[self.target][self.loc]: #避けられる対象の場所の中から
                    if Table_nex[pos[0]][pos[1]]<10 and pos!=self.pushing.loc: #その場所を既に予約しているagentがいない
                        self.nex=pos
                        break
            if self.nex==self.loc: #else
                self.wait=True #待つしかない
                agent=self
                while agent.pushed:
                    agent=agent.pushing
                    Table_nex[agent.nex[0]][agent.nex[1]]=Table[agent.nex[0]][agent.nex[1]]
                    agent.wait,agent.nex=True,agent.loc
                    Table_nex[agent.loc[0]][agent.loc[1]]=agent.id+10
        else: #押されていないときは、基本的に一番q-valueが高い所へ移動する。移動できないなら他の場所に移動したいが、結局今いるところに戻ってくるなら待つのがbest.  
            first=q_table[self.target][self.loc][0][0] #q_valueが一番高いloc
            if Table_nex[first[0]][first[1]]<10: self.nex=first #行きたい場所が空いてるなら行くしかない
            else:
                for pos,val in q_table[self.target][self.loc]:
                    if pos==self.target: break #その場所がtargetだった時、その場所で待つで確定。
                    elif q_table[self.target][pos][0][0]!=self.loc and Table_nex[pos[0]][pos[1]]<10: #行ったら別の道からtargetへ行けそうな時は、そっちの道から移動
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
e,a,r,gamma=0.998,0.06,50,0.93
diff=[(1,0),(0,1),(-1,0),(0,-1)]
Dist=lambda loc,tar: abs(loc[0]-tar[0])+abs(loc[1]-tar[1])
for pos in access: connection[pos]=[(pos[0]+diff[i][0],pos[1]+diff[i][1]) for i in range(4) if Table[pos[0]+diff[i][0]][pos[1]+diff[i][1]]]
for target in gentask:
    tmp={}
    for key,val in connection.items(): tmp[key]={pos:19-Dist(pos,target) for pos in val}
    q_table[target]=tmp
learn_agent=Agent(random.choice(gentask))
learn_agent.select_task_random()
for _ in range(500000):
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
    for agent in Agents: agent.reserve() 
    for agent in Agents: agent.prior() 
    ids.sort(key=lambda x:Agents[x].priority,reverse=True)
    for _ in range(Agent_Num):
        agent=Agents[ids.pop(0)]
        agent.decide()
    for agent in Agents: agent.move()
