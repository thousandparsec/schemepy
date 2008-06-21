(define pi 3.141592653589)
(define e  2.718281828459)

(define (rad->deg rad)
  "Converts radians into degrees"
  (* (/ 180 pi)
     rad))
(define (deg-rad deg)
  "Converts degrees into radians"
  (* (/ pi 180)
     deg))

(define (logt a b)
  "inverse of the expt function, if y = logt(a, b) then a^y == b"
  (/ (log b)
     (log a)))

;; Misc
(define (=~ a b tol)
  "Approximate equal"
  (< (abs (- a b))
     tol))
