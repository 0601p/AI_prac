import gym 
import random 
import math 
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from collections import deque
import matplotlib.pyplot as plt

#Hyper Parameter
EPISODES = 100   
EPS_START = 0.9 
EPS_END = 0.05
EPS_DECAY = 200  
GAMMA = 0.8    
LR = 0.001      
BATCH_SIZE = 32  

class DQNAgent:
    def __init__(self):
        self.model = nn.Sequential(
            nn.Linear(4, 128),
            nn.ReLU(),
            nn.Linear(128,256),
            nn.ReLU(),
            nn.Linear(256,512),
            nn.ReLU(),
            nn.Linear(512,256),
            nn.ReLU(),
            nn.Linear(256,128),
            nn.ReLU(),
            nn.Linear(128, 2)
        )
        self.optimizer = optim.Adam(self.model.parameters(), LR)
        self.steps_done = 0 
        self.memory = deque(maxlen=10000)
 
    def memorize(self, state, action, reward, next_state):
        self.memory.append((state,
                            action,
                            torch.FloatTensor([reward]),
                            torch.FloatTensor([next_state])))
    
    def act(self, state):
        eps_threshold = EPS_END + (EPS_START - EPS_END) * math.exp(-1. * self.steps_done / EPS_DECAY)
        self.steps_done += 1
        if random.random() > eps_threshold:
            return self.model(state).data.max(1)[1].view(1, 1)
        else:
            return torch.LongTensor([[random.randrange(2)]])
    
    def learn(self):
        if len(self.memory) < BATCH_SIZE:
            return
 
        batch = random.sample(self.memory, BATCH_SIZE) 
        states, actions, rewards, next_states = zip(*batch)
 
        states = torch.cat(states)
        actions = torch.cat(actions)
        rewards = torch.cat(rewards)
        next_states = torch.cat(next_states)
 
        current_q = self.model(states).gather(1, actions)
        
        max_next_q = self.model(next_states).detach().max(1)[0]
        expected_q = rewards + (GAMMA * max_next_q)
 
        loss = F.mse_loss(current_q.squeeze(), expected_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
 
env = gym.make('CartPole-v0')
agent = DQNAgent()
score_history = [] 
 
for e in range(1, EPISODES+1):
    state = env.reset()
    steps = 0
    while True:
        env.render()
        state = torch.FloatTensor([state]) 
        action = agent.act(state) 
        next_state, reward, done, _ = env.step(action.item())
        if done:
            reward = -1
        agent.memorize(state, action, reward, next_state) 
        agent.learn()
        state = next_state
        steps += 1
        if done:
            print("Eposide:{0} Score: {1}".format(e, steps))
            score_history.append(steps) 
            break
 
plt.plot(score_history)
plt.ylabel('score')
plt.show()