(define (problem cleaning_cupboards_0)
    (:domain igibson)

    (:objects
     	cabinet1 cabinet2 cabinet3 cabinet4 - cabinet
    	towel1 towel2 - towel
    	atomizer1 atomizer2 - atomizer
    	counter1 - counter
    	soap1 soap2 - soap
    	sink1 - sink
    	scrub_brush1 scrub_brush2 - scrub_brush
    	bucket1 bucket2 - bucket
    	rag1 rag2 rag3 rag4 - rag
    	porcelain1 porcelain2 - porcelain
    	photograph1 photograph2 - photograph
    	console_table1 - console_table
    	towel_rack1 - towel_rack
    )

    (:init
        (dusty cabinet1)
        (dusty cabinet2)
        (inside towel1 cabinet1)
        (inside towel2 cabinet1)
        (not
            (scrubbed towel1)
        )
        (not
            (scrubbed towel2)
        )
        (ontop atomizer1 counter1)
        (nextto soap1 sink1)
        (ontop scrub_brush1 counter1)
        (under bucket1 sink1)
        (ontop rag1 sink1)
        (ontop rag2 sink1)
        (not
            (soaked rag1)
        )

        (not
            (soaked rag2)
        )
        (dusty cabinet3)
        (dusty cabinet4)
        (inside porcelain1 cabinet3)
        (inside porcelain2 cabinet3)
        (not
            (scrubbed porcelain1)
        )
        (not
            (scrubbed porcelain2)
        )
        (inside photograph1 cabinet3)
        (inside photograph2 cabinet3)
        (dusty photograph1)
        (dusty photograph2)
        (dusty console_table1)
        (ontop atomizer2 console_table1)
        (ontop scrub_brush2 console_table1)
        (under bucket2 console_table1)
        (inside soap2 cabinet4)
        (inside rag3 cabinet4)
        (inside rag4 cabinet4)
        (not
            (soaked rag3)
        )
        (not
            (soaked rag4)
        )
        (inroom console_table1 diningroom)
        (inroom counter1 bathroom)
        (inroom cabinet1 bathroom)
        (inroom cabinet2 bathroom)
        (inroom cabinet3 diningroom)
        (inroom cabinet4 diningroom)
        (inroom sink1 bathroom)
        (inroom towel_rack1 bathroom)
    )

    (:goal
        (and
            (forall
                (?cabinet - cabinet)
                (scrubbed ?cabinet)
            )
            (forall
                (?cabinet - cabinet)
                (not
                    (dusty ?cabinet)
                )
            )
            (forall
                (?rag - rag)
                (soaked ?rag)
            )
            (forall
                (?rag - rag)
                (or
                    (inside ?rag ?bucket1)
                    (inside ?rag ?bucket2)
                )
            )
            (forall
                (?towel - towel)
                (scrubbed ?towel)
            )
            (forn
                (2)
                (?towel - towel)
                (nextto ?towel ?towel_rack1) ; original: ontop, can only be sampled next to
            )
            (or
                (inside ?atomizer1 ?cabinet1)
                (inside ?atomizer1 ?cabinet2)
                (inside ?atomizer1 ?cabinet3)
                (inside ?atomizer1 ?cabinet4)
            )
            (or
                (inside ?soap1 ?cabinet1)
                (inside ?soap1 ?cabinet2)
                (inside ?soap1 ?cabinet3)
                (inside ?soap1 ?cabinet4)
            )
            (or
                (inside ?scrub_brush1 ?cabinet1)
                (inside ?scrub_brush1 ?cabinet2)
                (inside ?scrub_brush1 ?cabinet3)
                (inside ?scrub_brush1 ?cabinet4)
            )
            (or
                (inside ?bucket1 ?cabinet1)
                (inside ?bucket1 ?cabinet2)
                (inside ?bucket1 ?cabinet3)
                (inside ?bucket1 ?cabinet4)
            )
            (forall
                (?porcelain - porcelain)
                (scrubbed ?porcelain)
            )
            (or
                (inside ?porcelain1 ?cabinet1)
                (inside ?porcelain1 ?cabinet2)
                (inside ?porcelain1 ?cabinet3)
                (inside ?porcelain1 ?cabinet4)

            )
            (or
                (inside ?porcelain2 ?cabinet1)
                (inside ?porcelain2 ?cabinet2)
                (inside ?porcelain2 ?cabinet3)
                (inside ?porcelain2 ?cabinet4)
            )
            (forall
                (?photograph - photograph)
                (not
                    (dusty ?photograph)
                )
            )
            (forall
                (?photograph - photograph)
                (or
                    (inside ?photograph ?cabinet1)
                    (inside ?photograph ?cabinet2)
                    (inside ?photograph ?cabinet3)
                    (inside ?photograph ?cabinet4)
                )
            )
            (not
                (dusty ?console_table1)
            )
            (or
                (inside ?atomizer2 ?cabinet1)
                (inside ?atomizer2 ?cabinet2)
                (inside ?atomizer2 ?cabinet3)
                (inside ?atomizer2 ?cabinet4)
            )
            (or
                (inside ?scrub_brush2 ?cabinet1)
                (inside ?scrub_brush2 ?cabinet2)
                (inside ?scrub_brush2 ?cabinet3)
                (inside ?scrub_brush2 ?cabinet4)
            )
            (or
                (inside ?soap2 ?cabinet1)
                (inside ?soap2 ?cabinet2)
                (inside ?soap2 ?cabinet3)
                (inside ?soap2 ?cabinet4)
            )
            (or
                (inside ?bucket2 ?cabinet1)
                (inside ?bucket2 ?cabinet2)
                (inside ?bucket2 ?cabinet3)
                (inside ?bucket2 ?cabinet4)
            )

        )
    )
)
