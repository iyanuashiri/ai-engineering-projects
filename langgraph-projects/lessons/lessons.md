
## Challenges with building AI Agents and applications

1. Latency - LLMs have long latencies, sometimes in seconds versus millisenconds. Current reasoning models can take even longer. Langgragh supports two points - Parallel execution of tasks. If you have N tasks, and run them in parallel, you can reduce latency by a factor of N. The second is streaming - to save perceived latency  

2. Reliability - Long running agents can fail which is expensive and time consuming. Langgraoh includes checkpointing to reduce the cost of each retry. A restarted application can then resume exactly where it left off. Checkpointing and maintaining state are prominent themes in LangGraph

3. Non-deterministic nature of LLMs - LLMs have variable responses. Further, different models produce different results and models are replaced all the times. For some applications, this will necessitate human approvals, and in all. First LangGraph implement a human-in-the-lopp to collaborate with the user. Human in the loop suspends the agents to await human input. Second, it supports tracing and evaluation with LangSmith  


## Understanding the LangGraph Ecosystem

1. LangChain prvides models and tools

2. LangGraph

3. LangSmith Deployments for deploying the LLMs agents

4. Studio and LangSmith provide useful debugging, evaluation, tracing, and testing capabilities. 



## There are 5 LangGraph concepts

1. State

2. Nodes

3. Edges

4. Memory

5. Interrupts