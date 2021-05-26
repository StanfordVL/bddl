(define (problem installing_a_fax_machine_0)
    (:domain igibson)

    (:objects
     	facsimile.n.02_1 - facsimile.n.02
    	floor.n.01_1 - floor.n.01
    	table.n.02_1 - table.n.02
    	agent.n.01_1 - agent.n.01
    )
    
    (:init 
        (onfloor facsimile.n.02_1 floor.n.01_1) 
        (not 
            (toggled_on facsimile.n.02_1)
        ) 
        (inroom table.n.02_1 home_office) 
        (inroom floor.n.01_1 home_office) 
        (onfloor agent.n.01_1 floor.n.01_1)
    )
    
    (:goal 
        (and 
            (ontop ?facsimile.n.02_1 ?table.n.02_1) 
            (toggled_on ?facsimile.n.02_1)
        )
    )
)