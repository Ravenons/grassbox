
/*
exec-success will log only process which executed successfully
*/

proc:::exec-success
{
  printf("%d\nPROCESS\nCREATE\n%s\n%d\n\n", ppid, execname, pid);
}

/*

*/

syscall::open:entry, syscall::open_dprotected_np:entry, syscall::open_extended:entry, syscall::open_nocancel:entry, syscall::guarded_open_np:entry
{
	printf("%d\nFILE\nOPEN\n%s\n\n", pid, copyinstr(arg0));
}