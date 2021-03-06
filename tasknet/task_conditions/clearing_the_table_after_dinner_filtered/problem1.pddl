(define (problem clearing_the_table_after_dinner_1)
    (:domain igibson)

    (:objects
     	knife1 knife2 knife3 knife4 - knife
    	table1 - table
    	dish1 dish2 dish3 dish4 - dish
    	cup1 cup2 cup3 cup4 - cup
    	fork1 fork2 fork3 fork4 - fork
    	garbage1 - garbage
    	dishwasher1 - dishwasher
    	mustard1 - mustard
    	catsup1 - catsup
    	refrigerator1 - refrigerator
    	crumb1 crumb2 crumb3 crumb4 crumb5 crumb6 - crumb
    )

    (:init

        (ontop knife1 table1)
        (not
            (scrubbed knife1)
        )

        (ontop knife2 table1)
        (not
            (scrubbed knife2)
        )

        (ontop knife3 table1)
        (not
            (scrubbed knife3)
        )

        (ontop knife4 table1)
        (not
            (scrubbed knife4)
        )

        (ontop dish1 table1)
        (not
            (scrubbed dish1)
        )

        (ontop dish2 table1)
        (not
            (scrubbed dish2)
        )

        (ontop dish3 table1)
        (not
            (scrubbed dish3)
        )

        (ontop dish4 table1)
        (not
            (scrubbed dish4)
        )

        (ontop cup1 table1)
        (not
            (scrubbed cup1)
        )

        (ontop cup2 table1)
        (not
            (scrubbed cup2)
        )

        (ontop cup3 table1)
        (not
            (scrubbed cup3)
        )

        (ontop cup4 table1)
        (not
            (scrubbed cup4)
        )

        (ontop fork1 table1)
        (not
            (scrubbed fork1)
        )

        (ontop fork2 table1)
        (not
            (scrubbed fork2)
        )

        (ontop fork3 table1)
        (not
            (scrubbed fork3)
        )

        (ontop fork4 table1)
        (not
            (scrubbed fork4)
        )


        (nextto garbage1 dishwasher1)
        (ontop mustard1 table1)
        (ontop catsup1 table1)
        (nextto refrigerator1 dishwasher1)


        (ontop crumb6 table1)
        (ontop crumb5 table1)
        (ontop crumb4 table1)
        (ontop crumb3 table1)
        (ontop crumb2 table1)
        (ontop crumb1 table1)
        (open dishwasher1)

        (inroom dishwasher1 kitchen)
        (inroom table1 diningroom)
    )

    (:goal
        (and
            (forall
                (?knife - knife)
                (and
                    (inside ?knife ?dishwasher1)
                    (scrubbed ?knife)
                )
            )
            (forall
                (?dish - dish)
                (and
                    (inside ?dish ?dishwasher1)
                    (scrubbed ?dish) ;original knife
                )
            )
            (forall
                (?cup - cup)
                (and
                    (inside ?cup ?dishwasher1)
                    (scrubbed ?cup) ;original knife
                )
            )
            (forall
                (?fork - fork)
                (and
                    (inside ?fork ?dishwasher1)
                    (scrubbed ?fork) ;original knife
                )
            )
            (not
                (open ?dishwasher1)
            )
            (and
                (inside ?catsup1 ?refrigerator1)
                (inside ?mustard1 ?refrigerator1)
                (not
                    (open ?refrigerator1)
                )
            )
            (forall
                (?crumb - crumb)
                (inside ?crumb ?garbage1)
            )
            (scrubbed ?table1)
        )
    )
)
