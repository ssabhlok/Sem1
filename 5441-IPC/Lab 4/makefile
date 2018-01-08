p1:
	nvcc -Wno-deprecated-gpu-targets -o lab4p1_serial sabhlok_shivani_serial-lab4p1.cu
	nvcc -Wno-deprecated-gpu-targets -o lab4p1_cuda sabhlok_shivani_lab4p1.cu
	nvcc  -Wno-deprecated-gpu-targets -lm bmpReader.o -o lab4p2_serial sabhlok_shivani_serial-lab4p2.cu
	nvcc  -Wno-deprecated-gpu-targets -lm bmpReader.o -o lab4p2_cuda sabhlok_shivani_lab4p2.cu
	
clean:
	rm lab4p1_serial
	rm lab4p1_cuda
	rm lab4p2_serial
	rm lab4p2_cuda