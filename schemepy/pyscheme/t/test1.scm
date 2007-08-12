;; Defines a few list operations

(define (range n)
  (define (range-helper k)
    (if (< k 0) '()
	(append (range-helper (- k 1))
		(list k))))
  (range-helper (- n 1)))


(define (reverse L)
  (if (null? L) '()
      (append (reverse (cdr L)) 
	      (list (car L)))))


(define (length L)
  (define (iter L n)
    (if (null? L) n
	(iter (cdr L) (+ n 1))))
  (iter L 0))
