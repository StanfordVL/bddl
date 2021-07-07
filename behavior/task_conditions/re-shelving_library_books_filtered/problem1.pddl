(define (problem re-shelving_library_books_1)
    (:domain igibson)

    (:objects
        book.n.02_1 book.n.02_2 - book.n.02
        shelf.n.01_1 shelf.n.01_2 - shelf.n.01
        table.n.02_1 - table.n.02
    )
    
    (:init 
        (ontop book.n.02_1 table.n.02_1)
        (under book.n.02_2 table.n.02_1)
        (inroom table.n.02_1 living_room)
        (inroom shelf.n.01_1 living_room)
        (inroom shelf.n.01_2 living_room)
    )
    
    (:goal 
        (and 
            (forall 
                (?book.n.02 - book.n.02)
                (exists 
                    (?shelf.n.01 - shelf.n.01)
                    (or
                        (inside ?book.n.02 ?shelf.n.01)
                        (ontop ?book.n.02 ?shelf.n.01)
                    )
                )
            )
        )
    )
)
