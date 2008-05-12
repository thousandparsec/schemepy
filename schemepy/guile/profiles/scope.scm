(define (make-scope base)
  (let ((m (make-module)))
    (module-define! m 'display display)
    (module-define! m 'newline newline)
    (module-use! m base)
    m))
