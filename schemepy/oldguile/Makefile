

_guilehelper.so: guilehelper.o
	cc -shared -o _guilehelper.so -lguile guilehelper.o

guilehelper.o: guilehelper.c
	cc -fPIC -c guilehelper.c -g3 -Wall

clean:
	rm *.o *.so
