
(:goal 
    (and 
        (ontop ?jug1 ?counter1) 
        (and 
            (inside ?citrus1 ?fridge1) 
            (forall 
                (?herb - herb) 
                (inside ?herb ?fridge1)
            ) 
            (inside ?greens1 ?fridge1)
        ) 
        (forall 
            (?apple - apple) 
            (ontop ?apple ?table1)
        ) 
        (inside ?foil1 ?cabinet1) 
        (and 
            (ontop ?towel1 ?shelf1) 
            (ontop ?thermometer1 ?shelf1)
        ) 
        (forall 
            (?bag - bag) 
            (inside ?bag ?cabinet1)
        )
    )
)