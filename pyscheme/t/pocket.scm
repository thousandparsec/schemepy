;; The pocket function
(define (pocket n)
  (define (func . x)
    (if (null? x)
	n
	(pocket (car x))))
  func)
