#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/sendfile.h>
#include <time.h>


void aes128_load_key(int8_t *enc_key);
void aes128_enc(int8_t *plainText,int8_t *cipherText);
void aes128_dec(int8_t *cipherText,int8_t *plainText);
size_t aes128_dec_ecb(int8_t *cipherText,int8_t *plainText,size_t size);
size_t aes128_enc_ecb(int8_t *plainText,int8_t *cipherText,size_t size);


int calc(int a, int b) {
    return a + b;
}

void setup() {
    // setup buffering for serving over the net
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    srand(time(NULL) + getpid());
}

void dump_hex(const uint8_t *data, size_t len) {
    for (int i = 0; i < len; i++) {
        printf("%02x", data[i]);
    }
    printf("\n");
}

void flag1() {
    unsigned int number;
    char msg[128];

    char buffer[256];
    uint8_t key[16];
    int fd;
    int i;
    size_t n;

    unsigned int guess;


    number = rand() | 0xfabada;
    printf("\n");
    printf("Vamos a jugar a un juego. He pensado un número entre 1 y 2^32\n");
    printf("Te puedo dar una pista. Los 3 últimos dígitos del número son: %03d\n", number % 1000);
    printf("Si lo aciertas, te doy la primer flag\n\n");
    
    printf("Dime un número: ");
    fflush(stdout);

    scanf("%u", &guess);
    if (guess == 1337) {
        for (i = 0; i < 16; i++) {
            key[i] = rand() % 256;
        }
        printf("Esta es la clave AES que voy a usar para descifrar tu mensaje: ");
        dump_hex(key, 16);

        printf("Envía tu mensaje cifrado:\n");
        n = read(0, buffer, 256);

        aes128_load_key(key);
        aes128_dec_ecb(buffer, msg, n); // Aquí está el bug. buffer son 256 bytes, pero msg solo 128. Subrescribe la variable "number", entre otras
        printf("Tu mensaje descifrado es:\n%s\n", msg);
    }

    if (guess == number) {
        printf("¡Has acertado! Aquí tienes tu flag:\n");
        fd = open("flag1.txt", 0);
        n = 1;
        while (n > 0) {
            n = read(fd, &msg, sizeof(msg));
            write(1, &msg, n);
        }
        fflush(stdout);
        printf("\n");

        close(fd);
    
    } else {
        printf("No has acertado. El número era %u\n", number);
    }

    exit(0);
}


// Deriva una passphrase en una clave aes.
void uamkdf2(const char *password, uint8_t *key) {
    char *xorkey = "Pues al final hubo reto de pwn y todo :)";

    memset(key, 0, 16);

    for (int i=0; i<strlen(password); i++) {
        key[i%16] ^= password[i];
    }
    for (int i=0; i<strlen(xorkey); i++) {
        key[i%16] ^= xorkey[i];
    }

    unsigned int seed = 0;

    for (int i=0; i<16; i++) {
        seed = (seed << 8) | (seed >> (sizeof(seed)*8 - 8)) ^ key[i];
    }
    srand(seed);

    for (int i=0; i<16; i++) {
        key[i] ^= rand() % 256;
    }
}

void gen_password(char *password, size_t length) {
    char charset[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    for (int i = 0; i < length-1; i++) {
        int index = rand() % strlen(charset);
        password[i] = charset[index];
    }
    password[length-1] = '\0';
}

void flag2() {
    char buffer[256];
    char password[64];
    uint8_t key[16];
    gen_password(password, 33);

    uamkdf2(password, key);
    aes128_load_key(key);

    printf("Esta es la password que tienes que usar: %s\n",password);
    printf("Dame el mensaje cifrado:\n");

    #pragma GCC diagnostic push
    #pragma GCC diagnostic ignored "-Wstringop-overflow"
    size_t n = read(0, buffer, 512);
    #pragma GCC diagnostic pop
    aes128_dec_ecb(buffer, buffer, n);
    printf("Tu mensaje descifrado es:\n%s\n", buffer);
    
    printf("La segunda flag está en el fichero flag2.txt");
    printf("\nSuerte!\n");
}

void encrypt() {
    char password[32];
    uint8_t key[16];
    struct {
        char buffer[128];
        void *pointer;
    } x;
    size_t n;

    x.pointer = &flag1; // Ayuda para leakear la dirección de flag1()
    memset(x.buffer, 0, 128);

    printf("Dame la contraseña de cifrado:\n");
    n = read(0, password, 32);
    password[n] = '\0';

    uamkdf2(password, key);
    printf("Esta es la clave AES que voy a utilizar para cifrar tu mensaje:\n");
    dump_hex(key, 16);
    
    printf("Envía tu mensaje:\n");
    n = read(0, &x, sizeof(x)); 
    aes128_load_key(key);
    n = aes128_enc_ecb(x.buffer, x.buffer, n);
    printf("Tu mensaje cifrado es:\n");
    dump_hex(x.buffer, n);
}


void menu() {
    printf("1. Flag 1\n");
    printf("2. Flag 2\n");
    printf("%%. Binario\r");
    printf("                 \n");
    printf("Elige una opción: ");
    fflush(stdout);

}

int main(void) {
    setup();

    while(1) {
        menu();
        char c;
        int ret = scanf("%c%*c", &c);
        if (ret != 1) {
            break;
        }

        if (c == '1') {
            flag1();
        } else if (c == '2') {
            flag2();
        } else if (c == '3') {
            encrypt();
        } else if (c == '%') {
            char buf[128];
            int fd = open("main.b64", 0);
            int n = 1;
            while (n > 0) {
                n = read(fd, &buf, sizeof(buf));
                write(1, &buf, n);
            }
        } else if (c == '\\') {
            char buf[128];
            int fd = open("hof.txt", 0);
            int n = 1;
            while (n > 0) {
                n = read(fd, &buf, sizeof(buf));
                write(1, &buf, n);
            }
        } else {
            break;
        }
    }

    printf("Bye!\n");
    return 0;
}


void help() {
    asm (
        ".intel_syntax noprefix\n"
        "push rax\n"
        "pop rax\n"
        "ret\n"
        "pop rdi\n"
        "ret\n"
        "pop rsi\n"
        "ret\n" 
    );
}
