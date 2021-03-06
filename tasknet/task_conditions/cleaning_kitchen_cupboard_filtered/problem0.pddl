(define (problem cleaning_kitchen_cupboard_0)
    (:domain igibson)

    (:objects
     	cabinet1 - cabinet
    	counter1 - counter
    	fridge1 - fridge
    	pop1 pop2 pop3 pop4 - pop
    	condiment1 condiment2 - condiment
    	dish1 dish2 - dish
    	box1 - box
    	cup1 cup2 cup3 - cup
    	bowl1 - bowl
    	rag1 - rag
    	bucket1 - bucket
    	soap1 - soap
    	water1 - water
    )

    (:init
        (ontop cabinet1 counter1)
        (dusty cabinet1)
        (not
            (scrubbed cabinet1)
        )
        (open cabinet1)
        (nextto fridge1 counter1)
        (inside pop1 cabinet1)
        (under counter1 pop1)
        (inside pop2 cabinet1)
        (under counter1 pop2)
        (inside pop3 cabinet1)
        (under counter1 pop3)
        (inside pop4 cabinet1)
        (under counter1 pop4)
        (inside condiment1 cabinet1)
        (under counter1 condiment1)
        (inside condiment2 cabinet1)
        (under counter1 condiment2)
        (inside dish1 cabinet1)
        (under counter1 dish1)
        (inside dish2 cabinet1)
        (under counter1 dish2)
        (inside box1 cabinet1)
        (under counter1 box1)
        (inside cup1 cabinet1)
        (under counter1 cup1)
        (inside cup2 cabinet1)
        (under counter1 cup2)
        (inside cup3 cabinet1)
        (under counter1 cup3)
        (inside bowl1 cabinet1)
        (under counter1 bowl1)
        (ontop rag1 counter1)
        (not
            (soaked rag1)
        )
        (ontop bucket1 counter1)
        (inside soap1 bucket1)
        (under counter1 soap1)
        (inside water1 bucket1)
        (under counter1 water1)
        (inroom cabinet1 kitchen)
        (inroom counter1 kitchen)
        (inroom fridge1 kitchen)
    )

    (:goal
        (and
            (forall
                (?pop - pop)
                (inside ?pop ?fridge1)
            )
            (and
                (scrubbed ?cabinet1)
                (not
                    (dusty ?cabinet1)
                )
                (not
                    (open ?cabinet1)
                )
            )
            (forall
                (?condiment - condiment)
                (inside ?condiment ?box1)
            )
            (and
                (forall
                    (?cup - cup)
                    (inside ?cup ?cabinet1)
                )
                (forall
                    (?dish - dish)
                    (inside ?dish ?cabinet1)
                )
                (inside ?bowl1 ?cabinet1)
            )
            (and
                (ontop ?rag1 ?bucket1)
                (soaked ?rag1)
                (inside ?water1 ?bucket1)
                (inside ?soap1 ?bucket1)
            )
        )
    )
)
