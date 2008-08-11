_mzhelper.so: mzhelper.o Makefile
	$(CC) -shared -o _mzhelper.so -lmzscheme3m -ldl -lm mzhelper.o

mzhelper.o: mzhelper.c Makefile base.c
	mzc --3m --cc  mzhelper.c

base.c:
	mzc --c-mods base.c ++lib scheme/base ++lib r5rs

clean:
	rm *.o *.so || true
