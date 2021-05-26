(define (problem putting_dishes_away_after_cleaning_0)
    (:domain igibson)

    (:objects
     	plate.n.04_1 plate.n.04_2 plate.n.04_3 plate.n.04_4 plate.n.04_5 plate.n.04_6 plate.n.04_7 plate.n.04_8 - plate.n.04
    	countertop.n.01_1 countertop.n.01_2 - countertop.n.01
    	cabinet.n.01_1 - cabinet.n.01
    	floor.n.01_1 - floor.n.01
    	agent.n.01_1 - agent.n.01
    )
    
    (:init 
        (ontop plate.n.04_1 countertop.n.01_1) 
        (ontop plate.n.04_2 countertop.n.01_1) 
        (ontop plate.n.04_3 countertop.n.01_1) 
        (ontop plate.n.04_4 countertop.n.01_1) 
        (ontop plate.n.04_5 countertop.n.01_2) 
        (ontop plate.n.04_6 countertop.n.01_2) 
        (ontop plate.n.04_7 countertop.n.01_2) 
        (ontop plate.n.04_8 countertop.n.01_2) 
        (inroom countertop.n.01_1 kitchen) 
        (inroom countertop.n.01_2 kitchen) 
        (inroom cabinet.n.01_1 kitchen) 
        (inroom floor.n.01_1 kitchen) 
        (onfloor agent.n.01_1 floor.n.01_1)
    )
    
    (:goal 
        (and 
            (exists 
                (?cabinet.n.01 - cabinet.n.01) 
                (forall 
                    (?plate.n.04 - plate.n.04) 
                    (inside ?plate.n.04 ?cabinet.n.01_1)
                )
            )
        )
    )
)