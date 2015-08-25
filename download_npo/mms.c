#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <libmms/mmsh.h>


// fetch -qo- 'http://cgi.omroep.nl/cgi-bin/streams?/tv/nps/anderetijden/bb.20060318.asf' | grep mms:// | cut -d\" -f 2
int main (int argc, char *argv[]) {
	char *url = argv[1];
	int total;
	char *buf;
	FILE *fp;

	mmsh_t *mms = mmsh_connect(NULL, NULL, url, 128 * 1024);

	if (!mms) {
		printf("mmsh_connect failed\n");
		exit(1);
	}

	fp = fopen("out.mms", "w");
	while (1) {
		buf = malloc(8192);
		total = mmsh_read(NULL, mms, buf, 8192);
		if (total == 0) break;
		fwrite(buf, total, 1, fp);
		
		//printf("%d, %lu\n", total, strlen(buf));
		//printf("%s\n\n", buf);
		//fflush(stdout);
	}
	printf("\n");
	mmsh_close(mms);
	fclose(fp);

	exit(0);
}
