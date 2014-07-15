syscall::open:entry
{
	printf("FILE\nOPEN\n%s\n\n", copyinstr(arg0));
}