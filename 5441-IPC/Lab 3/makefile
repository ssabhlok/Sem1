p1:
	gcc -I . -c main.c
	gcc -fopenmp -I . -c Sabhlok_Shivani_Disposable.c
	gcc -fopenmp -I . -c Sabhlok_Shivani_Persistent.c
	gcc -fopenmp -O3 -lrt -o disposable Sabhlok_Shivani_Disposable.o main.o
	gcc -fopenmp -O3 -lrt -o persistent Sabhlok_Shivani_Persistent.o main.o
clean:
	rm disposable
	rm persistent