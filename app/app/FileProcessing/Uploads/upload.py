import numpy as np
import numpy.random as rnd
import torch as pt

import math
from gym import spaces, logger
from gym.utils import seeding

###
import sys
sys.path.insert(0, '/home/pi/pendulum/System')
###


from System.system import System
#from . import System
import time
from sys import exit

class SwingUpEnv():
    """
    Description:
        A pole is attached by an un-actuated joint to a cart, which moves along a frictionless track. The pendulum starts upright, and the goal is to prevent it from falling over by increasing and reducing the cart's velocity.

    Source:
        This environment corresponds to the version of the cart-pole problem described by Barto, Sutton, and Anderson

    Observation: 
        Type: Box(4)
        Num	Observation                 Min         Max
        0	Cart Position             -4.8            4.8
        1	Cart Velocity             -Inf            Inf
        2	Pole Angle                 -Inf           Inf
        3	Pole Velocity At Tip      -Inf            Inf
        
    Actions:
        Type: Box(1)
        Num	Action                      Min         Max
        0	Push cart                   -1          1
        
        Note: The amount the velocity that is reduced or increased is not fixed; it depends on the angle the pole is pointing. This is because the center of gravity of the pole increases the amount of energy needed to move the cart underneath it

    Reward:
        Reward is 1 for every step taken, including the termination step

    Starting State:
        All observations are assigned a uniform random value in [-0.05..0.05]

    Episode Termination:
        Pole Angle is more than 12 degrees
        Cart Position is more than 2.4 (center of the cart reaches the edge of the display)
        Episode length is greater than 200
        Solved Requirements
        Considered solved when the average reward is greater than or equal to 195.0 over 100 consecutive trials.
    """
    
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second' : 50
    }

    def __init__(self):
        self.x_threshold = 14.
        self.sys = System(angular_units='Radians', positive_limit=self.x_threshold, negative_limit=-self.x_threshold, sw_limit_routine=self.x_threshold_routine)
		
        self.force_mag = 11.
        self.last_time = time.time()  # time for seconds between updates

        # Angle at which to fail the episode
        self.x_dot_threshold = 10.
        self.theta_dot_threshold = 3*np.pi

        # Angle limit set to 2 * theta_threshold_radians so failing observation is still within bounds
        high = np.array([self.x_threshold*2, self.x_dot_threshold, np.finfo(np.float32).max, np.finfo(np.float32).max])

        
        self.action_space = spaces.Box(-np.ones(1), np.ones(1), dtype = np.float32)

        self.seed()
        self.state = None

        self.steps_beyond_done = None
        self.done = False

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        assert self.action_space.contains(action), "%r (%s) invalid"%(action, type(action))
        state = self.state
        x, x_dot, theta, theta_dot = state
        force = self.force_mag * action[0]
        # Do not adjust the motor further if the x_threshold has been triggered by the SW limit
        if self.done == False:
            self.sys.adjust(force)

        costheta = math.cos(theta)
        sintheta = math.sin(theta)

        if costheta > 0:
            self.up_time += 1
            self.max_up_time = np.max([self.up_time, self.max_up_time])

        else:
            self.up_time = 0

        current_time = time.time()
        tau = current_time - self.last_time
        self.last_time = current_time
        
        new_theta, new_x = self.sys.measure()
        if (theta >= 0 and theta < math.pi/2.) and (new_theta > 3.*math.pi/2.):
            theta_dot = (new_theta - (theta + 2.*math.pi)) / tau
        elif (new_theta >= 0 and new_theta < math.pi/2.) and (theta > 3.*math.pi/2.):
            theta_dot = ((new_theta + 2.*math.pi) - theta) / tau
        else:
            theta_dot = (new_theta - theta) / tau
        x_dot = (new_x - x) / tau
        self.state = (new_x, x_dot, new_theta, theta_dot)
        self.sys.add_results(new_theta, new_x, force)

        '''done =  theta_dot < -self.theta_dot_threshold \
                or theta_dot > self.theta_dot_threshold \
                or self.done == True'''
        done = self.done
        
        '''done =  x < -self.x_threshold \
                or x > self.x_threshold \
                or theta_dot < -self.theta_dot_threshold \
                or theta_dot > self.theta_dot_threshold \
                or self.done == True'''
        done = bool(done)

        if not done:
            reward = np.ceil(costheta)
        elif self.steps_beyond_done is None:
            # Pole just fell!
            self.steps_beyond_done = 0
            reward = -( 100 * (np.abs(x_dot) + np.abs(theta_dot)) )
        else:
            if self.steps_beyond_done == 0:
                logger.warn("You are calling 'step()' even though this environment has already returned done = True. You should always call 'reset()' once you receive 'done = True' -- any further steps are undefined behavior.")
            self.steps_beyond_done += 1
            reward = 0.0

        return np.array(self.state), reward, done, {'max_up_time' : self.max_up_time}

    def x_threshold_routine(self):
        print("SW Limit reached!")
        self.done = True
        self.sys.adjust(0)

    def reset(self, home = True):
        if home == True:
            self.sys.return_home()
        time.sleep(1)
        init_ang, lin = self.sys.measure()
        time.sleep(0.05)
        ang, lin = self.sys.measure()
        self.state = (0, 0, ang, (ang-init_ang)/0.05)

        self.up_time = 0
        self.max_up_time = 0
        self.up = False
        self.steps_beyond_done = None
        self.done = False
        return np.array(self.state)
        
    def end(self):
        self.sys.deinitialize()
        
    def log(self, message):
        self.sys.add_log(message)
        print(message)


class nnQ(pt.nn.Module):
    """
    Here is a basic neural network with for representing a policy 
    """
    
    def __init__(self, stateDim, numActions, numHiddenUnits, numLayers):
        super().__init__()
        
        InputLayer = [pt.nn.Linear(stateDim + numActions, numHiddenUnits),
                      pt.nn.ReLU()]
        
        HiddenLayers = []
        for _ in range(numLayers - 1):
            HiddenLayers.append(pt.nn.Linear(numHiddenUnits, numHiddenUnits))
            HiddenLayers.append(pt.nn.ReLU())
            
        
        OutputLayer = [pt.nn.Linear(numHiddenUnits, 1)]
        
        AllLayers = InputLayer + HiddenLayers + OutputLayer
        self.net = pt.nn.Sequential(*AllLayers)
        
        self.numActions = numActions
        
    def forward(self,x,a):
        x = pt.tensor(x, dtype = pt.float32)

        b = pt.nn.functional.one_hot(pt.tensor(a).long(), self.numActions)
        
        c = b.float().detach()
        y = pt.cat([x, c])
        
        return self.net(y)
        
class deepQagent:
    def __init__(self,stateDim,numActions,numHiddenUnits,numLayers,epsilon=.1,gamma=.9,alpha=.1,
                c = 100,batch_size=20):
        self.Q = nnQ(stateDim,numActions,numHiddenUnits,numLayers)
        self.Q_target = nnQ(stateDim,numActions,numHiddenUnits,numLayers)
        
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.numActions = numActions
        
        self.D = []
        self.batch_size = batch_size
        self.c = c
        self.optimizer = pt.optim.SGD(self.Q.parameters(),lr=alpha)
        self.counter = 0
    
    def action(self,x):
        # This is an epsilon greedy selection
        if rnd.rand() < self.epsilon:
            a = rnd.randint(numActions)
        else:
            qBest = -np.inf
            for aTest in range(self.numActions):
                qTest = self.Q(x,aTest).detach().numpy()[0]
                if qTest > qBest:
                    qBest = qTest
                    a = aTest
        return a
    
    def update(self,s,a,r,s_next,done):
        self.counter += 1
        self.D.append((s,a,r,s_next,done))

        B_ind = rnd.choice(len(self.D),size=self.batch_size)

        loss = 0.

        #B_ind = [-1]
        for j in B_ind:
            sj,aj,rj,s_next_j,done_j = self.D[j]
            Q_cur = self.Q(sj,aj)
            if done_j:
                y = rj
            else:
                
                Q_vals = []
                for a_next in range(self.numActions):
                    
                    Q_vals.append(self.Q_target(s_next_j,a_next).detach().numpy()[0])
                    
                
                y = rj + self.gamma * np.max(Q_vals)
            loss += .5 * (y-Q_cur)**2 / self.batch_size
        self.optimizer.zero_grad()
        #self.Q.zero_grad()
        loss.backward()
        self.optimizer.step()
        
      
        if (self.counter % self.c) == 0:
            for p, p_target in zip(self.Q.parameters(),self.Q_target.parameters()):
                p_target.data = p.data.clone().detach()

class sarsaAgent:
    def __init__(self, stateDim, numActions, numHiddenUnits, numLayers,
                 epsilon = .1, gamma = .9, alpha = .1):
        self.Q = nnQ(stateDim, numActions, numHiddenUnits, numLayers)
        self.gamma = gamma
        self.epsilon = epsilon
        self.alpha = alpha
        self.numActions = numActions
        self.s_last = None

    def action(self, x):
        # This is an epsilon greedy selection
        a = 0
        if rnd.rand() < self.epsilon:
            a = rnd.randint(0, numActions)
        else:
            qBest = -np.inf
            for aTest in range(self.numActions):
                qTest = self.Q(x, aTest).detach().numpy()[0]
                if qTest > qBest:
                    qBest = qTest
                    a = aTest
        return a
    
    def update(self, s, a, r, s_next,done):
        # Compute the TD error, if there is enough data
        update = True
        if done:
            Q_cur = self.Q(s, a).detach().numpy()[0]
            delta = r - Q_cur
            self.s_last = None
            Q_diff = self.Q(s, a)
        elif self.s_last is not None:
            Q_next = self.Q(s, a).detach().numpy()[0]
            Q_cur = self.Q(self.s_last, self.a_last).detach().numpy()[0]
            delta = self.r_last + self.gamma * Q_next - Q_cur
            Q_diff = self.Q(self.s_last, self.a_last)
        else:
            update = False
            
        # Update the parameter via the semi-gradient method
        if update:
            self.Q.zero_grad()
            Q_diff.backward()
            for p in self.Q.parameters():
                p.data.add_(self.alpha * delta, p.grad.data)

        if not done:
            self.s_last = np.copy(s)
            self.a_last = np.copy(a)
            self.r_last = np.copy(r)

# This is the environment
env = SwingUpEnv()

# For simplicity, we only consider forces of -1 and 1
numActions = 2
Actions = np.linspace(-1, 1, numActions)

# This is our learning agent
gamma = .95
#agent = sarsaAgent(5, numActions, 20, 1, epsilon = 5e-2, gamma = gamma, alpha = 1e-5)
agent = deepQagent(5,numActions,20,2,epsilon=5e-2,gamma=gamma,batch_size=20,
                   c= 100,alpha=1e-4)

maxSteps = 2e6

# This is a helper to deal with the fact that x[2] is actually an angle
x_to_y = lambda x : np.array([x[0], x[1], np.cos(x[2]), np.sin(x[2]), x[3]])

R = []
UpTime = []

step = 0
ep = 0
maxLen = 500
try:
    while step < maxSteps:
        ep += 1
        x = env.reset(home = ep > 1)
        C = 0.
        
        done = False
        t = 1
        while not done:
            t += 1
            step += 1
            y = x_to_y(x)
            a = agent.action(y)
            u = Actions[a:a+1]
            x_next, c, done, info = env.step(u)
            
            max_up_time = info['max_up_time']
            y_next = x_to_y(x_next)

            C += (1./t) * (c - C)
            agent.update(y, a, c, y_next, done)
            x = x_next
            if done:
                break
                
            if step >= maxSteps:
                break
                
            if t > maxLen:
                agent.s_last = None
                break
                
            
            R.append(C)
        UpTime.append(max_up_time)
        #print('t:',ep+1,', R:',C,', L:',t-1,', G:',G,', Q:', Q_est, 'U:', max_up_time)
        log = "Episode:" + str(ep) + "   Total Steps:" + str(step) + "   Ave. Reward:" + str(C) + "   Episode Length:" + str(t-1) + "   Max Up-Time:" + str(max_up_time)
        env.log(log)
except:
    env.end()
    exit(-1)
finally:
    env.end()
    exit(0)
