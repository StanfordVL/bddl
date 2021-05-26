(define (problem laying_wood_floors_0)
    (:domain igibson)

    (:objects
     	plywood.n.01_1 plywood.n.01_2 plywood.n.01_3 plywood.n.01_4 - plywood.n.01
    	floor.n.01_1 floor.n.01_2 - floor.n.01
    	hammer.n.02_1 - hammer.n.02
    	saw.n.02_1 - saw.n.02
    	agent.n.01_1 - agent.n.01
    )
    
    (:init 
        (onfloor plywood.n.01_1 floor.n.01_1) 
        (onfloor plywood.n.01_2 floor.n.01_1) 
        (onfloor plywood.n.01_3 floor.n.01_1) 
        (onfloor plywood.n.01_4 floor.n.01_1) 
        (onfloor hammer.n.02_1 floor.n.01_1) 
        (onfloor saw.n.02_1 floor.n.01_1) 
        (inroom floor.n.01_1 kitchen) 
        (inroom floor.n.01_2 living_room) 
        (onfloor agent.n.01_1 floor.n.01_1)
    )
    
    (:goal 
        (and 
            (forall 
                (?plywood.n.01 - plywood.n.01) 
                (onfloor ?plywood.n.01 ?floor.n.01_2)
            ) 
            (forall 
                (?plywood.n.01 - plywood.n.01) 
                (or 
                    (nextto ?plywood.n.01 ?plywood.n.01_1) 
                    (nextto ?plywood.n.01 ?plywood.n.01_2) 
                    (nextto ?plywood.n.01 ?plywood.n.01_3) 
                    (nextto ?plywood.n.01 ?plywood.n.01_4)
                )
            )
        )
    )
)