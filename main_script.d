
/*
exec-success will log only process which executed successfully
*/

proc:::exec-success
{
  printf("%d\nPROCESS\nCREATE\n%s\n%d\n\n", ppid, execname, pid);
}

/*
open functions
*/

syscall::open:entry,
syscall::open_dprotected_np:entry,
syscall::open_extended:entry,
syscall::open_nocancel:entry,
syscall::guarded_open_np:entry,
syscall::readlink:entry
{
  self->file_path = arg0
}

syscall::open:return,
syscall::open_dprotected_np:return,
syscall::open_extended:return,
syscall::open_nocancel:return,
syscall::guarded_open_np:return,
syscall::readlink:return
/self->file_path/
{
	printf("%d\nFILE\nOPEN\n%d\n%s\n\n", pid, arg0, copyinstr(self->file_path));
}

/*
read functions
*/

syscall::read:entry,
syscall::readv:entry,
syscall::pread:entry,
syscall::read_nocancel:entry,
syscall::readv_nocancel:entry,
syscall::pread_nocancel:entry
{
  printf("%d\nFILE\nREAD\n%d\n\n", pid, arg0);
}

/*
write functions
*/

syscall::write:entry,
syscall::writev:entry,
syscall::pwrite:entry,
syscall::write_nocancel:entry,
syscall::writev_nocancel:entry,
syscall::pwrite_nocancel:entry
{
  printf("%d\nFILE\nWRITE\n%d\n\n", pid, arg0);
}

/*
close functions
*/

syscall::close:entry,
syscall::close_nocancel:entry,
syscall::guarded_close_np:entry
{
  printf("%d\nFILE\nCLOSE\n%d\n\n", pid, arg0);
}