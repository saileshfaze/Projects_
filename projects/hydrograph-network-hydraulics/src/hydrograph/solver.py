"""Newton solver for nodal continuity with quadratic pipe losses.

For each pipe q = sign(dh)*sqrt(abs(dh)/R). A small regularization
inside the square root makes the Jacobian finite near zero head difference.
"""
from dataclasses import dataclass
from math import sqrt
from .model import Network

@dataclass(frozen=True)
class Solution:
    heads: dict[str,float]
    flows: dict[str,float]
    residual: float
    iterations: int
    converged: bool
    def as_dict(self): return vars(self)

def _linear(a,b):
    n=len(b); a=[list(row)+[b[i]] for i,row in enumerate(a)]
    for j in range(n):
        pivot=max(range(j,n),key=lambda i:abs(a[i][j]))
        if abs(a[pivot][j]) < 1e-14: raise ArithmeticError('singular Jacobian')
        a[j],a[pivot]=a[pivot],a[j]
        div=a[j][j]
        for k in range(j,n+1): a[j][k]/=div
        for i in range(n):
            if i == j: continue
            m=a[i][j]
            for k in range(j,n+1): a[i][k]-=m*a[j][k]
    return [row[-1] for row in a]

def _evaluate(network,heads,epsilon):
    names=list(network.demands); index={name:i for i,name in enumerate(names)}
    balance=[-network.demands[x] for x in names]
    jac=[[0.0]*len(names) for _ in names]
    flows={}
    for p in network.pipes:
        delta=heads[p.start]-heads[p.end]
        # Smooth odd flow law, approaching sqrt(|dh|/R) outside epsilon.
        scale=sqrt(delta*delta+epsilon*epsilon)
        q=delta/sqrt(p.resistance*scale)
        dq=(delta*delta/2+epsilon*epsilon)/(sqrt(p.resistance)*scale**2.5)
        flows[p.name]=q
        for node,sign in ((p.start,-1),(p.end,1)):
            if node not in index:continue
            i=index[node];balance[i]+=sign*q
            for other,direction in ((p.start,1),(p.end,-1)):
                if other in index: jac[i][index[other]]+=sign*direction*dq
    return balance,jac,flows

def solve(network:Network,tolerance=1e-8,max_iterations=100,epsilon=1e-6):
    if tolerance<=0 or max_iterations<1 or epsilon<=0:raise ValueError('invalid solver settings')
    names=list(network.demands)
    heads={network.reservoir:network.reservoir_head,**{x:network.reservoir_head-1 for x in names}}
    for iteration in range(max_iterations+1):
        residual,jac,flows=_evaluate(network,heads,epsilon)
        norm=max((abs(x) for x in residual),default=0.0)
        if norm<tolerance:return Solution(heads,flows,norm,iteration,True)
        if iteration==max_iterations:break
        direction=_linear(jac,[-x for x in residual])
        step=1.0
        for _ in range(35):
            candidate={**heads,**{x:heads[x]+step*direction[i] for i,x in enumerate(names)}}
            next_res,_,_=_evaluate(network,candidate,epsilon)
            if max((abs(x) for x in next_res),default=0)<norm*(1-1e-4*step):break
            step*=0.5
        else:break
        heads=candidate
    return Solution(heads,flows,norm,iteration,False)

def continuity(network,solution):
    balances={x:-d for x,d in network.demands.items()}
    for p in network.pipes:
        if p.start in balances:balances[p.start]-=solution.flows[p.name]
        if p.end in balances:balances[p.end]+=solution.flows[p.name]
    return balances
