(define (domain packlunch)
    (:requirements :strips)
    (:predicates 
        (chips ?ch - chip) 
        (fruit ?fr - fruit) 
        (container ?con - container) 
        (shelf ?sh - shelf) 
        (counter ?cou - counter)
        (inside ?obj1 ?obj2)
        (nextTo ?obj2 ?obj2)
    )
)