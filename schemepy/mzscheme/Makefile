_mzhelper.so: mzhelper.o Makefile
	$(CC) -shared -o _mzhelper.so -lmzscheme -ldl -lm -lmzgc mzhelper.o

mzhelper.o: mzhelper.c Makefile
	mzc --cc  mzhelper.c

clean:
	rm *.o *.so
