#include <stdio.h>
#include <string.h>
#include <math.h>
#include <sys/time.h>
#include <fcntl.h>
#include <unistd.h>

int main(void) {
    char status[32] = "Playing";
    int fd = open("/dev/shm/hyprlock_player_status", O_RDONLY);
    if (fd >= 0) {
        int n = read(fd, status, sizeof(status) - 1);
        if (n > 0) status[n] = '\0';
        close(fd);
    }

    // Zero-width space to avoid trimming
    putchar(0xE2); putchar(0x80); putchar(0x8B);

    if (strncmp(status, "Playing", 7) != 0) {
        if (strncmp(status, "Paused", 6) == 0) {
            printf("                           \n");
            printf("                           \n");
            printf("  ▂   ▂   ▂   ▂   ▂   ▂   ▂\n");
            printf("  - - - - - - - - - - - - -\n");
        } else {
            printf("                           \n");
            printf("                           \n");
            printf("                           \n");
            printf("  - - - - - - - - - - - - -\n");
        }
        return 0;
    }

    struct timeval tv;
    gettimeofday(&tv, NULL);
    double t = (tv.tv_sec % 10000) + tv.tv_usec / 1000000.0;

    const char *blocks[] = {" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"};
    const int num_bars = 14;
    const int rows = 4;

    float heights[14];
    for (int i = 0; i < num_bars; i++) {
        float speed = 4.0f + (float)i * 0.5f;
        float h = sinf((float)t * speed + (float)i * 0.8f) * 0.35f
                + sinf((float)t * (speed * 1.7f) - (float)i * 1.1f) * 0.25f
                + sinf((float)t * (speed * 0.5f) + (float)i * 0.4f) * 0.20f
                + 0.50f;
        if (h < 0.05f) h = 0.05f;
        if (h > 1.0f) h = 1.0f;
        heights[i] = h;
    }

    for (int r = rows - 1; r >= 0; r--) {
        for (int i = 0; i < num_bars; i++) {
            float level = heights[i] * (float)rows;
            if (level >= (float)(r + 1)) {
                printf("█");
            } else if (level > (float)r) {
                int frac = (int)((level - (float)r) * 8.0f);
                if (frac < 1) frac = 1;
                if (frac > 8) frac = 8;
                printf("%s", blocks[frac]);
            } else {
                printf(" ");
            }
            if (i < num_bars - 1) putchar(' ');
        }
        putchar('\n');
    }
    return 0;
}
