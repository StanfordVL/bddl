(define (problem picking_up_take-out_food_0)
    (:domain igibson)

    (:objects
    	floor.n.01_1 - floor.n.01
    	carton.n.02_1 - carton.n.02
        table.n.02_1 - table.n.02
        sushi.n.01_1 - sushi.n.01
        hamburger.n.01_1 - hamburger.n.01
    	agent.n.01_1 - agent.n.01
    )
    
    (:init 
        (onfloor carton.n.02_1 floor.n.01_1) 
        (inside sushi.n.01_1 carton.n.02_1) 
        (inside hamburger.n.01_1 carton.n.02_1) 
        (inroom floor.n.01_1 living_room) 
        (inroom table.n.02_1 dining_room) 
        (onfloor agent.n.01_1 floor.n.01_1)
    )
    
    (:goal 
        (and 
            (forall 
                (?carton.n.02 - carton.n.02) 
                (ontop ?carton.n.02 ?table.n.02_1)
            ) 
            (inside ?sushi.n.01_1 ?carton.n.02_1) 
            (inside ?hamburger.n.01_1 ?carton.n.02_1)
        )
    )
)
