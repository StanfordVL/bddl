(define (problem installing_alarms_0)
    (:domain igibson)

    (:objects
     	alarm.n.02_1 alarm.n.02_2 - alarm.n.02
    	table.n.02_1 table.n.02_2 - table.n.02
    	floor.n.01_1 - floor.n.01
    	agent.n.01_1 - agent.n.01
    )
    
    (:init 
        (ontop alarm.n.02_1 table.n.02_2) 
        (ontop alarm.n.02_2 table.n.02_2) 
        (not 
            (toggled_on alarm.n.02_1)
        ) 
        (not 
            (toggled_on alarm.n.02_2)
        ) 
        (inroom table.n.02_1 dining_room) 
        (inroom table.n.02_2 living_room) 
        (inroom floor.n.01_1 living_room) 
        (onfloor agent.n.01_1 floor.n.01_1)
    )
    
    (:goal 
        (and 
            (forpairs 
                (?alarm.n.02 - alarm.n.02) 
                (?table.n.02 - table.n.02) 
                (ontop ?alarm.n.02 ?table.n.02)
            ) 
            (forall 
                (?alarm.n.02 - alarm.n.02) 
                (toggled_on ?alarm.n.02)
            )
        )
    )
)