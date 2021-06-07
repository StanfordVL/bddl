(define (problem putting_away_Christmas_decorations_0)
    (:domain igibson)

    (:objects
     	wreath.n.01_1 wreath.n.01_2 - wreath.n.01
    	floor.n.01_1 - floor.n.01
    	bow.n.08_1 bow.n.08_2 bow.n.08_3 - bow.n.08
    	ribbon.n.01_1 ribbon.n.01_2 ribbon.n.01_3 - ribbon.n.01
    	cabinet.n.01_1 - cabinet.n.01
    	agent.n.01_1 - agent.n.01
    )
    
    (:init 
        (onfloor wreath.n.01_1 floor.n.01_1) 
        (onfloor wreath.n.01_2 floor.n.01_1) 
        (onfloor bow.n.08_1 floor.n.01_1) 
        (onfloor bow.n.08_2 floor.n.01_1) 
        (onfloor bow.n.08_3 floor.n.01_1) 
        (onfloor ribbon.n.01_1 floor.n.01_1) 
        (onfloor ribbon.n.01_2 floor.n.01_1) 
        (onfloor ribbon.n.01_3 floor.n.01_1) 
        (inroom floor.n.01_1 living_room) 
        (inroom cabinet.n.01_1 living_room) 
        (onfloor agent.n.01_1 floor.n.01_1)
    )
    
    (:goal 
        (and 
            (forall 
                (?wreath.n.01 - wreath.n.01) 
                (nextto ?wreath.n.01 ?cabinet.n.01_1)
            ) 
            (forall 
                (?bow.n.08 - bow.n.08) 
                (nextto ?bow.n.08 ?cabinet.n.01_1)
            ) 
            (forall 
                (?ribbon.n.01 - ribbon.n.01) 
                (inside ?ribbon.n.01 ?cabinet.n.01_1)
            )
        )
    )
)
