(define (problem organizing_file_cabinet_0)
    (:domain igibson)

    (:objects
        floor.n.01_1 - floor.n.01
        marker.n.03_1 - marker.n.03
        chair.n.01_1 - chair.n.01
        document.n.01_1 document.n.01_2 document.n.01_3 document.n.01_4 - document.n.01
        table.n.02_1 - table.n.02
        cabinet.n.01_1 - cabinet.n.01
        folder.n.02_1 folder.n.02_2 - folder.n.02
        agent.n.01_1 - agent.n.01
    )
    
    (:init 
        (ontop marker.n.03_1 chair.n.01_1) 
        (ontop document.n.01_1 table.n.02_1) 
        (inside document.n.01_2 cabinet.n.01_1) 
        (ontop document.n.01_3 table.n.02_1) 
        (inside document.n.01_4 cabinet.n.01_1) 
        (ontop folder.n.02_1 table.n.02_1) 
        (onfloor folder.n.02_2 floor.n.01_1) 
        (inroom cabinet.n.01_1 home_office) 
        (inroom table.n.02_1 home_office) 
        (inroom chair.n.01_1 home_office) 
        (inroom floor.n.01_1 home_office) 
        (onfloor agent.n.01_1 floor.n.01_1)
    )
    
    (:goal 
        (and 
            (ontop ?marker.n.03_1 ?table.n.02_1) 
            (forall 
                (?document.n.01 - document.n.01) 
                (inside ?document.n.01 ?cabinet.n.01_1)
            ) 
            (forall 
                (?folder.n.02 - folder.n.02) 
                (inside ?folder.n.02 ?cabinet.n.01_1)
            )
        )
    )
)