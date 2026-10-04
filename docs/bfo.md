# Brainfuck Optimized (.bfo)

## Overview

Brainfuck can be optimized into a comparatively fast language
by extracting common conventions into single instructions. For
example, "+++++" can become "+5" and "[-]" can become "=0". In
doing so, the number of computational cycles required to execute
a Brainfuck program is reduced, often significantly.
