bool checkOverflow(unsigned short x, unsigned short y) {
  return (x + y < x);  // BAD: x and y are automatically promoted to int.
}

int
tls1_process_heartbeat(SSL *s)
    {
    unsigned char *p = &s->s3->rrec.data[0], *pl;
    unsigned short hbtype;
    unsigned int payload;
 
    /* ... */
 
    hbtype = *p++;
    n2s(p, payload);
    pl = p;
 
    /* ... */
 
    if (hbtype == TLS1_HB_REQUEST)
            {
            /* ... */
            memcpy(bp, pl, payload);  // BAD: overflow here
            /* ... */
            }
 
 
    /* ... */
 
    }
    
#define BUFFERSIZE (1024)
// BAD: using gets
void echo_bad() {
    char buffer[BUFFERSIZE];
    gets(buffer);
    printf("Input was: '%s'\n", buffer);
}


wchar_t* pSrc;
pSrc = (wchar_t*)"a";

void bad_server() {
  char* query = getenv("QUERY_STRING");
  puts("<p>Query results for ");
  // BAD: Printing out an HTTP parameter with no escaping
  puts(query);
  puts("\n<p>\n");
  puts(do_search(query));
}


void congratulateUser(const char *userName)
{
        char buffer[80];
        // BAD: this could overflow the buffer if the UserName is long
        sprintf(buffer, "Congratulations, %s!", userName);
        MessageBox(hWnd, buffer, "New Message", MB_OK);
}
