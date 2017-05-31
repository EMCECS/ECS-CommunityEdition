#!/usr/bin/python
# coding: utf-8

# Copyright (c) 2013 Mountainstorm
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import urwid

import scrollview
import splitview
from ui.tui import tabview

palette = [
    ('header', '', '', '', '#8ac', 'g10'),
    ('header1', '', '', '', 'g60', 'g20'),
    ('body', '', '', '', '#fff', 'g10'),
    ('dif', '', '', '', '#f00', 'g10'),
    ('scroll', '', '', '', 'g20', 'g10'),
    ('splitbar', '', '', '', 'g50', 'g10')
]

txt1 = urwid.Text( u"tab 1" )
txt2 = urwid.Text( u"tab 2" )
txt3 = urwid.Text( u"""tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab1  tab1
tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2tab 2 tab 2
tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab3  tab3
tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab4  tab4
tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab5  tab5
tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab6  tab6
tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab7  tab7
tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab8  tab8
tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab 9 tab 91234
tab a tab a tab a tab a tab a tab a tab a tab a tab a tab a tab a taba  taba
tab b tab b tab b tab b tab b tab b tab b tab b tab b tab b tab b tabb  tabb
tab c tab c tab c tab c tab c tab c tab c tab c tab c tab c tab c tabc  tabc
tab d tab d tab d tab d tab d tab d tab d tab d tab d tab d tab d tabd  tabd
tab e tab e tab e tab e tab e tab e tab e tab e tab e tab e tab e tabe  tabe
tab f tab f tab f tab f tab f tab f tab f tab f tab f tab f tab f tabf  tabf
tab g tab g tab g tab g tab g tab g tab g tab g tab g tab g tab g tabg  tabg
tab h tab h tab h tab h tab h tab h tab h tab h tab h tab h tab h tabh  tabh
tab i tab i tab i tab i tab i tab i tab i tab i tab i tab i tab i tabi  tabi
tab j tab j tab j tab j tab j tab j tab j tab j tab j tab j tab j tabj  tabj
tab k tab k tab k tab k tab k tab k tab k tab k tab k tab k tab k tabk  tabk
tab l tab l tab l tab l tab l tab l tab l tab l tab l tab l tab l tabl  tabl
tab m tab m tab m tab m tab m tab m tab m tab m tab m tab m tab m tabm  tabm
tab n tab n tab n tab n tab n tab n tab n tab n tab n tab n tab n tabn  tabn
tab o tab o tab o tab o tab o tab o tab o tab o tab o tab o tab o tabo  tabo
tab p tab p tab p tab p tab p tab p tab p tab p tab p tab p tab p tabp  tabp
tab q tab q tab q tab q tab q tab q tab q tab q tab q tab q tab q tabq  tabq
tab r tab r tab r tab r tab r tab r tab r tab r tab r tab r tab r tabr  tabr
tab s tab s tab s tab s tab s tab s tab s tab s tab s tab s tab s tabs  tabs
tab t tab t tab t tab t tab t tab t tab t tab t tab t tab t tab t tabt  tabt
tab u tab u tab u tab u tab u tab u tab u tab u tab u tab u tab u tabu  tabu
tab v tab v tab v tab v tab v tab v tab v tab v tab v tab v tab v tabv  tabv
tab w tab  wtab  wta b wt ab w tab  wtab  wta b wt ab w tab  wta b wtabw tabw
tab x tab x ta  x tb  x ab  xtab  xtab3 xta 3 xtb 3 xab   xab3  xab  x ta x 3
tab y tab y tab y tab y tab y tab y tab y tab y tab y tab y tab y taby3 tay 3
tab z tab z tab z tab z tab z tab z tab z tab z tab z tab z tab z tabz3 taz 3
tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab13 ta1 3
tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab23 ta2 3
tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2tab 2 tab 2
tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab3  tab3
tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab4  tab4
tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab5  tab5
tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab6  tab6
tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab7  tab7
tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab8  tab8
tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab3  tab3
tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab4  tab4
tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab5  tab5
tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab6  tab6
tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab7  tab7
tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab8  tab8
tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab 9 tab 91234
tab a tab a tab a tab a tab a tab a tab a tab a tab a tab a tab a taba  taba
tab b tab b tab b tab b tab b tab b tab b tab b tab b tab b tab b tabb  tabb
tab c tab c tab c tab c tab c tab c tab c tab c tab c tab c tab c tabc  tabc
tab d tab d tab d tab d tab d tab d tab d tab d tab d tab d tab d tabd  tabd
tab e tab e tab e tab e tab e tab e tab e tab e tab e tab e tab e tabe  tabe
tab f tab f tab f tab f tab f tab f tab f tab f tab f tab f tab f tabf  tabf
tab g tab g tab g tab g tab g tab g tab g tab g tab g tab g tab g tabg  tabg
tab h tab h tab h tab h tab h tab h tab h tab h tab h tab h tab h tabh  tabh
tab i tab i tab i tab i tab i tab i tab i tab i tab i tab i tab i tabi  tabi
tab j tab j tab j tab j tab j tab j tab j tab j tab j tab j tab j tabj  tabj
tab k tab k tab k tab k tab k tab k tab k tab k tab k tab k tab k tabk  tabk
tab l tab l tab l tab l tab l tab l tab l tab l tab l tab l tab l tabl  tabl
tab m tab m tab m tab m tab m tab m tab m tab m tab m tab m tab m tabm  tabm
tab n tab n tab n tab n tab n tab n tab n tab n tab n tab n tab n tabn  tabn
tab o tab o tab o tab o tab o tab o tab o tab o tab o tab o tab o tabo  tabo
tab p tab p tab p tab p tab p tab p tab p tab p tab p tab p tab p tabp  tabp
tab q tab q tab q tab q tab q tab q tab q tab q tab q tab q tab q tabq  tabq
tab r tab r tab r tab r tab r tab r tab r tab r tab r tab r tab r tabr  tabr
tab s tab s tab s tab s tab s tab s tab s tab s tab s tab s tab s tabs  tabs
tab t tab t tab t tab t tab t tab t tab t tab t tab t tab t tab t tabt  tabt
tab u tab u tab u tab u tab u tab u tab u tab u tab u tab u tab u tabu  tabu
tab v tab v tab v tab v tab v tab v tab v tab v tab v tab v tab v tabv  tabv
tab w tab  wtab  wta b wt ab w tab  wtab  wta b wt ab w tab  wta b wtabw tabw
tab x tab x ta  x tb  x ab  xtab  xtab3 xta 3 xtb 3 xab   xab3  xab  x ta x 3
tab y tab y tab y tab y tab y tab y tab y tab y tab y tab y tab y taby3 tay 3
tab z tab z tab z tab z tab z tab z tab z tab z tab z tab z tab z tabz3 taz 3
tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab13 ta1 3
tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab23 ta2 3
tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2tab 2 tab 2
tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab3  tab3
tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab4  tab4
tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab5  tab5
tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab6  tab6
tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab7  tab7
tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab8  tab8
tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab3  tab3
tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab4  tab4
tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab5  tab5
tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab6  tab6
tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab7  tab7
tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab8  tab8
tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab 9 tab 91234
tab a tab a tab a tab a tab a tab a tab a tab a tab a tab a tab a taba  taba
tab b tab b tab b tab b tab b tab b tab b tab b tab b tab b tab b tabb  tabb
tab c tab c tab c tab c tab c tab c tab c tab c tab c tab c tab c tabc  tabc
tab d tab d tab d tab d tab d tab d tab d tab d tab d tab d tab d tabd  tabd
tab e tab e tab e tab e tab e tab e tab e tab e tab e tab e tab e tabe  tabe
tab f tab f tab f tab f tab f tab f tab f tab f tab f tab f tab f tabf  tabf
tab g tab g tab g tab g tab g tab g tab g tab g tab g tab g tab g tabg  tabg
tab h tab h tab h tab h tab h tab h tab h tab h tab h tab h tab h tabh  tabh
tab i tab i tab i tab i tab i tab i tab i tab i tab i tab i tab i tabi  tabi
tab j tab j tab j tab j tab j tab j tab j tab j tab j tab j tab j tabj  tabj
tab k tab k tab k tab k tab k tab k tab k tab k tab k tab k tab k tabk  tabk
tab l tab l tab l tab l tab l tab l tab l tab l tab l tab l tab l tabl  tabl
tab m tab m tab m tab m tab m tab m tab m tab m tab m tab m tab m tabm  tabm
tab n tab n tab n tab n tab n tab n tab n tab n tab n tab n tab n tabn  tabn
tab o tab o tab o tab o tab o tab o tab o tab o tab o tab o tab o tabo  tabo
tab p tab p tab p tab p tab p tab p tab p tab p tab p tab p tab p tabp  tabp
tab q tab q tab q tab q tab q tab q tab q tab q tab q tab q tab q tabq  tabq
tab r tab r tab r tab r tab r tab r tab r tab r tab r tab r tab r tabr  tabr
tab s tab s tab s tab s tab s tab s tab s tab s tab s tab s tab s tabs  tabs
tab t tab t tab t tab t tab t tab t tab t tab t tab t tab t tab t tabt  tabt
tab u tab u tab u tab u tab u tab u tab u tab u tab u tab u tab u tabu  tabu
tab v tab v tab v tab v tab v tab v tab v tab v tab v tab v tab v tabv  tabv
tab w tab  wtab  wta b wt ab w tab  wtab  wta b wt ab w tab  wta b wtabw tabw
tab x tab x ta  x tb  x ab  xtab  xtab3 xta 3 xtb 3 xab   xab3  xab  x ta x 3
tab y tab y tab y tab y tab y tab y tab y tab y tab y tab y tab y taby3 tay 3
tab z tab z tab z tab z tab z tab z tab z tab z tab z tab z tab z tabz3 taz 3
tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab13 ta1 3
tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab23 ta2 3
tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2tab 2 tab 2
tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab3  tab3
tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab4  tab4
tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab5  tab5
tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab6  tab6
tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab7  tab7
tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab8  tab8
tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab3  tab3
tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab4  tab4
tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab5  tab5
tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab6  tab6
tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab7  tab7
tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab8  tab8
tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab 9 tab 91234
tab a tab a tab a tab a tab a tab a tab a tab a tab a tab a tab a taba  taba
tab b tab b tab b tab b tab b tab b tab b tab b tab b tab b tab b tabb  tabb
tab c tab c tab c tab c tab c tab c tab c tab c tab c tab c tab c tabc  tabc
tab d tab d tab d tab d tab d tab d tab d tab d tab d tab d tab d tabd  tabd
tab e tab e tab e tab e tab e tab e tab e tab e tab e tab e tab e tabe  tabe
tab f tab f tab f tab f tab f tab f tab f tab f tab f tab f tab f tabf  tabf
tab g tab g tab g tab g tab g tab g tab g tab g tab g tab g tab g tabg  tabg
tab h tab h tab h tab h tab h tab h tab h tab h tab h tab h tab h tabh  tabh
tab i tab i tab i tab i tab i tab i tab i tab i tab i tab i tab i tabi  tabi
tab j tab j tab j tab j tab j tab j tab j tab j tab j tab j tab j tabj  tabj
tab k tab k tab k tab k tab k tab k tab k tab k tab k tab k tab k tabk  tabk
tab l tab l tab l tab l tab l tab l tab l tab l tab l tab l tab l tabl  tabl
tab m tab m tab m tab m tab m tab m tab m tab m tab m tab m tab m tabm  tabm
tab n tab n tab n tab n tab n tab n tab n tab n tab n tab n tab n tabn  tabn
tab o tab o tab o tab o tab o tab o tab o tab o tab o tab o tab o tabo  tabo
tab p tab p tab p tab p tab p tab p tab p tab p tab p tab p tab p tabp  tabp
tab q tab q tab q tab q tab q tab q tab q tab q tab q tab q tab q tabq  tabq
tab r tab r tab r tab r tab r tab r tab r tab r tab r tab r tab r tabr  tabr
tab s tab s tab s tab s tab s tab s tab s tab s tab s tab s tab s tabs  tabs
tab t tab t tab t tab t tab t tab t tab t tab t tab t tab t tab t tabt  tabt
tab u tab u tab u tab u tab u tab u tab u tab u tab u tab u tab u tabu  tabu
tab v tab v tab v tab v tab v tab v tab v tab v tab v tab v tab v tabv  tabv
tab w tab  wtab  wta b wt ab w tab  wtab  wta b wt ab w tab  wta b wtabw tabw
tab x tab x ta  x tb  x ab  xtab  xtab3 xta 3 xtb 3 xab   xab3  xab  x ta x 3
tab y tab y tab y tab y tab y tab y tab y tab y tab y tab y tab y taby3 tay 3
tab z tab z tab z tab z tab z tab z tab z tab z tab z tab z tab z tabz3 taz 3
tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab13 ta1 3
tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab23 ta2 3
tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2tab 2 tab 2
tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab3  tab3
tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab4  tab4
tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab5  tab5
tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab6  tab6
tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab7  tab7
tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab8  tab8
tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab3  tab3
tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab4  tab4
tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab5  tab5
tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab6  tab6
tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab7  tab7
tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab8  tab8
tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab  9tab 9 tab 91234
tab a tab a tab a tab a tab a tab a tab a tab a tab a tab a tab a taba  taba
tab b tab b tab b tab b tab b tab b tab b tab b tab b tab b tab b tabb  tabb
tab c tab c tab c tab c tab c tab c tab c tab c tab c tab c tab c tabc  tabc
tab d tab d tab d tab d tab d tab d tab d tab d tab d tab d tab d tabd  tabd
tab e tab e tab e tab e tab e tab e tab e tab e tab e tab e tab e tabe  tabe
tab f tab f tab f tab f tab f tab f tab f tab f tab f tab f tab f tabf  tabf
tab g tab g tab g tab g tab g tab g tab g tab g tab g tab g tab g tabg  tabg
tab h tab h tab h tab h tab h tab h tab h tab h tab h tab h tab h tabh  tabh
tab i tab i tab i tab i tab i tab i tab i tab i tab i tab i tab i tabi  tabi
tab j tab j tab j tab j tab j tab j tab j tab j tab j tab j tab j tabj  tabj
tab k tab k tab k tab k tab k tab k tab k tab k tab k tab k tab k tabk  tabk
tab l tab l tab l tab l tab l tab l tab l tab l tab l tab l tab l tabl  tabl
tab m tab m tab m tab m tab m tab m tab m tab m tab m tab m tab m tabm  tabm
tab n tab n tab n tab n tab n tab n tab n tab n tab n tab n tab n tabn  tabn
tab o tab o tab o tab o tab o tab o tab o tab o tab o tab o tab o tabo  tabo
tab p tab p tab p tab p tab p tab p tab p tab p tab p tab p tab p tabp  tabp
tab q tab q tab q tab q tab q tab q tab q tab q tab q tab q tab q tabq  tabq
tab r tab r tab r tab r tab r tab r tab r tab r tab r tab r tab r tabr  tabr
tab s tab s tab s tab s tab s tab s tab s tab s tab s tab s tab s tabs  tabs
tab t tab t tab t tab t tab t tab t tab t tab t tab t tab t tab t tabt  tabt
tab u tab u tab u tab u tab u tab u tab u tab u tab u tab u tab u tabu  tabu
tab v tab v tab v tab v tab v tab v tab v tab v tab v tab v tab v tabv  tabv
tab w tab  wtab  wta b wt ab w tab  wtab  wta b wt ab w tab  wta b wtabw tabw
tab x tab x ta  x tb  x ab  xtab  xtab3 xta 3 xtb 3 xab   xab3  xab  x ta x 3
tab y tab y tab y tab y tab y tab y tab y tab y tab y tab y tab y taby3 tay 3
tab z tab z tab z tab z tab z tab z tab z tab z tab z tab z tab z tabz3 taz 3
tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab 1 tab13 ta1 3
tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab23 ta2 3
tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2 tab 2tab 2 tab 2
tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab 3 tab3  tab3
tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab 4 tab4  tab4
tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab 5 tab5  tab5
tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab 6 tab6  tab6
tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab 7 tab7  tab7
tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab 8 tab8  tab8""" )

f1 = urwid.AttrWrap( urwid.Filler( urwid.AttrWrap( urwid.LineBox( txt1, "body" ), 'dif' ) ), 'body' )
f2 = scrollview.ScrollView(urwid.BigText("Hello World and welcome to my scroll view",
                                         urwid.Thin6x6Font( )), 'scroll')
f3 = scrollview.ScrollView(txt3, 'scroll')

tab_view = tabview.TabView(
        'header',
        'header1',
        [ (u'Hello World', f1, True), (u'Goodbyte', f2, True), (u'test.py', f3) ]
)

split1 = splitview.SplitView(
        f1,
        tab_view,
        False,
        0.4,
        'splitbar'
)

split = splitview.SplitView(
        split1,
        urwid.AttrWrap( urwid.Filler( urwid.AttrWrap( urwid.LineBox( txt2, "body" ), 'dif' ) ), 'body' ),
        True,
        0.3,
        'splitbar'
)


def unhandled( key ):
    if key == 'ctrl w':
        tab_view.close_active_tab( )
        return True
    elif key == 'm':
        tab_view.set_active_next( )
    elif key == 'n':
        tab_view.set_active_prev( )
    elif key in ('q', 'Q'):
        raise urwid.ExitMainLoop( )


loop = urwid.MainLoop(split, palette, unhandled_input=unhandled)
loop.screen.set_terminal_properties(colors=256)
loop.screen.set_mouse_tracking()
loop.run( )
