(define (problem putting_away_Halloween_decorations_0)
    (:domain igibson)

    (:objects
     	pumpkin.n.02_1 pumpkin.n.02_2 - pumpkin.n.02
    	floor.n.01_1 - floor.n.01
    	caldron.n.01_1 - caldron.n.01
    	sheet.n.03_1 - sheet.n.03
    	table.n.02_1 - table.n.02
    	candle.n.01_1 candle.n.01_2 candle.n.01_3 - candle.n.01
    	cabinet.n.01_1 - cabinet.n.01
    	sofa.n.01_1 - sofa.n.01
    	agent.n.01_1 - agent.n.01
    )
    
    (:init 
        (onfloor pumpkin.n.02_1 floor.n.01_1) 
        (onfloor pumpkin.n.02_2 floor.n.01_1) 
        (onfloor caldron.n.01_1 floor.n.01_1) 
        (ontop sheet.n.03_1 table.n.02_1) 
        (onfloor candle.n.01_1 floor.n.01_1) 
        (onfloor candle.n.01_2 floor.n.01_1) 
        (onfloor candle.n.01_3 floor.n.01_1) 
        (inroom floor.n.01_1 living_room) 
        (inroom cabinet.n.01_1 living_room) 
        (inroom table.n.02_1 living_room) 
        (inroom sofa.n.01_1 living_room) 
        (onfloor agent.n.01_1 floor.n.01_1)
    )
    
    (:goal 
        (and 
            (forall 
                (?pumpkin.n.02 - pumpkin.n.02) 
                (inside ?pumpkin.n.02 ?cabinet.n.01_1)
            ) 
            (forall 
                (?candle.n.01 - candle.n.01) 
                (inside ?candle.n.01 ?cabinet.n.01_1)
            ) 
            (or 
                (nextto ?sheet.n.03_1 ?table.n.02_1) 
                (ontop ?sheet.n.03_1 ?table.n.02_1)
            ) 
            (nextto ?caldron.n.01_1 ?table.n.02_1)
        )
    )
)