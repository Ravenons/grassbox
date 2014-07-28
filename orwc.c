#include <fcntl.h>
#include <sys/types.h>
#include <sys/uio.h>
#include <unistd.h>

int main() {

	int fd = open("orwc_test.txt", O_RDWR | O_APPEND);
	char buf[10] = "";
	read(fd, buf, 10);
	write(fd, buf, 10);
	close(fd);
}
