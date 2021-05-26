(define (problem installing_a_printer_0)
    (:domain igibson)

    (:objects
     	printer.n.03_1 - printer.n.03
    	floor.n.01_1 - floor.n.01
    	table.n.02_1 - table.n.02
        agent.n.01_1 - agent.n.01
    )
    
    (:init 
        (onfloor printer.n.03_1 floor.n.01_1) 
        (not 
            (toggled_on printer.n.03_1)
        ) 
        (inroom table.n.02_1 home_office) 
        (inroom floor.n.01_1 home_office) 
        (onfloor agent.n.01_1 floor.n.01_1)
    )
    
    (:goal 
        (and 
            (ontop ?printer.n.03_1 ?table.n.02_1) 
            (toggled_on ?printer.n.03_1)
        )
    )
)