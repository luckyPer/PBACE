# PTSG: a test generation tool based on  Extended Finite State Machine (EFSM)

## Introduction

PTSG, which can provide an underlying service for the implementation of testing algorithms, makes test case generation easier and more efficient. It automatically builds an executable EFSM model in memory according to the system specification and opens a service interface to interact with the model. By relying on the services provided by the tool, the business logic in the test generation algorithm can be decoupled from the cumbersome interaction with the model, and the tester can focus on implementing the test case generation algorithm itself without having to consider the operational details of interacting with the model.

## How to use

1. The user needs to define the model file description in the Specification folder with the Json syntax according to the EFSM model specification.
2. Take the model specification as input and use LoadEFSM in the EFSMparser module to get the parsed dynamic EFSM object.
3. Some basic model information is available in the EFSM object. The is_feasible method can be used to determine if the current transition is executable, and then the execute method can be used to update the variables involved in the action.

## P.S.

PTSG supports python3

The parsing syntax for EFSM is using [GOLD Parser](http://www.goldparser.org/)

We use [PyAuParser](https://github.com/veblush/PyAuParser) as the parsing engine

Address of the preview version of the paper[PTSG](https://arxiv.org/abs/2209.10255)

