_mzhelper.so: mzhelper.o Makefile
	$(CC) -shared -o _mzhelper.so -lmzscheme3m -ldl -lm mzhelper.o

mzhelper.o: mzhelper.c Makefile
	mzc --3m --cc  mzhelper.c

clean:
	rm *.o *.so
