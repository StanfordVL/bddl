# Core BDDL API 

The BDDL API allows a user, likely a simulator, to use BDDL entirely functionally. The necessary steps are 1) creating a domain file for your simulator (the iGibson domain file, `domain_igibson.bddl`, is provided), 2) selecting an activity definition in BDDL, and 3) running the definition with the API. Existing activities are found in `bddl/bddl/activity_definitions`](https://github.com/StanfordVL/bddl/tree/functional_api/bddl/activity_definitions). Instructions for creating a domain file and for creating a custom activity if you so choose are found in the [Activity Definition section](TODO) of this documentation. 

## BDDL API functionality and example 
The BDDL API is purely functional, making it simple to use with a simulator. The steps are: 
1. Provide a backend (interface between BDDL and simulator)
2. Provide settings 
3. Parse conditions 
4. Map BDDL object symbols to simulator objects 
5. Compile the goal conditions so they can be evaluated by querying the simulator 
6. Check success at each simulator step! 
7. (Optional) Get ground solutions to the goal condition to compute the `Q` success metric 
8. (Optional) Get a natural language translation of any condition, possibly to show a human demonstrator or an agent that understands tasks with natural language

### 1. Provide a backend 
Next, provide a backend that will implement the object states that form predicates in BDDL, e.g. your simulator's implementation of `cooked` in `(cooked apple.n.01_1)`. 

The interface between BDDL and the backend is `backend.get_predicate_class(token)`, used [here](https://github.com/StanfordVL/bddl/blob/e0b44a18e4840bd163a1cbca9f9810c05ca79931/bddl/condition_evaluation.py#L486). `token` will be a predicate found in `domain_<simulator_name>.bddl`, such as `cooked` or `ontop`. `get_predicate_class(token)` must return your simulator's implementation of the object state that **corresponds to the token**, **will take the object that eventually needs to be evaluated** (e.g. the simulator object assigned to `apple.n.01_1` in the `(cooked apple.n.01_1)` example), and **returns a Boolean indicating whether the fact is true in the current simulator state**, e.g. whether `apple.n.01_1` is indeed `cooked`. See the documentation on object states and iGibson's BDDL backend [here](TODO), iGibson's backend implementation [here](https://github.com/StanfordVL/iGibson/blob/afe24c6aa95c8d4e74ce6d6b5eae2f479f2807ae/igibson/activity/bddl_backend.py), and iGibson's object state implementations [here](https://github.com/StanfordVL/iGibson/tree/master/igibson/object_states). 

In the code, you may want to simply import your backend.
```python
import my_bddl_backend 
```

### 2. Provide settings
Next, provide settings for the simulator, activity, and particular definition you are using. 

```python
behavior_activity = "packing_lunches"        # your activity of choice 
activity_definition = 0                      # such that bddl/activity_definitions/<behavior_activity>/
                                             #          problem<activity_definition>.bddl exists 
simulator_name = "igibson"                   # such that bddl/activity_definitions/domain_<simulator_name>.bddl exists
```

### 3. Parse conditions
Next, with these settings create a `Conditions` object (contains parsed domain and problem) and an unpopulated scope (a map from BDDL object instance/category labels to NoneTypes that will eventually be replaced by simulator objects).  

```python
conds = Conditions(behavior_activity, activity_definition, simulator_name)
unpopulated_scope = get_object_scope(conds)
```

### 4. Map BDDL object symbols to simulator objects
Now that we have an activity definition with some initial condition and a backend that can check object states (e.g. `(inside apple.n.01_1 cabinet.n.01_1) (not (cooked apple.n.01_1))`), you can create a simulator state that satisfies BDDL's symbolic initial state - in fact, you can create potentially infinite such simulator states. For the given example, this simulator state would have an apple object model assigned to label `apple.n.01_1` and a cabinet object model assigned to `cabinet.n.01_1`. Furthermore, the apple model would be placed at a specific position in the scene such that *at task start time*, if your simulator's "inside" state was given references to this apple simulator object and this cabinet simulator object, it would return `True`. If your simulator's "cooked" state was given references to this apple simulator object, it would return `False`. 

This simulator state that instantiates the activity can be determined however you choose - you can pick all object positions by hand, have scene-specific programmatic instantiation as in Habitat or AI2THOR, have programmatic instantiation with a discrete set of locations as in VirtualHome, etc. The most general way is scene-agnostic, potentially-infinite instantiation, as in iGibson 2.0. If using a different simulator, check out iGibson 2.0's scene instantiation functionality ([docs](TODO) [code](TODO)) for an example!

Furthermore, this mapping can be done online by running your instantiation code while setting up a BDDL activity, or offline by caching instantiations that can be loaded at any time. iGibson 2.0 provides hundreds of such instantiations for various combinations of BEHAVIOR activities and its many scenes, all generated from the same code. See examples at [TODO - ig_dataset link?](TODO). **Note that in the cached instantiation URDFs, each object has a field `object_scope=<BDDL object instance label>`, e.g. `object_scope=apple.n.01_1`.**

Implement functionality to perform this sampling and associate BDDL object instance labels like `apple.n.01_1` to their corresponding simulator objects. Then, populate the BDDL object scope so that instead of 
```python
{
    apple.n.01_1: None,
    apple.n.01_2: None,
    cabinet.n.01_1: None,
    ...
}
```
it looks like 
```
{
    apple.n.01_1: your_apple_simulator_object_X,
    apple.n.01_2: your_apple_simulator_object_Y,
    cabinet.n.01_1: your_cabinet_simulator_object_Z,
    ...
}
```
Because every simulator's method of instantiating and storing instantiations will vary in details such as filetypes, we leave this implementation to the user. In the script that uses BDDL, include your code with whatever name and signature you like, as long as it returns a populated scope. Here's a stub example of "compiling" initial conditions to be in a usable format (see next step for more details on "compilation") and populating your scope offline: 

```python
init = get_initial_conditions(conds, my_bddl_backend, unpopulated_scope)
populated_scope = my_instantiation_function(unpopulated_scope, online=False, cached_instantiation=my_cache_filename)
```
Note that you do **not** need to worry about assigning simulator objects to BDDL's object **category** labels such as `apple.n.01` (no underscore) (see [Activity Definition section](TODO) for explanation of object categories vs. instances if interested). Object category labels do not appear in the initial conditions; in goal conditions, where your populated scope and implemented simulator states will be used to check for success, BDDL will handle object category assignments for you. 

### 5. Compile the goal conditions
With a populated scope, you can use BDDL's API to *"compile"* the goal condition. As explained in the [Activity Definition section](TODO), the goal condition is a compositional logical expression. Here, "compiling" means turning the activity's logical expression into a tree of BDDL logical operator objects where all leaf nodes are [atomic formulae](https://en.wikipedia.org/wiki/Atomic_formula#:~:text=In%20mathematical%20logic%2C%20an%20atomic,formed%20formulas%20of%20the%20logic.) (and all non-leaves are not atomic formulae). Only atomic formulae, which are terms like `(cooked apple.n.01_1)` or `(inside apple.n.01_1 cabinet.n.01_1)`, query the simulator. 

You should add code to your BDDL usage as follows:
```python
goal = get_goal_conditions(conds, my_bddl_backend, populated_scope)
```

`get_goal_conditions` and its inputs are all you need to compile the goal expression and get it ready to evaluate any state of the simulator during this activity. Though it is not at all necessary for using BDDL, if you want to know more about the logic representation, see these [two](TODO - condition evaluation) [files](TODO - logic base). 

### 6. Check success at each simulator step 
You are now ready to check your agent's success, as well as a rough report of progress, at every step of your simulator! We have only ever observed BDDL taking negligible time relative to the simulator itself, so this should not significantly impact your simulation speed. That said, you can also save the simulator trajectory and run success checking offline ([example](TODO)). The code is as follows: 

```python
# This is your main simulator loop. This example shows an infinite loop for simplicity.
while True: 
    print(evaluate_goal_conditions(goal))
```

Full script: 
```python
import bddl 
from bddl.activity import *
import my_bddl_backend 

behavior_activity = "packing_lunches"        # your activity of choice 
activity_definition = 0                      # such that bddl/activity_definitions/<behavior_activity>/
                                             #          problem<activity_definition>.bddl exists 
simulator_name = "igibson"                   # such that bddl/activity_definitions/domain_<simulator_name>.bddl exists

conds = Conditions(behavior_activity, activity_definition, simulator_name)
unpopulated_scope = get_object_scope(conds)
init = get_initial_conditions(conds, my_bddl_backend, unpopulated_scope)
populated_scope = my_instantiation_function(unpopulated_scope, online=False, cached_instantiation=my_cache_filename)
goal = get_goal_conditions(conds, my_bddl_backend, populated_scope)

# This is your main simulator loop. This example shows an infinite loop for simplicity.
while True: 
    print(evaluate_goal_conditions(goal))
```

### 7. Get ground solutions to the goal 
`evaluate_goal_conditions` tells you whether the goal condition expression is satisfied by the current simulator state or not. The goal condition is typically one conjunction with multiple conjuncts, so `evaluate_goal_conditions` also tells you which conjuncts are satisfied, providing a more detailed picture of current progress. 

However, consider an activity like 
```
(:objects 
    apple.n.01_1 apple.n.01_2 apple.n.01_3 apple.n.01_4 apple.n.01_5 - apple.n.01
    table.n.02_1 - table.n.02
    ; ...other objects...
)

; ...some :init where apples are not on the table...

(:goal
    (and
        (forall 
            (?apple.n.01 - apple.n.01)
            (exists 
                (?table.n.02 - table.n.02)
                (ontop ?apple.n.01 ?table.n.02)
            )
        )
        (forall
            (?apple.n.01 - apple.n.01)
            (cooked ?apple.n.01)
        )
    )
)
```
Here, `evaluate_goal_conditions` will only tell you 1) whether the entire goal expression is satisfied or not, and 2) whether all the apples are on the table or not and whether all the apples are cooked or not. 2) is finer-grained than 1) but coarser grained than it could be - one, three, or four apples on the table all indicate meaningfully different amounts of progress on the task, yet they are indistinguishable from `evaluate_goal_conditions`. 

For a finer-grained picture of success that ultimately defines our success score `Q`, as well as for a variety of other functions including verifying feasibility of new definitions, we provide code to *solve* (not just evalute) BDDL goal expressions. The code is as follows:

```python
>>> from bddl.activity import *
>>> import my_bddl_backend
# ...get populated scope... 
>>> ground_goal = get_ground_goal_state_options(conds, my_bddl_backend, populated_scope)
>>> print(ground_goal)
[
    [            # first option, i.e. one solution such that if all literals (atomic formula or negated atomic formula) in it are true, then the goal expression will be satisfied 
        [...],   # first literal 
        [...],   # second iteral in this solution
        ...      # more literals in this solution
    ],
    ...          # more options if the goal expression can be satsified through more than one symbolic state 
]
```
**Example**
BDDL:
```
(:objects
    apple.n.01_1 apple.n.01_2 - apple.n.01
    banana.n.01_1 banana.n.01_2 - banana.n.01
    table.n.02_1 - table.n.02
)
; ...some :init...
(:goal
    (and
        (exists 
            (?apple.n.01 - apple.n.01)
            (ontop ?apple.n.01 table.n.02_1)
        )
        (exists 
            (?banana.n.01 - banana.n.01)
            (not
                (ontop ?banana.n.01 table.n.02_1)
            )
        )    
    )
)
```
output of `get_ground_goal_state_options(cond)` (list of lists pf compiled conditions):
```python 
# list of...
[
    # ...standalone solutions to the goal expression, which are lists of... 
    [
        # *compiled* atomic formulae and negated atomic formulae that have the following meaning:
        ["ontop", "apple.n.01_1", "table.n.02_1"],
        ["ontop", "banana.n.01_1", "table.n.02_1"]
    ]
    [
        ["ontop", "apple.n.01_2", "table.n.02_1"],
        ["ontop", "banana.n.01_1", "table.n.02_1"]
    ]
    [
        ["ontop", "apple.n.01_1", "table.n.02_1"],
        ["ontop", "banana.n.01_2", "table.n.02_1"]
    ]
    [
        ["ontop", "apple.n.01_2", "table.n.02_1"],
        ["ontop", "banana.n.01_2", "table.n.02_1"]
    ]
]
```

### 8. Get natural language translations 
Predicate logic lends itself easily to creating natural language. To get "natural"-sounding versions of BDDL initial and goal conditions, you can use `get_natural_initial_conditions(conds)` and `get_natural_goal_conditions(conds)`:
```python
>>> from bddl.activity import *
>>> natural_init = get_natural_initial_conditions(conds)
>>> natural_goal = get_natural_goal_conditions(conds)

# for goal condition
# (:goal
#     (and
#         (forall 
#             (?apple.n.01 - apple.n.01)
#             (exists 
#                 (?table.n.02 - table.n.02)
#                 (ontop ?apple.n.01 ?table.n.02)
#             )
#         )
#     )
# )
>>> print(natural_goal)
for every apple.n.01
    for at least one table.n.02
        the apple.n.01 is on top of the table.n.02
```
We plan to use more advanced linguistics methods to get even more natural sounding translations, so stay tuned! 
