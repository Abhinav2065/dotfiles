#include <stdio.h>
#include <string.h>
#include <math.h>
#include <sys/time.h>

#define WIDTH 46
#define HEIGHT 22

int main(void) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    double t = (tv.tv_sec % 10000) + tv.tv_usec / 1000000.0;
    float A = (float)(t * 1.4);
    float B = (float)(t * 0.7);

    float z[WIDTH * HEIGHT];
    char b[WIDTH * HEIGHT];
    memset(b, ' ', sizeof(b));
    memset(z, 0, sizeof(z));

    const float two_pi = 6.2831853f;
    for (float j = 0.0f; j < two_pi; j += 0.07f) {
        float d = cosf(j), f = sinf(j);
        float h = d + 2.0f;
        for (float i = 0.0f; i < two_pi; i += 0.02f) {
            float c = sinf(i), l = cosf(i);
            float e = sinf(A), g = cosf(A);
            float m = cosf(B), n = sinf(B);
            float D = 1.0f / (c * h * e + f * g + 5.0f);
            float tr = c * h * g - f * e;
            int x = (int)((WIDTH / 2.0f) + 30.0f * D * (l * h * m - tr * n));
            int y = (int)((HEIGHT / 2.0f) + 15.0f * D * (l * h * n + tr * m));
            int o = x + WIDTH * y;
            int N = (int)(8.0f * ((f * e - c * d * g) * m - c * d * e - f * g - l * d * n));
            if (y >= 0 && y < HEIGHT && x >= 0 && x < WIDTH && D > z[o]) {
                z[o] = D;
                const char *lum = ".,-~:;=!*#$@";
                b[o] = lum[N > 0 ? (N < 11 ? N : 11) : 0];
            }
        }
    }

    char out_buf[(WIDTH + 1) * HEIGHT + 1];
    int idx = 0;
    for (int y = 0; y < HEIGHT; y++) {
        memcpy(&out_buf[idx], &b[y * WIDTH], WIDTH);
        idx += WIDTH;
        out_buf[idx++] = '\n';
    }
    out_buf[idx] = '\0';
    fwrite(out_buf, 1, idx, stdout);
    return 0;
}
