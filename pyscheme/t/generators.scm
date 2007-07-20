;; A small stress test that generates iterators.
(define (make-generator f)
  (let ((resumption-point 'uninitialized))
    (let ((return-to 'uninitialized))
      (let ((yield-hook (lambda (val)
			  (call/cc (lambda (r)
				     (set! resumption-point r)
				     (return-to val))))))
	(let ((start-up-generator 
	       (lambda ()
		 (f yield-hook)
		 ;; After the generator is done, just return the 'ok
		 ;; symbol.  We might want to change this to a user-defined
		 ;; sentinel character instead.
		 (set! resumption-point (lambda (hook) 'ok))
		 'ok)))
		   
	  
	  (lambda ()
	    (call/cc 
	     (lambda (r)
	       (set! return-to r)
	       (if (eq? resumption-point 'uninitialized)
		   (start-up-generator)
		   ;; otherwise, resume from resumption-point.
		   (resumption-point yield-hook))))))))))
    


(define test-yield
  (make-generator 
   (lambda (yield)
     (yield 1)
     (yield 2)
     (yield 3)
     )))


(define yield-ints
  (make-generator
   (lambda (yield)
     (define counter 0)
     (define (loop)
       (yield counter)
       (set! counter (+ counter 1))
       (loop))

     (loop))))



;; If we had define-syntax, it might be nice to say something like:
;;
; (define-syntax define-generator
;   (syntax-rules
;    ()
;    ((define-generator generator-name (lambda (yield) e1 e2 ...))
;     (define generator-name (make-generator (lambda (yield) e1 e2 ...))))))
