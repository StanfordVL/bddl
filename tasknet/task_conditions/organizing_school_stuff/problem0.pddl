(define (problem organizing_school_stuff_0)
    (:domain igibson)

    (:objects
     	highlighter.n.02_1 - highlighter.n.02
    	bed.n.01_1 - bed.n.01
    	pencil.n.01_1 - pencil.n.01
    	pen.n.01_1 - pen.n.01
    	floor.n.01_1 - floor.n.01
    	calculator.n.02_1 - calculator.n.02
    	book.n.02_1 - book.n.02
    	folder.n.02_1 - folder.n.02
        table.n.02_1 - table.n.02
    	backpack.n.01_1 - backpack.n.01
    	agent.n.01_1 - agent.n.01
    )
    
    (:init 
        (ontop highlighter.n.02_1 bed.n.01_1) 
        (ontop pencil.n.01_1 bed.n.01_1) 
        (onfloor pen.n.01_1 floor.n.01_1) 
        (onfloor calculator.n.02_1 floor.n.01_1) 
        (ontop book.n.02_1 bed.n.01_1) 
        (ontop folder.n.02_1 bed.n.01_1) 
        (onfloor backpack.n.01_1 floor.n.01_1) 
        (inroom floor.n.01_1 bedroom) 
        (inroom bed.n.01_1 bedroom) 
        (inroom table.n.02_1 bedroom) 
        (onfloor agent.n.01_1 floor.n.01_1)
    )
    
    (:goal 
        (and 
            (and 
                (nextto ?folder.n.02_1 ?book.n.02_1) 
                (nextto ?folder.n.02_1 ?backpack.n.01_1) 
                (nextto ?book.n.02_1 ?backpack.n.01_1)
            ) 
            (inside ?highlighter.n.02_1 ?backpack.n.01_1) 
            (inside ?pencil.n.01_1 ?backpack.n.01_1) 
            (inside ?pen.n.01_1 ?backpack.n.01_1) 
            (inside ?calculator.n.02_1 ?backpack.n.01_1) 
            (ontop ?backpack.n.01_1 ?bed.n.01_1)
        )
    )
)