#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "sha256.h"
#include "utils.h"
#include <iostream>
using namespace std;

#ifdef SHA256

const __constant__ u32 __align__(8) cons_K256[64]
    = {0x428a2f98UL, 0x71374491UL, 0xb5c0fbcfUL, 0xe9b5dba5UL, 0x3956c25bUL, 0x59f111f1UL,
       0x923f82a4UL, 0xab1c5ed5UL, 0xd807aa98UL, 0x12835b01UL, 0x243185beUL, 0x550c7dc3UL,
       0x72be5d74UL, 0x80deb1feUL, 0x9bdc06a7UL, 0xc19bf174UL, 0xe49b69c1UL, 0xefbe4786UL,
       0x0fc19dc6UL, 0x240ca1ccUL, 0x2de92c6fUL, 0x4a7484aaUL, 0x5cb0a9dcUL, 0x76f988daUL,
       0x983e5152UL, 0xa831c66dUL, 0xb00327c8UL, 0xbf597fc7UL, 0xc6e00bf3UL, 0xd5a79147UL,
       0x06ca6351UL, 0x14292967UL, 0x27b70a85UL, 0x2e1b2138UL, 0x4d2c6dfcUL, 0x53380d13UL,
       0x650a7354UL, 0x766a0abbUL, 0x81c2c92eUL, 0x92722c85UL, 0xa2bfe8a1UL, 0xa81a664bUL,
       0xc24b8b70UL, 0xc76c51a3UL, 0xd192e819UL, 0xd6990624UL, 0xf40e3585UL, 0x106aa070UL,
       0x19a4c116UL, 0x1e376c08UL, 0x2748774cUL, 0x34b0bcb5UL, 0x391c0cb3UL, 0x4ed8aa4aUL,
       0x5b9cca4fUL, 0x682e6ff3UL, 0x748f82eeUL, 0x78a5636fUL, 0x84c87814UL, 0x8cc70208UL,
       0x90befffaUL, 0xa4506cebUL, 0xbef9a3f7UL, 0xc67178f2UL}; // __align__

__device__ uint32_t dev_load_bigendian_32(const uint8_t* x) {
    return (uint32_t) (x[3]) | (((uint32_t) (x[2])) << 8) | (((uint32_t) (x[1])) << 16)
        | (((uint32_t) (x[0])) << 24);
} // dev_load_bigendian_32

__device__ uint64_t dev_load_bigendian_64(const uint8_t* x) {
    return (uint64_t) (x[7]) | (((uint64_t) (x[6])) << 8) | (((uint64_t) (x[5])) << 16)
        | (((uint64_t) (x[4])) << 24) | (((uint64_t) (x[3])) << 32) | (((uint64_t) (x[2])) << 40)
        | (((uint64_t) (x[1])) << 48) | (((uint64_t) (x[0])) << 56);
} // dev_load_bigendian_64

__device__ void dev_store_bigendian_32(uint8_t* x, uint64_t u) {
    x[3] = (uint8_t) u;
    u >>= 8;
    x[2] = (uint8_t) u;
    u >>= 8;
    x[1] = (uint8_t) u;
    u >>= 8;
    x[0] = (uint8_t) u;
} // dev_store_bigendian_32

__device__ void dev_store_bigendian_64(uint8_t* x, uint64_t u) {
    x[7] = (uint8_t) u;
    u >>= 8;
    x[6] = (uint8_t) u;
    u >>= 8;
    x[5] = (uint8_t) u;
    u >>= 8;
    x[4] = (uint8_t) u;
    u >>= 8;
    x[3] = (uint8_t) u;
    u >>= 8;
    x[2] = (uint8_t) u;
    u >>= 8;
    x[1] = (uint8_t) u;
    u >>= 8;
    x[0] = (uint8_t) u;
} // dev_store_bigendian_64

#ifdef USING_SHA256_PTX

#if USING_SHA256_PTX_MODE == 0 // sign & default

#define Ch(a, b, c)                                                                                \
    ({                                                                                             \
        u32 result;                                                                                \
        asm("lop3.b32 %0, %1, %2, %3, 0xCA;" : "=r"(result) : "r"(a), "r"(b), "r"(c));             \
        result;                                                                                    \
    })

#define Maj(a, b, c)                                                                               \
    ({                                                                                             \
        u32 result;                                                                                \
        asm("lop3.b32 %0, %1, %2, %3, 0xE8;" : "=r"(result) : "r"(a), "r"(b), "r"(c));             \
        result;                                                                                    \
    })

#define ROL(v, n)                                                                                  \
    ({                                                                                             \
        u32 result;                                                                                \
        asm("shf.l.clamp.b32 %0, %1, %1, %2;\n\t" : "=r"(result) : "r"(v), "r"(n));                \
        result;                                                                                    \
    })

#define Sigma0_32(x)                                                                               \
    ({                                                                                             \
        u32 t1 = 0, t2 = 0;                                                                        \
        asm("shf.l.clamp.b32 %0, %2, %2, 30;\n\t"                                                  \
            "shf.l.clamp.b32 %1, %2, %2, 19;\n\t"                                                  \
            "xor.b32 %0, %0, %1;\n\t"                                                              \
            "shf.l.clamp.b32 %1, %2, %2, 10;\n\t"                                                  \
            "xor.b32 %0, %0, %1;\n\t"                                                              \
            : "+r"(t1), "+r"(t2)                                                                   \
            : "r"(x));                                                                             \
        t1;                                                                                        \
    })

#define Sigma1_32(x)                                                                               \
    ({                                                                                             \
        u32 t1 = 0, t2 = 0;                                                                        \
        asm("shf.l.clamp.b32 %0, %2, %2, 26;\n\t"                                                  \
            "shf.l.clamp.b32 %1, %2, %2, 21;\n\t"                                                  \
            "xor.b32 %0, %0, %1;\n\t"                                                              \
            "shf.l.clamp.b32 %1, %2, %2, 7;\n\t"                                                   \
            "xor.b32 %0, %0, %1;\n\t"                                                              \
            : "+r"(t1), "+r"(t2)                                                                   \
            : "r"(x));                                                                             \
        t1;                                                                                        \
    })

#define sigma0_32(x)                                                                               \
    ({                                                                                             \
        u32 t1 = 0, t2 = 0;                                                                        \
        asm("shf.l.clamp.b32 %0, %2, %2, 25;\n\t"                                                  \
            "shf.l.clamp.b32 %1, %2, %2, 14;\n\t"                                                  \
            "xor.b32 %0, %0, %1;\n\t"                                                              \
            "shr.b32 %1, %2, 3;\n\t"                                                               \
            "xor.b32 %0, %0, %1;\n\t"                                                              \
            : "+r"(t1), "+r"(t2)                                                                   \
            : "r"(x));                                                                             \
        t1;                                                                                        \
    })

#define sigma1_32(x)                                                                               \
    ({                                                                                             \
        u32 t1 = 0, t2 = 0;                                                                        \
        asm("shf.l.clamp.b32 %0, %2, %2, 15;\n\t"                                                  \
            "shf.l.clamp.b32 %1, %2, %2, 13;\n\t"                                                  \
            "xor.b32 %0, %0, %1;\n\t"                                                              \
            "shr.b32 %1, %2, 10;\n\t"                                                              \
            "xor.b32 %0, %0, %1;\n\t"                                                              \
            : "+r"(t1), "+r"(t2)                                                                   \
            : "r"(x));                                                                             \
        t1;                                                                                        \
    })

// __device__ __forceinline__ u32 Sigma1_32_Ch(u32 e, u32 f, u32 g) {
//     u32 t1 = 0, t2 = 0;
//     asm("shf.l.clamp.b32 %1, %0, %0, 26;\n\t"
//         "shf.l.clamp.b32 %2, %0, %0, 21;\n\t"
//         "xor.b32 %1, %1, %2;\n\t"
//         "shf.l.clamp.b32 %2, %0, %0, 7;\n\t"
//         "xor.b32 %1, %1, %2;\n\t"
//         "lop3.b32 %0, %0, %3, %4, 0xCA;\n\t"
//         "add.u32 %0, %0, %1;\n\t"
//         : "+r"(e), "+r"(t1), "+r"(t2)
//         : "r"(f), "r"(g));
//     return e;
// }

// __device__ __forceinline__ u32 Sigma0_32_Maj(u32 a, u32 b, u32 c) {
//     u32 t1 = 0, t2 = 0;
//     asm("shf.l.clamp.b32 %1, %0, %0, 26;\n\t"
//         "shf.l.clamp.b32 %2, %0, %0, 21;\n\t"
//         "xor.b32 %1, %1, %2;\n\t"
//         "shf.l.clamp.b32 %2, %0, %0, 7;\n\t"
//         "xor.b32 %1, %1, %2;\n\t"
//         "lop3.b32 %0, %0, %3, %4, 0xE8;\n\t"
//         "add.u32 %0, %0, %1;\n\t"
//         : "+r"(a), "+r"(t1), "+r"(t2)
//         : "r"(b), "r"(c));
//     return a;
// }

#elif USING_SHA256_PTX_MODE == 1 // kg

#define Ch(x, y, z) ((z) ^ ((x) & ((y) ^ (z))))
#define Maj(x, y, z) (((y) & ((x) | (z))) | ((x) & (z)))
#define ROL(v, n) (((v) << (n)) | ((v) >> (32 - (n))))

#define Sigma0_32(x) (ROL((x), 30) ^ ROL((x), 19) ^ ROL((x), 10))
#define Sigma1_32(x) (ROL((x), 26) ^ ROL((x), 21) ^ ROL((x), 7))
#define sigma0_32(x) (ROL((x), 25) ^ ROL((x), 14) ^ ((x) >> 3))
#define sigma1_32(x) (ROL((x), 15) ^ ROL((x), 13) ^ ((x) >> 10))

#elif USING_SHA256_PTX_MODE == 2 // verify
#define Ch(a, b, c)                                                                                \
    ({                                                                                             \
        u32 result;                                                                                \
        asm("lop3.b32 %0, %1, %2, %3, 0xCA;" : "=r"(result) : "r"(a), "r"(b), "r"(c));             \
        result;                                                                                    \
    })

#define Maj(a, b, c)                                                                               \
    ({                                                                                             \
        u32 result;                                                                                \
        asm("lop3.b32 %0, %1, %2, %3, 0xE8;" : "=r"(result) : "r"(a), "r"(b), "r"(c));             \
        result;                                                                                    \
    })

#define ROL(v, n) (((v) << (n)) | ((v) >> (32 - (n))))

#define Sigma0_32(x) (ROL((x), 30) ^ ROL((x), 19) ^ ROL((x), 10))
#define Sigma1_32(x) (ROL((x), 26) ^ ROL((x), 21) ^ ROL((x), 7))
#define sigma0_32(x) (ROL((x), 25) ^ ROL((x), 14) ^ ((x) >> 3))
#define sigma1_32(x) (ROL((x), 15) ^ ROL((x), 13) ^ ((x) >> 10))

#endif

#else // ifdef USING_SHA256_PTX

#define Ch(x, y, z) ((z) ^ ((x) & ((y) ^ (z))))
#define Maj(x, y, z) (((y) & ((x) | (z))) | ((x) & (z)))
#define ROL(v, n) (((v) << (n)) | ((v) >> (32 - (n))))
#define Sigma0_32(x) (ROL((x), 30) ^ ROL((x), 19) ^ ROL((x), 10))
#define Sigma1_32(x) (ROL((x), 26) ^ ROL((x), 21) ^ ROL((x), 7))
#define sigma0_32(x) (ROL((x), 25) ^ ROL((x), 14) ^ ((x) >> 3))
#define sigma1_32(x) (ROL((x), 15) ^ ROL((x), 13) ^ ((x) >> 10))

#endif // ifdef USING_SHA256_PTX

#ifdef USING_SHA256_INTEGER
#define HOST_c2l(c, l) (l = __byte_perm(*(c++), 0, 0x0123))
#else // ifdef USING_SHA256_INTEGER
#define HOST_c2l(c, l)                                                                             \
    (l = (((unsigned long) (*((c)++))) << 24), l |= (((unsigned long) (*((c)++))) << 16),          \
     l |= (((unsigned long) (*((c)++))) << 8), l |= (((unsigned long) (*((c)++)))))
#endif // ifdef USING_SHA256_INTEGER

#ifdef FASTER

#define ROUND_00_15(i, a, b, c, d, e, f, g, h)                                                     \
    T1 += h + Sigma1_32(e) + Ch(e, f, g) + cons_K256[i];                                           \
    h = Sigma0_32(a) + Maj(a, b, c);                                                               \
    d += T1;                                                                                       \
    h += T1;

#ifdef USING_SHA256_X_UNROLL
// x unroll version
__device__ void dev_crypto_hashblocks_sha256(uint8_t* __restrict__ statebytes,
                                             const void* __restrict__ in, size_t inlen) {

    u32 state[8];
    u32 a, b, c, d, e, f, g, h, s0, s1, T1;
    u32 X0, X1, X2, X3;
    u32 X4, X5, X6, X7;
    u32 X8, X9, X10, X11;
    u32 X12, X13, X14, X15;
    u32 num = inlen / 64;

    for (int i = 0; i < 8; i++)
        state[i] = dev_load_bigendian_32(statebytes + 4 * i);

#ifdef USING_SHA256_INTEGER
    const u32* data = (const u32*) in;
#else  // ifdef USING_SHA256_INTEGER
    const u8* data = (const u8*) in;
#endif // ifdef USING_SHA256_INTEGER

    while (num--) {
        a = state[0];
        b = state[1];
        c = state[2];
        d = state[3];
        e = state[4];
        f = state[5];
        g = state[6];
        h = state[7];

        u32 l;

        (void) HOST_c2l(data, l);
        T1 = X0 = l;
        ROUND_00_15(0, a, b, c, d, e, f, g, h);
        (void) HOST_c2l(data, l);
        T1 = X1 = l;
        ROUND_00_15(1, h, a, b, c, d, e, f, g);
        (void) HOST_c2l(data, l);
        T1 = X2 = l;
        ROUND_00_15(2, g, h, a, b, c, d, e, f);
        (void) HOST_c2l(data, l);
        T1 = X3 = l;
        ROUND_00_15(3, f, g, h, a, b, c, d, e);
        (void) HOST_c2l(data, l);
        T1 = X4 = l;
        ROUND_00_15(4, e, f, g, h, a, b, c, d);
        (void) HOST_c2l(data, l);
        T1 = X5 = l;
        ROUND_00_15(5, d, e, f, g, h, a, b, c);
        (void) HOST_c2l(data, l);
        T1 = X6 = l;
        ROUND_00_15(6, c, d, e, f, g, h, a, b);
        (void) HOST_c2l(data, l);
        T1 = X7 = l;
        ROUND_00_15(7, b, c, d, e, f, g, h, a);
        (void) HOST_c2l(data, l);
        T1 = X8 = l;
        ROUND_00_15(8, a, b, c, d, e, f, g, h);
        (void) HOST_c2l(data, l);
        T1 = X9 = l;
        ROUND_00_15(9, h, a, b, c, d, e, f, g);
        (void) HOST_c2l(data, l);
        T1 = X10 = l;
        ROUND_00_15(10, g, h, a, b, c, d, e, f);
        (void) HOST_c2l(data, l);
        T1 = X11 = l;
        ROUND_00_15(11, f, g, h, a, b, c, d, e);
        (void) HOST_c2l(data, l);
        T1 = X12 = l;
        ROUND_00_15(12, e, f, g, h, a, b, c, d);
        (void) HOST_c2l(data, l);
        T1 = X13 = l;
        ROUND_00_15(13, d, e, f, g, h, a, b, c);
        (void) HOST_c2l(data, l);
        T1 = X14 = l;
        ROUND_00_15(14, c, d, e, f, g, h, a, b);
        (void) HOST_c2l(data, l);
        T1 = X15 = l;
        ROUND_00_15(15, b, c, d, e, f, g, h, a);

        // #pragma unroll
        for (int i = 16; i < 64; i += 16) {
            s0 = sigma0_32(X1);
            s1 = sigma1_32(X14);
            T1 = X0 += s0 + s1 + X9;
            ROUND_00_15(i + 0, a, b, c, d, e, f, g, h);

            s0 = sigma0_32(X2);
            s1 = sigma1_32(X15);
            T1 = X1 += s0 + s1 + X10;
            ROUND_00_15(i + 1, h, a, b, c, d, e, f, g);

            s0 = sigma0_32(X3);
            s1 = sigma1_32(X0);
            T1 = X2 += s0 + s1 + X11;
            ROUND_00_15(i + 2, g, h, a, b, c, d, e, f);

            s0 = sigma0_32(X4);
            s1 = sigma1_32(X1);
            T1 = X3 += s0 + s1 + X12;
            ROUND_00_15(i + 3, f, g, h, a, b, c, d, e);

            s0 = sigma0_32(X5);
            s1 = sigma1_32(X2);
            T1 = X4 += s0 + s1 + X13;
            ROUND_00_15(i + 4, e, f, g, h, a, b, c, d);

            s0 = sigma0_32(X6);
            s1 = sigma1_32(X3);
            T1 = X5 += s0 + s1 + X14;
            ROUND_00_15(i + 5, d, e, f, g, h, a, b, c);

            s0 = sigma0_32(X7);
            s1 = sigma1_32(X4);
            T1 = X6 += s0 + s1 + X15;
            ROUND_00_15(i + 6, c, d, e, f, g, h, a, b);

            s0 = sigma0_32(X8);
            s1 = sigma1_32(X5);
            T1 = X7 += s0 + s1 + X0;
            ROUND_00_15(i + 7, b, c, d, e, f, g, h, a);

            // 8 - 16
            s0 = sigma0_32(X9);
            s1 = sigma1_32(X6);
            T1 = X8 += s0 + s1 + X1;
            ROUND_00_15(i + 8, a, b, c, d, e, f, g, h);

            s0 = sigma0_32(X10);
            s1 = sigma1_32(X7);
            T1 = X9 += s0 + s1 + X2;
            ROUND_00_15(i + 9, h, a, b, c, d, e, f, g);

            s0 = sigma0_32(X11);
            s1 = sigma1_32(X8);
            T1 = X10 += s0 + s1 + X3;
            ROUND_00_15(i + 10, g, h, a, b, c, d, e, f);

            s0 = sigma0_32(X12);
            s1 = sigma1_32(X9);
            T1 = X11 += s0 + s1 + X4;
            ROUND_00_15(i + 11, f, g, h, a, b, c, d, e);

            s0 = sigma0_32(X13);
            s1 = sigma1_32(X10);
            T1 = X12 += s0 + s1 + X5;
            ROUND_00_15(i + 12, e, f, g, h, a, b, c, d);

            s0 = sigma0_32(X14);
            s1 = sigma1_32(X11);
            T1 = X13 += s0 + s1 + X6;
            ROUND_00_15(i + 13, d, e, f, g, h, a, b, c);

            s0 = sigma0_32(X15);
            s1 = sigma1_32(X12);
            T1 = X14 += s0 + s1 + X7;
            ROUND_00_15(i + 14, c, d, e, f, g, h, a, b);

            s0 = sigma0_32(X0);
            s1 = sigma1_32(X13);
            T1 = X15 += s0 + s1 + X8;
            ROUND_00_15(i + 15, b, c, d, e, f, g, h, a);
        }

        state[0] += a;
        state[1] += b;
        state[2] += c;
        state[3] += d;
        state[4] += e;
        state[5] += f;
        state[6] += g;
        state[7] += h;
    }

    for (int i = 0; i < 8; i++)
        dev_store_bigendian_32(statebytes + 4 * i, state[i]);
}
#else // ifdef USING_SHA256_X_UNROLL

#define ROUND_16_63(i, a, b, c, d, e, f, g, h, X)                                                  \
    do {                                                                                           \
        s0 = X[(i + 1) & 0x0f];                                                                    \
        s0 = sigma0_32(s0);                                                                        \
        s1 = X[(i + 14) & 0x0f];                                                                   \
        s1 = sigma1_32(s1);                                                                        \
        T1 = X[(i) & 0x0f] += s0 + s1 + X[(i + 9) & 0x0f];                                         \
        ROUND_00_15(i, a, b, c, d, e, f, g, h);                                                    \
    } while (0)

__device__ void dev_crypto_hashblocks_sha256(uint8_t* statebytes, const void* in, size_t inlen) {
    u32 state[8];
    u32 a, b, c, d, e, f, g, h, s0, s1, T1;
    u32 X[16];
    u32 i;
    u32 num = inlen / 64;

    for (i = 0; i < 8; i++)
        state[i] = dev_load_bigendian_32(statebytes + 4 * i);

#ifdef USING_SHA256_INTEGER
    const u32* data = (const u32*) in;
#else  // ifdef USING_SHA256_INTEGER
    const u8* data = (const u8*) in;
#endif // ifdef USING_SHA256_INTEGER

    while (num--) {
        a = state[0];
        b = state[1];
        c = state[2];
        d = state[3];
        e = state[4];
        f = state[5];
        g = state[6];
        h = state[7];

        u32 l;

        (void) HOST_c2l(data, l);
        T1 = X[0] = l;
        ROUND_00_15(0, a, b, c, d, e, f, g, h);
        (void) HOST_c2l(data, l);
        T1 = X[1] = l;
        ROUND_00_15(1, h, a, b, c, d, e, f, g);
        (void) HOST_c2l(data, l);
        T1 = X[2] = l;
        ROUND_00_15(2, g, h, a, b, c, d, e, f);
        (void) HOST_c2l(data, l);
        T1 = X[3] = l;
        ROUND_00_15(3, f, g, h, a, b, c, d, e);
        (void) HOST_c2l(data, l);
        T1 = X[4] = l;
        ROUND_00_15(4, e, f, g, h, a, b, c, d);
        (void) HOST_c2l(data, l);
        T1 = X[5] = l;
        ROUND_00_15(5, d, e, f, g, h, a, b, c);
        (void) HOST_c2l(data, l);
        T1 = X[6] = l;
        ROUND_00_15(6, c, d, e, f, g, h, a, b);
        (void) HOST_c2l(data, l);
        T1 = X[7] = l;
        ROUND_00_15(7, b, c, d, e, f, g, h, a);
        (void) HOST_c2l(data, l);
        T1 = X[8] = l;
        ROUND_00_15(8, a, b, c, d, e, f, g, h);
        (void) HOST_c2l(data, l);
        T1 = X[9] = l;
        ROUND_00_15(9, h, a, b, c, d, e, f, g);
        (void) HOST_c2l(data, l);
        T1 = X[10] = l;
        ROUND_00_15(10, g, h, a, b, c, d, e, f);
        (void) HOST_c2l(data, l);
        T1 = X[11] = l;
        ROUND_00_15(11, f, g, h, a, b, c, d, e);
        (void) HOST_c2l(data, l);
        T1 = X[12] = l;
        ROUND_00_15(12, e, f, g, h, a, b, c, d);
        (void) HOST_c2l(data, l);
        T1 = X[13] = l;
        ROUND_00_15(13, d, e, f, g, h, a, b, c);
        (void) HOST_c2l(data, l);
        T1 = X[14] = l;
        ROUND_00_15(14, c, d, e, f, g, h, a, b);
        (void) HOST_c2l(data, l);
        T1 = X[15] = l;
        ROUND_00_15(15, b, c, d, e, f, g, h, a);

#pragma unroll 6
        for (i = 16; i < 64; i += 8) {
            ROUND_16_63(i + 0, a, b, c, d, e, f, g, h, X);
            ROUND_16_63(i + 1, h, a, b, c, d, e, f, g, X);
            ROUND_16_63(i + 2, g, h, a, b, c, d, e, f, X);
            ROUND_16_63(i + 3, f, g, h, a, b, c, d, e, X);
            ROUND_16_63(i + 4, e, f, g, h, a, b, c, d, X);
            ROUND_16_63(i + 5, d, e, f, g, h, a, b, c, X);
            ROUND_16_63(i + 6, c, d, e, f, g, h, a, b, X);
            ROUND_16_63(i + 7, b, c, d, e, f, g, h, a, X);
        }

        state[0] += a;
        state[1] += b;
        state[2] += c;
        state[3] += d;
        state[4] += e;
        state[5] += f;
        state[6] += g;
        state[7] += h;
    }

    for (i = 0; i < 8; i++)
        dev_store_bigendian_32(statebytes + 4 * i, state[i]);

} // sha256_block_data_order
#endif // ifdef USING_SHA256_X_UNROLL

#else // ifdef FASTER

__device__ void dev_crypto_hashblocks_sha256(uint8_t* statebytes, const void* in, size_t inlen) {
    u32 state[8];
    u32 a, b, c, d, e, f, g, h, s0, s1, T1, T2;
    u32 X[16], l;
    u32 i;
    u32 num = inlen / 64;

    for (i = 0; i < 8; i++)
        state[i] = dev_load_bigendian_32(statebytes + 4 * i);

#ifdef USING_SHA256_INTEGER
    const u32* data = (const u32*) in;
#else  // ifdef USING_SHA256_INTEGER
    const u8* data = (const u8*) in;
#endif // ifdef USING_SHA256_INTEGER

    while (num--) {
        a = state[0];
        b = state[1];
        c = state[2];
        d = state[3];
        e = state[4];
        f = state[5];
        g = state[6];
        h = state[7];

#ifdef USING_SHA256_UNROLL
#pragma unroll
#endif // ifdef USING_SHA256_UNROLL
        for (i = 0; i < 16; i++) {
            (void) HOST_c2l(data, l);
            T1 = X[i] = l;
            T1 += h + Sigma1_32(e) + Ch(e, f, g) + cons_K256[i];
            T2 = Sigma0_32(a) + Maj(a, b, c);
            h = g;
            g = f;
            f = e;
            e = d + T1;
            d = c;
            c = b;
            b = a;
            a = T1 + T2;
        }

#ifdef USING_SHA256_UNROLL
#pragma unroll
#endif // ifdef USING_SHA256_UNROLL
        for (i = 16; i < 64; i++) {
            s0 = X[(i + 1) & 0x0f];
            s0 = sigma0_32(s0);
            s1 = X[(i + 14) & 0x0f];
            s1 = sigma1_32(s1);

            T1 = X[i & 0xf] += s0 + s1 + X[(i + 9) & 0xf];
            T1 += h + Sigma1_32(e) + Ch(e, f, g) + cons_K256[i];
            T2 = Sigma0_32(a) + Maj(a, b, c);
            h = g;
            g = f;
            f = e;
            e = d + T1;
            d = c;
            c = b;
            b = a;
            a = T1 + T2;
        }

        state[0] += a;
        state[1] += b;
        state[2] += c;
        state[3] += d;
        state[4] += e;
        state[5] += f;
        state[6] += g;
        state[7] += h;
    }

    for (i = 0; i < 8; i++)
        dev_store_bigendian_32(statebytes + 4 * i, state[i]);
} // dev_crypto_hashblocks_sha256

#endif // ifdef FASTER

__device__ void dev_sha256_inc_init(uint8_t* state) {
    u8 iv[40] = {0x6a, 0x09, 0xe6, 0x67, 0xbb, 0x67, 0xae, 0x85, 0x3c, 0x6e, 0xf3, 0x72, 0xa5, 0x4f,
                 0xf5, 0x3a, 0x51, 0x0e, 0x52, 0x7f, 0x9b, 0x05, 0x68, 0x8c, 0x1f, 0x83, 0xd9, 0xab,
                 0x5b, 0xe0, 0xcd, 0x19, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

    memcpy(state, iv, 40);
} // dev_sha256_inc_init

__device__ void dev_sha256_inc_blocks(uint8_t* state, const void* in, size_t inblocks) {
    if (inblocks == 0) return;

    uint64_t bytes = dev_load_bigendian_64(state + 32);

    dev_crypto_hashblocks_sha256(state, in, 64 * inblocks);
    bytes += 64 * inblocks;

    dev_store_bigendian_64(state + 32, bytes);
} // dev_sha256_inc_blocks

__device__ void dev_sha256_inc_finalize(uint8_t* out, uint8_t* state, void* in_, size_t inlen) {
    // u8 padded[128];
    uint32_t padded_[32];
    u8* padded = (u8*) padded_;

    memset(padded, 0, 128);
    uint64_t bytes = dev_load_bigendian_64(state + 32) + inlen;

    u8* in = (u8*) in_;

    dev_crypto_hashblocks_sha256(state, in, inlen);

    in += inlen;
    inlen &= 63;
    in -= inlen;

    if (inlen != 0) memcpy(padded, in, inlen);

    padded[inlen] = 0x80;

    u32 bytes_arr[8] = {53, 45, 37, 29, 21, 13, 5, 3};

    if (inlen < 56) {
        memset(padded + inlen + 1, 0, 56 - inlen - 1);
        // padded[63] = (uint8_t)(bytes << 3);
        // padded[56] = (uint8_t)(bytes >> 53);
        // padded[57] = (uint8_t)(bytes >> 45);
        // padded[58] = (uint8_t)(bytes >> 37);
        // padded[59] = (uint8_t)(bytes >> 29);
        // padded[60] = (uint8_t)(bytes >> 21);
        // padded[61] = (uint8_t)(bytes >> 13);
        // padded[62] = (uint8_t)(bytes >> 5);
        // padded[63] = (uint8_t)(bytes << 3);
        for (size_t i = 0; i < 7; i++)
            padded[i + 56] = (uint8_t) (bytes >> bytes_arr[i]);
        padded[63] = (uint8_t) (bytes << 3);

        dev_crypto_hashblocks_sha256(state, (void*) padded, 64);
    } else {
        memset(in + inlen + 1, 0, 120 - inlen - 1);
        padded[120] = (uint8_t) (bytes >> 53);
        padded[121] = (uint8_t) (bytes >> 45);
        padded[122] = (uint8_t) (bytes >> 37);
        padded[123] = (uint8_t) (bytes >> 29);
        padded[124] = (uint8_t) (bytes >> 21);
        padded[125] = (uint8_t) (bytes >> 13);
        padded[126] = (uint8_t) (bytes >> 5);
        padded[127] = (uint8_t) (bytes << 3);
        // for (size_t i = 0; i < 8; i++)
        // 	padded[i + 120] = (uint8_t)(bytes >> bytes_arr[i]);
        dev_crypto_hashblocks_sha256(state, (void*) padded, 128);
    }
    memcpy(out, state, 32);
}

__device__ void dev_sha256(uint8_t* out, uint8_t* in, size_t inlen) {
    uint8_t state[40];
    static u8 m[32];

    // if (out == NULL) out = m;

    dev_sha256_inc_init(state);
    dev_sha256_inc_finalize(out, state, in, inlen);
}

__global__ void global_sha256(uint8_t* out, uint8_t* in, size_t inlen, size_t loop_num) {
    for (int i = 0; i < loop_num; i++)
        dev_sha256(out, in, inlen);
} // global_sha256

void face_sha256(uint8_t* md, uint8_t* d, size_t n, size_t loop_num) {
    struct timespec start, stop;
    CHECK(cudaSetDevice(DEVICE_USED));
    u8 *dev_d = NULL, *dev_md = NULL;

    CHECK(cudaMalloc((void**) &dev_d, n * sizeof(u8)));
    CHECK(cudaMalloc((void**) &dev_md, 32 * sizeof(u8)));
    CHECK(cudaMemcpy(dev_d, d, n * sizeof(u8), HOST_2_DEVICE));

    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &start);

    CHECK(cudaDeviceSynchronize());
    global_sha256<<<1, 1>>>(dev_md, dev_d, n, loop_num);
    CHECK(cudaGetLastError());
    CHECK(cudaDeviceSynchronize());
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &stop);

    g_result = (stop.tv_sec - start.tv_sec) * 1e6 + (stop.tv_nsec - start.tv_nsec) / 1e3;

    CHECK(cudaMemcpy(md, dev_md, 32 * sizeof(u8), DEVICE_2_HOST));

    cudaFree(dev_d);
    cudaFree(dev_md);
}

__global__ void global_dp_sha256(uint8_t* out, const uint8_t* in, size_t inlen, size_t total_msg_num) {
    size_t tid = blockDim.x * blockIdx.x + threadIdx.x;
    if (tid >= total_msg_num) return;

    // Calculate offset for this thread's input and output
    uint8_t* my_out = out + tid * 32;  // Each hash output is 32 bytes
    const uint8_t* my_in = in + tid * inlen;
    
    dev_sha256(my_out, (uint8_t*)my_in, inlen);
}

void face_dp_sha256(const uint8_t* in, uint8_t* out, size_t msg_size,
                    size_t total_msg_num, size_t grid_size, size_t block_size) {
    struct timespec start, stop;
    CHECK(cudaSetDevice(DEVICE_USED));
    
    uint8_t *dev_in = NULL, *dev_out = NULL;
    size_t total_in_size = msg_size * total_msg_num;
    size_t total_out_size = 32 * total_msg_num;  // 32 bytes per SHA256 hash

    // Allocate device memory
    CHECK(cudaMalloc((void**)&dev_in, total_in_size));
    CHECK(cudaMalloc((void**)&dev_out, total_out_size));

    // Copy input data to device
    CHECK(cudaMemcpy(dev_in, in, total_in_size, HOST_2_DEVICE));

    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &start);

    // Launch kernel with specified grid and block sizes
    CHECK(cudaDeviceSynchronize());
    global_dp_sha256<<<grid_size, block_size>>>(dev_out, dev_in, msg_size, total_msg_num);
    CHECK(cudaGetLastError());
    CHECK(cudaDeviceSynchronize());

    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &stop);
    g_result = (stop.tv_sec - start.tv_sec) * 1e6 + (stop.tv_nsec - start.tv_nsec) / 1e3;

    // Copy results back to host
    CHECK(cudaMemcpy(out, dev_out, total_out_size, DEVICE_2_HOST));

    // Clean up
    cudaFree(dev_in);
    cudaFree(dev_out);
}

/**
 * Note that inlen should be sufficiently small that it still allows for
 * an array to be allocated on the stack. Typically 'in' is merely a seed.
 * Outputs outlen number of bytes
 */
__device__ void dev_mgf1(unsigned char* out, unsigned long outlen, const unsigned char* in,
                         unsigned long inlen) {
    unsigned char inbuf[SPX_N + SPX_SHA256_ADDR_BYTES + 4];
    // unsigned char outbuf[SPX_SHA256_OUTPUT_BYTES]; // 715 wrong
    unsigned char outbuf[SPX_SHA256_OUTPUT_BYTES * 2];
    u32 i;

    memcpy(inbuf, in, inlen);

    /* While we can fit in at least another full block of SHA256 output.. */
    for (i = 0; (i + 1) * SPX_SHA256_OUTPUT_BYTES <= outlen; i++) {
        dev_u32_to_bytes(inbuf + inlen, i);
        dev_sha256(out, inbuf, inlen + 4);
        out += SPX_SHA256_OUTPUT_BYTES;
    }
    /* Until we cannot anymore, and we fill the remainder. */
    if (outlen > i * SPX_SHA256_OUTPUT_BYTES) {
        dev_u32_to_bytes(inbuf + inlen, i);
        dev_sha256(outbuf, inbuf, inlen + 4);
        memcpy(out, outbuf, outlen - i * SPX_SHA256_OUTPUT_BYTES);
    }

    // const unsigned int tid = (blockIdx.x * blockDim.x) + threadIdx.x;
    //
    // out -= SPX_SHA256_OUTPUT_BYTES;
    // if (tid == 0) {
    // 	printf("gpu\n");
    // 	printf("out = %02x\n", out[0]);
    // 	printf("out = %02x\n", out[1]);
    // 	printf("out = %02x\n", out[2]);
    // }
    // int a = 1;
    //
    // while (a) {
    // }

} // dev_mgf1

__device__ void dev_mgf1_hg(unsigned char* out, unsigned long outlen, const unsigned char* in,
                            unsigned long inlen) {
    unsigned char inbuf[SPX_SHA256_OUTPUT_BYTES + 4]; // inlen + 4
    unsigned char outbuf[SPX_SHA256_OUTPUT_BYTES];
    unsigned long i;

    memcpy(inbuf, in, inlen);

    /* While we can fit in at least another full block of SHA256 output.. */
    for (i = 0; (i + 1) * SPX_SHA256_OUTPUT_BYTES <= outlen; i++) {
        dev_u32_to_bytes(inbuf + inlen, i);
        dev_sha256(out, inbuf, inlen + 4);
        out += SPX_SHA256_OUTPUT_BYTES;
    }
    /* Until we cannot anymore, and we fill the remainder. */
    if (outlen > i * SPX_SHA256_OUTPUT_BYTES) {
        dev_u32_to_bytes(inbuf + inlen, i);
        dev_sha256(outbuf, inbuf, inlen + 4);
        memcpy(out, outbuf, outlen - i * SPX_SHA256_OUTPUT_BYTES);
    }
    // if (outlen / SPX_SHA256_OUTPUT_BYTES > 1) no output
    // 	printf("outlen = %d\n", outlen / SPX_SHA256_OUTPUT_BYTES);

} // dev_mgf1_hg

__device__ uint8_t dev_state_seeded[40];

/**
 * Absorb the constant pub_seed using one round of the compression function
 * This initializes state_seeded, which can then be reused in thash
 **/
__device__ void dev_seed_state(const unsigned char* pub_seed) {
    uint8_t block[SPX_SHA256_BLOCK_BYTES];
    size_t i;

    for (i = 0; i < SPX_N; ++i) {
        block[i] = pub_seed[i];
    }
    for (i = SPX_N; i < SPX_SHA256_BLOCK_BYTES; ++i) {
        block[i] = 0;
    }

    dev_sha256_inc_init(dev_state_seeded);
    dev_sha256_inc_blocks(dev_state_seeded, block, 1);
} // seed_state

#endif // ifdef SHA256