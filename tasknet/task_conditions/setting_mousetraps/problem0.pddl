(define (problem setting_mousetraps_0)
    (:domain igibson)

    (:objects
     	mousetrap.n.01_1 mousetrap.n.01_2 mousetrap.n.01_3 mousetrap.n.01_4 - mousetrap.n.01
    	sink.n.01_1 - sink.n.01
    	floor.n.01_1 floor.n.01_2 - floor.n.01
    	toilet.n.02_1 - toilet.n.02
        bed.n.01_1 - bed.n.01
    	agent.n.01_1 - agent.n.01
    )
    
    (:init 
        (ontop mousetrap.n.01_1 bed.n.01_1) 
        (ontop mousetrap.n.01_2 bed.n.01_1) 
        (ontop mousetrap.n.01_3 bed.n.01_1) 
        (ontop mousetrap.n.01_4 bed.n.01_1) 
        (inroom floor.n.01_1 corridor) 
        (inroom toilet.n.02_1 bathroom) 
        (inroom sink.n.01_1 bathroom) 
        (inroom floor.n.01_2 bathroom) 
        (inroom bed.n.01_1 bedroom) 
        (onfloor agent.n.01_1 floor.n.01_2)
    )
    
    (:goal 
        (and 
            (onfloor ?mousetrap.n.01_1 ?floor.n.01_1) 
            (onfloor ?mousetrap.n.01_2 ?floor.n.01_1) 
            (nextto ?mousetrap.n.01_3 ?toilet.n.02_1) 
            (nextto ?mousetrap.n.01_4 ?toilet.n.02_1)
        )
    )
)