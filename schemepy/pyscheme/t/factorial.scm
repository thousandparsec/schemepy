(define (factorial x) 
  (if (= x 0) 
      1 
      (* x (factorial (- x 1)))))

(factorial 10)
(factorial 100)
(factorial 1000)
;;(display (factorial 10000))
;;(newline)
