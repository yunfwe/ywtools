cdef extern from 'stdio.h':
    extern int printf(const char *format, ...)

def say(s):
    printf(s)