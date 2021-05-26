(define (problem installing_a_modem_0)
    (:domain igibson)

    (:objects
     	modem.n.01_1 - modem.n.01
    	table.n.02_1 - table.n.02
    	floor.n.01_1 - floor.n.01
    	agent.n.01_1 - agent.n.01
    )
    
    (:init 
        (not 
            (toggled_on modem.n.01_1)
        ) 
        (ontop modem.n.01_1 table.n.02_1) 
        (inroom table.n.02_1 home_office) 
        (inroom floor.n.01_1 home_office) 
        (onfloor agent.n.01_1 floor.n.01_1)
    )
    
    (:goal 
        (and 
            (toggled_on ?modem.n.01_1) 
            (under ?modem.n.01_1 ?table.n.02_1)
        )
    )
)