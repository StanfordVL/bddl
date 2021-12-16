# Interface with simulator 

## Summary 
As explained in the [paper](https://arxiv.org/pdf/2108.03332.pdf), BEHAVIOR includes a set of functional requirements needed to use its activities in a simulator. These are: 
1. Object-centric representation (object identities enriched with properties and states)
2. Simulation of physical forces and motion, generation of virtual sensor signals 
3. Simulation of additional, non-kinematic properties per object (following the specifications in `bddl/utils/synsets_to_filtered_properties_pruned_<your_simulator>.json`)
4. Functionality to generate valid instances in the simulator that satisfy the `:init` of a given activity definition
5. Functionality to check the current simulator state, with the goal of evaluating its progress against the `:goal` of the given activity definition

This page includes a detailed description of how these requirements relate to the BDDL code, as well as links to the iGibson 2.0 codebase where these requirements have been implemented. This implementation can be used as an example to guide implementation for using BEHAVIOR with your simulator of choice.

## Object-centric representation
This part of the simulator code is necessary for BEHAVIOR to function properly, but it doesn't interface directly with the BDDL codebase. For an example, look at [iGibson 2.0's object design](http://svl.stanford.edu/igibson/docs/objects.html).

## Simulation of physical forces and motion, simulation of additional non-kinematic properties 
Physical forces + motion and non-kinematic states may require very different implementations on the simulation side. For examples in iGibson, see:
- Physical forces and motion: [iGibson 2.0 documentation](http://svl.stanford.edu/igibson/docs/physics_engine.html)
- Non-kinematic states: [iGibson 2.0 documentation](TODO)

However, both of these requirements interface with BDDL code in the same way, and only minimally. BDDL includes several different object states as predicates as explained [here](TODO), some kinematic and some nonkinematic, all of different arities. The only requirement is that given some atomic formula `(predicate cat1_1 ... catN_n)`, such as `(cooked apple.n.01_1)` or `(ontop bowl.n.01_3 table.n.02_1)`, your simulator 1) can determine whether the atomic formula is satsified (for atomic formulae coming from the activity definition `:goal`) and 2) instantiate the objects so that it is satisfied (for atomic formulae coming from `:init`). 

## Functionality to generate valid instances 
This functionality must take a *compiled* `:init` condition and create a physical scene that satisfies it. This requires **sampling functionality** that can turn symbols in compiled BDDL into objects in the correct states, whether positional relationships or nonkinematic. For example, given compiled literals `(cooked apple.n.01_1) (inside apple.n.01_1 electric_refrigerator.n.01_1)`, the sampler needs to place an apple inside the fridge and set it as cooked. TODO iGibson examples

## Functionality to check the current simulator state 
This functionality must be able to check if compiled `:goal` conditions in BDDL are satisfied or not. This requires functionality that can take a compiled goal atomic formula and see if it is satisfied by the current physical state. For example, given a compiled atomic formula `(cooked apple.n.01_1)`, the checking functionality of the simulator must be able to find the object labeled `apple.n.01_1`, see if it is in the cooked state, and answer the BDDL code's query accordingly. 

Note that at both sampling and checking, the simulator will only encounter literals (atomic formulae or negated atomic formulae). In the case of sampling, the only negated atomic formulae will be those with unary predicates, i.e. those that deal with one object. For example, during sampling the simulator may see `(not (cooked apple.n.01_1))` but it will not see `(not (inside apple.n.01_1 electric_refrigerator.n.01_1))` (see [BDDL language rules](TODO) for a full explanation of the rules of BDDL). So, the simulator does not need to handle the logic side, e.g. breaking a complex expression into atomic formulae or generating solutions. It only needs to answer queries involving atomic formulae, i.e. facts about the physical state. 
