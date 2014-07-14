syscall::open:entry { printf("FILE\nOPEN\n%s", copyinstr(arg0)); }
