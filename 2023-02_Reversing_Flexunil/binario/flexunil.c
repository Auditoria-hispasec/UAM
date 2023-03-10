#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <sys/ptrace.h>

bool perturbate = false;

extern char _start, _etext;

const char flag1[] = "Flag 1: VUFNezU4NGUwNjZjY2I5Y2UwNTk4N2QwYmNlNmY3ZDNlMzIzfQ==";

void maxmix(const char *input, int input_len, char *output)
{
   int cc = 0;

   static char flag2[]="\xea\xa4\xd1\xbe\x9f\xfcJ\x91\xb1>\xa5L\xaeX\x11\xd8X\xc4\x07\xdf\x02\x01\x94\x0c\x90\xc2\xf8\x8c\xb4\x97\x0c\x05";

   for (char *ptr = &_start; ptr < &_etext; ptr++)
   {
      if (*ptr == '\xcc')
      {
         cc++;
      }
   }

   if (cc > 1)
   {
      perturbate = true;
   }

   for(int i = 0 ; i < input_len; i++)
   {
      output[i] = ((flag2[i] ^ (input[i] * 25)) + (perturbate ? 3*(i % 4 == 2) : 0)) & 0xff;
   }

   output[input_len] = '\0';
}

void hint()
{
   static char hint[] = "Gexpevz7xbcgbc7zbdc7ur75Vzvm~yp67Q{vp7~d7BVZlnxbe7~ygbcj57cx7dbttrrs";
   int hint_len = strlen(hint);

   for (int i = 0; i < hint_len; i++)
   {
      putchar(hint[i] ^ 0x17);
   }

   puts("");
}

int main(void)
{
   char hint_xor[4] = { 0x22, 0x26, 0x25, 0x31 };
   char input[52] = {0};
   char output[33] = {0};
   bool printable = true;

   if (ptrace(PTRACE_TRACEME, 0, 0, 0))
   {
      perturbate = true;
   }

   printf("Second flag is hidden somewhere. Please check your guess: ");
   if (!fgets(input, 51, stdin))
   {
      puts("fgets failed");
      return 1;
   }

   int input_length = strlen(input);
   if (input[input_length-1] == '\n')
   {
       input[input_length-1] = '\0';
       input_length--;
   }

   if ((input[0] ^ hint_xor[0]) == 'J'
        && (input[1] ^ hint_xor[1]) == 'O'
        && (input[2] ^ hint_xor[2]) == 'K'
        && (input[3] ^ hint_xor[3]) == 'E'
        && input[4] == '\0'
        && !perturbate)
   {
      hint();
      return 1;
   }

   if (input_length > 32)
   {
      puts("Too many characters");
      return 1;
   }

   maxmix(input, input_length, output);
#ifdef CHECK
   for (int i = 0; i < input_length; i++)
   {
      if (output[i] == '\\')
      {
         printf("\\\\");
      }
      else if (output[i] >= 32 && output[i] <= 126)
      {
         printf("%c", output[i]);
      }
      else
      {
         printf("\\x%02x", (unsigned char)output[i]);
      }
   }

   puts("");
#else
   for (int i = 0; i < input_length; i++)
   {
      if (output[i] < 32 || output[i] > 126)
      {
         printable = false;
         break;
      }
   }

   if (printable)
   {
      puts(output);
   }
   else
   {
      puts("I don't understand you");
   }
#endif
   return 0;
}
