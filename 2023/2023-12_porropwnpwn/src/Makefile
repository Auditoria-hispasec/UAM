CC = gcc
CFLAGS = -Wall -Wextra -z relro -z lazy
CASMFLAGS = -fno-asynchronous-unwind-tables -fno-dwarf2-cfi-asm -maes -O0 -fno-stack-protector 

all: main

main: main.s aes.s
	$(CC) $(CFLAGS) -o main main.s aes.s
	strip -K flag1 -K flag2 -K uamkdf2 -K encrypt main
	base64 main > main.b64

main.s: main.c
	$(CC) $(CASMFLAGS) main.c -S -o main_tmp.s
	#cp main_tmp.s main.s
	python3 obfuscate.py main_tmp.s > main.s
	

aes.s: aes.c
	$(CC) $(CASMFLAGS) aes.c -S -o aes_tmp.s
	#cp aes_tmp.s aes.s
	python3 obfuscate.py aes_tmp.s > aes.s

clean:
	rm -f main *.o *.s main main.b64
