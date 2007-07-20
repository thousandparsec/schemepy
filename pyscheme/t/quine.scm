;; A "quine", a self-documenting program.
;; Seth David Schoen sent me this code fragment.  Very cool!  *grin*

 ((lambda (x) (list x (list (quote quote) x))) 
  (quote (lambda (x) (list x (list (quote quote) x)))))