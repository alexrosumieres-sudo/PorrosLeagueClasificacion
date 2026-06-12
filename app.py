import streamlit as st
import pandas as pd
from sqlalchemy import text
import datetime
import os
import plotly.express as px
import random
import itertools
import numpy as np
import time
import pytz
from streamlit_gsheets import GSheetsConnection
 
# --- 1. CONFIGURACIONES GENERALES ---
PERFILES_DIR = "perfiles/"
LOGOS_DIR = "logos/"

# --- MATRIZ OFICIAL DE TERCEROS (ANEXO C FIFA) ---
# Sustituye el contenido de TEXTO_FIFA_TERCEROS por TODO el bloque de 495 líneas que me pasaste por el chat.
# He puesto las 3 primeras y las 2 últimas como ejemplo, ¡tú pégalo entero entre las triples comillas!

TEXTO_FIFA_TERCEROS = """
Option 1A 1B 1D 1E 1G 1I 1K 1L
1 3E 3J 3I 3F 3H 3G 3L 3K
2 3H 3G 3I 3D 3J 3F 3L 3K
3 3E 3J 3I 3D 3H 3G 3L 3K
4 3E 3J 3I 3D 3H 3F 3L 3K
5 3E 3G 3I 3D 3J 3F 3L 3K
6 3E 3G 3J 3D 3H 3F 3L 3K
7 3E 3G 3I 3D 3H 3F 3L 3K
8 3E 3G 3J 3D 3H 3F 3L 3I
9 3E 3G 3J 3D 3H 3F 3I 3K
10 3H 3G 3I 3C 3J 3F 3L 3K
11 3E 3J 3I 3C 3H 3G 3L 3K
12 3E 3J 3I 3C 3H 3F 3L 3K
13 3E 3G 3I 3C 3J 3F 3L 3K
14 3E 3G 3J 3C 3H 3F 3L 3K
15 3E 3G 3I 3C 3H 3F 3L 3K
16 3E 3G 3J 3C 3H 3F 3L 3I
17 3E 3G 3J 3C 3H 3F 3I 3K
18 3H 3G 3I 3C 3J 3D 3L 3K
19 3C 3J 3I 3D 3H 3F 3L 3K
20 3C 3G 3I 3D 3J 3F 3L 3K
21 3C 3G 3J 3D 3H 3F 3L 3K
22 3C 3G 3I 3D 3H 3F 3L 3K
23 3C 3G 3J 3D 3H 3F 3L 3I
24 3C 3G 3J 3D 3H 3F 3I 3K
25 3E 3J 3I 3C 3H 3D 3L 3K
26 3E 3G 3I 3C 3J 3D 3L 3K
27 3E 3G 3J 3C 3H 3D 3L 3K
28 3E 3G 3I 3C 3H 3D 3L 3K
29 3E 3G 3J 3C 3H 3D 3L 3I
30 3E 3G 3J 3C 3H 3D 3I 3K
31 3C 3J 3E 3D 3I 3F 3L 3K
32 3C 3J 3E 3D 3H 3F 3L 3K
33 3C 3E 3I 3D 3H 3F 3L 3K
34 3C 3J 3E 3D 3H 3F 3L 3I
35 3C 3J 3E 3D 3H 3F 3I 3K
36 3C 3G 3E 3D 3J 3F 3L 3K
37 3C 3G 3E 3D 3I 3F 3L 3K
38 3C 3G 3E 3D 3J 3F 3L 3I
39 3C 3G 3E 3D 3J 3F 3I 3K
40 3C 3G 3E 3D 3H 3F 3L 3K
41 3C 3G 3J 3D 3H 3F 3L 3E
42 3C 3G 3J 3D 3H 3F 3E 3K
43 3C 3G 3E 3D 3H 3F 3L 3I
44 3C 3G 3E 3D 3H 3F 3I 3K
45 3C 3G 3J 3D 3H 3F 3E 3I
46 3H 3J 3B 3F 3I 3G 3L 3K
47 3E 3J 3I 3B 3H 3G 3L 3K
48 3E 3J 3B 3F 3I 3H 3L 3K
49 3E 3J 3B 3F 3I 3G 3L 3K
50 3E 3J 3B 3F 3H 3G 3L 3K
51 3E 3G 3B 3F 3I 3H 3L 3K
52 3E 3J 3B 3F 3H 3G 3L 3I
53 3E 3J 3B 3F 3H 3G 3I 3K
54 3H 3J 3B 3D 3I 3G 3L 3K
55 3H 3J 3B 3D 3I 3F 3L 3K
56 3I 3G 3B 3D 3J 3F 3L 3K
57 3H 3G 3B 3D 3J 3F 3L 3K
58 3H 3G 3B 3D 3I 3F 3L 3K
59 3H 3G 3B 3D 3J 3F 3L 3I
60 3H 3G 3B 3D 3J 3F 3I 3K
61 3E 3J 3B 3D 3I 3H 3L 3K
62 3E 3J 3B 3D 3I 3G 3L 3K
63 3E 3J 3B 3D 3H 3G 3L 3K
64 3E 3G 3B 3D 3I 3H 3L 3K
65 3E 3J 3B 3D 3H 3G 3L 3I
66 3E 3J 3B 3D 3H 3G 3I 3K
67 3E 3J 3B 3D 3I 3F 3L 3K
68 3E 3J 3B 3D 3H 3F 3L 3K
69 3E 3I 3B 3D 3H 3F 3L 3K
70 3E 3J 3B 3D 3H 3F 3L 3I
71 3E 3J 3B 3D 3H 3F 3I 3K
72 3E 3G 3B 3D 3J 3F 3L 3K
73 3E 3G 3B 3D 3I 3F 3L 3K
74 3E 3G 3B 3D 3J 3F 3L 3I
75 3E 3G 3B 3D 3J 3F 3I 3K
76 3E 3G 3B 3D 3H 3F 3L 3K
77 3H 3G 3B 3D 3J 3F 3L 3E
78 3H 3G 3B 3D 3J 3F 3E 3K
79 3E 3G 3B 3D 3H 3F 3L 3I
80 3E 3G 3B 3D 3H 3F 3I 3K
81 3H 3G 3B 3D 3J 3F 3E 3I
82 3H 3J 3B 3C 3I 3G 3L 3K
83 3H 3J 3B 3C 3I 3F 3L 3K
84 3I 3G 3B 3C 3J 3F 3L 3K
85 3H 3G 3B 3C 3J 3F 3L 3K
86 3H 3G 3B 3C 3I 3F 3L 3K
87 3H 3G 3B 3C 3J 3F 3L 3I
88 3H 3G 3B 3C 3J 3F 3I 3K
89 3E 3J 3B 3C 3I 3H 3L 3K
90 3E 3J 3B 3C 3I 3G 3L 3K
91 3E 3J 3B 3C 3H 3G 3L 3K
92 3E 3G 3B 3C 3I 3H 3L 3K
93 3E 3J 3B 3C 3H 3G 3L 3I
94 3E 3J 3B 3C 3H 3G 3I 3K
95 3E 3J 3B 3C 3I 3F 3L 3K
96 3E 3J 3B 3C 3H 3F 3L 3K
97 3E 3I 3B 3C 3H 3F 3L 3K
98 3E 3J 3B 3C 3H 3F 3L 3I
99 3E 3J 3B 3C 3H 3F 3I 3K
100 3E 3G 3B 3C 3J 3F 3L 3K
101 3E 3G 3B 3C 3I 3F 3L 3K
102 3E 3G 3B 3C 3J 3F 3L 3I
103 3E 3G 3B 3C 3J 3F 3I 3K
104 3E 3G 3B 3C 3H 3F 3L 3K
105 3H 3G 3B 3C 3J 3F 3L 3E
106 3H 3G 3B 3C 3J 3F 3E 3K
107 3E 3G 3B 3C 3H 3F 3L 3I
108 3E 3G 3B 3C 3H 3F 3I 3K
109 3H 3G 3B 3C 3J 3F 3E 3I
110 3H 3J 3B 3C 3I 3D 3L 3K
111 3I 3G 3B 3C 3J 3D 3L 3K
112 3H 3G 3B 3C 3J 3D 3L 3K
113 3H 3G 3B 3C 3I 3D 3L 3K
114 3H 3G 3B 3C 3J 3D 3L 3I
115 3H 3G 3B 3C 3J 3D 3I 3K
116 3C 3J 3B 3D 3I 3F 3L 3K
117 3C 3J 3B 3D 3H 3F 3L 3K
118 3C 3I 3B 3D 3H 3F 3L 3K
119 3C 3J 3B 3D 3H 3F 3L 3I
120 3C 3J 3B 3D 3H 3F 3I 3K
121 3C 3G 3B 3D 3J 3F 3L 3K
122 3C 3G 3B 3D 3I 3F 3L 3K
123 3C 3G 3B 3D 3J 3F 3L 3I
124 3C 3G 3B 3D 3J 3F 3I 3K
125 3C 3G 3B 3D 3H 3F 3L 3K
126 3C 3G 3B 3D 3H 3F 3L 3J
127 3H 3G 3B 3C 3J 3F 3D 3K
128 3C 3G 3B 3D 3H 3F 3L 3I
129 3C 3G 3B 3D 3H 3F 3I 3K
130 3H 3G 3B 3C 3J 3F 3D 3I
131 3E 3J 3B 3C 3I 3D 3L 3K
132 3E 3J 3B 3C 3H 3D 3L 3K
133 3E 3I 3B 3C 3H 3D 3L 3K
134 3E 3J 3B 3C 3H 3D 3L 3I
135 3E 3J 3B 3C 3H 3D 3I 3K
136 3E 3G 3B 3C 3J 3D 3L 3K
137 3E 3G 3B 3C 3I 3D 3L 3K
138 3E 3G 3B 3C 3J 3D 3L 3I
139 3E 3G 3B 3C 3J 3D 3I 3K
140 3E 3G 3B 3C 3H 3D 3L 3K
141 3H 3G 3B 3C 3J 3D 3L 3E
142 3H 3G 3B 3C 3J 3D 3E 3K
143 3E 3G 3B 3C 3H 3D 3L 3I
144 3E 3G 3B 3C 3H 3D 3I 3K
145 3H 3G 3B 3C 3J 3D 3E 3I
146 3C 3J 3B 3D 3E 3F 3L 3K
147 3C 3E 3B 3D 3I 3F 3L 3K
148 3C 3J 3B 3D 3E 3F 3L 3I
149 3C 3J 3B 3D 3E 3F 3I 3K
150 3C 3E 3B 3D 3H 3F 3L 3K
151 3C 3J 3B 3D 3H 3F 3L 3E
152 3C 3J 3B 3D 3H 3F 3E 3K
153 3C 3E 3B 3D 3H 3F 3L 3I
154 3C 3E 3B 3D 3H 3F 3I 3K
155 3C 3J 3B 3D 3H 3F 3E 3I
156 3C 3G 3B 3D 3E 3F 3L 3K
157 3C 3G 3B 3D 3J 3F 3L 3E
158 3C 3G 3B 3D 3J 3F 3E 3K
159 3C 3G 3B 3D 3E 3F 3L 3I
160 3C 3G 3B 3D 3E 3F 3I 3K
161 3C 3G 3B 3D 3J 3F 3E 3I
162 3C 3G 3B 3D 3H 3F 3L 3E
163 3C 3G 3B 3D 3H 3F 3E 3K
164 3H 3G 3B 3C 3J 3F 3D 3E
165 3C 3G 3B 3D 3H 3F 3E 3I
166 3H 3J 3I 3F 3A 3G 3L 3K
167 3E 3J 3I 3A 3H 3G 3L 3K
168 3E 3J 3I 3F 3A 3H 3L 3K
169 3E 3J 3I 3F 3A 3G 3L 3K
170 3E 3G 3J 3F 3A 3H 3L 3K
171 3E 3G 3I 3F 3A 3H 3L 3K
172 3E 3G 3J 3F 3A 3H 3L 3I
173 3E 3G 3J 3F 3A 3H 3I 3K
174 3H 3J 3I 3D 3A 3G 3L 3K
175 3H 3J 3I 3D 3A 3F 3L 3K
176 3I 3G 3J 3D 3A 3F 3L 3K
177 3H 3G 3J 3D 3A 3F 3L 3K
178 3H 3G 3I 3D 3A 3F 3L 3K
179 3H 3G 3J 3D 3A 3F 3L 3I
180 3H 3G 3J 3D 3A 3F 3I 3K
181 3E 3J 3I 3D 3A 3H 3L 3K
182 3E 3J 3I 3D 3A 3G 3L 3K
183 3E 3G 3J 3D 3A 3H 3L 3K
184 3E 3G 3I 3D 3A 3H 3L 3K
185 3E 3G 3J 3D 3A 3H 3L 3I
186 3E 3G 3J 3D 3A 3H 3I 3K
187 3E 3J 3I 3D 3A 3F 3L 3K
188 3H 3J 3E 3D 3A 3F 3L 3K
189 3H 3E 3I 3D 3A 3F 3L 3K
190 3H 3J 3E 3D 3A 3F 3L 3I
191 3H 3J 3E 3D 3A 3F 3I 3K
192 3E 3G 3J 3D 3A 3F 3L 3K
193 3E 3G 3I 3D 3A 3F 3L 3K
194 3E 3G 3J 3D 3A 3F 3L 3I
195 3E 3G 3J 3D 3A 3F 3I 3K
196 3H 3G 3E 3D 3A 3F 3L 3K
197 3H 3G 3J 3D 3A 3F 3L 3E
198 3H 3G 3J 3D 3A 3F 3E 3K
199 3H 3G 3E 3D 3A 3F 3L 3I
200 3H 3G 3E 3D 3A 3F 3I 3K
201 3H 3G 3J 3D 3A 3F 3E 3I
202 3H 3J 3I 3C 3A 3G 3L 3K
203 3H 3J 3I 3C 3A 3F 3L 3K
204 3I 3G 3J 3C 3A 3F 3L 3K
205 3H 3G 3J 3C 3A 3F 3L 3K
206 3H 3G 3I 3C 3A 3F 3L 3K
207 3H 3G 3J 3C 3A 3F 3L 3I
208 3H 3G 3J 3C 3A 3F 3I 3K
209 3E 3J 3I 3C 3A 3H 3L 3K
210 3E 3J 3I 3C 3A 3G 3L 3K
211 3E 3G 3J 3C 3A 3H 3L 3K
212 3E 3G 3I 3C 3A 3H 3L 3K
213 3E 3G 3J 3C 3A 3H 3L 3I
214 3E 3G 3J 3C 3A 3H 3I 3K
215 3E 3J 3I 3C 3A 3F 3L 3K
216 3H 3J 3E 3C 3A 3F 3L 3K
217 3H 3E 3I 3C 3A 3F 3L 3K
218 3H 3J 3E 3C 3A 3F 3L 3I
219 3H 3J 3E 3C 3A 3F 3I 3K
220 3E 3G 3J 3C 3A 3F 3L 3K
221 3E 3G 3I 3C 3A 3F 3L 3K
222 3E 3G 3J 3C 3A 3F 3L 3I
223 3E 3G 3J 3C 3A 3F 3I 3K
224 3H 3G 3E 3C 3A 3F 3L 3K
225 3H 3G 3J 3C 3A 3F 3L 3E
226 3H 3G 3J 3C 3A 3F 3E 3K
227 3H 3G 3E 3C 3A 3F 3L 3I
228 3H 3G 3E 3C 3A 3F 3I 3K
229 3H 3G 3J 3C 3A 3F 3E 3I
230 3H 3J 3I 3C 3A 3D 3L 3K
231 3I 3G 3J 3C 3A 3D 3L 3K
232 3H 3G 3J 3C 3A 3D 3L 3K
233 3H 3G 3I 3C 3A 3D 3L 3K
234 3H 3G 3J 3C 3A 3D 3L 3I
235 3H 3G 3J 3C 3A 3D 3I 3K
236 3C 3J 3I 3D 3A 3F 3L 3K
237 3H 3J 3F 3C 3A 3D 3L 3K
238 3H 3F 3I 3C 3A 3D 3L 3K
239 3H 3J 3F 3C 3A 3D 3L 3I
240 3H 3J 3F 3C 3A 3D 3I 3K
241 3C 3G 3J 3D 3A 3F 3L 3K
242 3C 3G 3I 3D 3A 3F 3L 3K
243 3C 3G 3J 3D 3A 3F 3L 3I
244 3C 3G 3J 3D 3A 3F 3I 3K
245 3H 3G 3F 3C 3A 3D 3L 3K
246 3C 3G 3J 3D 3A 3F 3L 3H
247 3H 3G 3J 3C 3A 3F 3D 3K
248 3H 3G 3F 3C 3A 3D 3L 3I
249 3H 3G 3F 3C 3A 3D 3I 3K
250 3H 3G 3J 3C 3A 3F 3D 3I
251 3E 3J 3I 3C 3A 3D 3L 3K
252 3H 3J 3E 3C 3A 3D 3L 3K
253 3H 3E 3I 3C 3A 3D 3L 3K
254 3H 3J 3E 3C 3A 3D 3L 3I
255 3H 3J 3E 3C 3A 3D 3I 3K
256 3E 3G 3J 3C 3A 3D 3L 3K
257 3E 3G 3I 3C 3A 3D 3L 3K
258 3E 3G 3J 3C 3A 3D 3L 3I
259 3E 3G 3J 3C 3A 3D 3I 3K
260 3H 3G 3E 3C 3A 3D 3L 3K
261 3H 3G 3J 3C 3A 3D 3L 3E
262 3H 3G 3J 3C 3A 3D 3E 3K
263 3H 3G 3E 3C 3A 3D 3L 3I
264 3H 3G 3E 3C 3A 3D 3I 3K
265 3H 3G 3J 3C 3A 3D 3E 3I
266 3C 3J 3E 3D 3A 3F 3L 3K
267 3C 3E 3I 3D 3A 3F 3L 3K
268 3C 3J 3E 3D 3A 3F 3L 3I
269 3C 3J 3E 3D 3A 3F 3I 3K
270 3H 3E 3F 3C 3A 3D 3L 3K
271 3H 3J 3F 3C 3A 3D 3L 3E
272 3H 3J 3E 3C 3A 3F 3D 3K
273 3H 3E 3F 3C 3A 3D 3L 3I
274 3H 3E 3F 3C 3A 3D 3I 3K
275 3H 3J 3E 3C 3A 3F 3D 3I
276 3C 3G 3E 3D 3A 3F 3L 3K
277 3C 3G 3J 3D 3A 3F 3L 3E
278 3C 3G 3J 3D 3A 3F 3E 3K
279 3C 3G 3E 3D 3A 3F 3L 3I
280 3C 3G 3E 3D 3A 3F 3I 3K
281 3C 3G 3J 3D 3A 3F 3E 3I
282 3H 3G 3F 3C 3A 3D 3L 3E
283 3H 3G 3E 3C 3A 3F 3D 3K
284 3H 3G 3J 3C 3A 3F 3D 3E
285 3H 3G 3E 3C 3A 3F 3D 3I
286 3H 3J 3B 3A 3I 3G 3L 3K
287 3H 3J 3B 3A 3I 3F 3L 3K
288 3I 3J 3B 3F 3A 3G 3L 3K
289 3H 3J 3B 3F 3A 3G 3L 3K
290 3H 3G 3B 3A 3I 3F 3L 3K
291 3H 3J 3B 3F 3A 3G 3L 3I
292 3H 3J 3B 3F 3A 3G 3I 3K
293 3E 3J 3B 3A 3I 3H 3L 3K
294 3E 3J 3B 3A 3I 3G 3L 3K
295 3E 3J 3B 3A 3H 3G 3L 3K
296 3E 3G 3B 3A 3I 3H 3L 3K
297 3E 3J 3B 3A 3H 3G 3L 3I
298 3E 3J 3B 3A 3H 3G 3I 3K
299 3E 3J 3B 3A 3I 3F 3L 3K
300 3E 3J 3B 3F 3A 3H 3L 3K
301 3E 3I 3B 3F 3A 3H 3L 3K
302 3E 3J 3B 3F 3A 3H 3L 3I
303 3E 3J 3B 3F 3A 3H 3I 3K
304 3E 3J 3B 3F 3A 3G 3L 3K
305 3E 3G 3B 3A 3I 3F 3L 3K
306 3E 3J 3B 3F 3A 3G 3L 3I
307 3E 3J 3B 3F 3A 3G 3I 3K
308 3E 3G 3B 3F 3A 3H 3L 3K
309 3H 3J 3B 3F 3A 3G 3L 3E
310 3H 3J 3B 3F 3A 3G 3E 3K
311 3E 3G 3B 3F 3A 3H 3L 3I
312 3E 3G 3B 3F 3A 3H 3I 3K
313 3H 3J 3B 3F 3A 3G 3E 3I
314 3I 3J 3B 3D 3A 3H 3L 3K
315 3I 3J 3B 3D 3A 3G 3L 3K
316 3H 3J 3B 3D 3A 3G 3L 3K
317 3I 3G 3B 3D 3A 3H 3L 3K
318 3H 3J 3B 3D 3A 3G 3L 3I
319 3H 3J 3B 3D 3A 3G 3I 3K
320 3I 3J 3B 3D 3A 3F 3L 3K
321 3H 3J 3B 3D 3A 3F 3L 3K
322 3H 3I 3B 3D 3A 3F 3L 3K
323 3H 3J 3B 3D 3A 3F 3L 3I
324 3H 3J 3B 3D 3A 3F 3I 3K
325 3F 3J 3B 3D 3A 3G 3L 3K
326 3I 3G 3B 3D 3A 3F 3L 3K
327 3F 3J 3B 3D 3A 3G 3L 3I
328 3F 3J 3B 3D 3A 3G 3I 3K
329 3H 3G 3B 3D 3A 3F 3L 3K
330 3H 3G 3B 3D 3A 3F 3L 3J
331 3H 3G 3B 3D 3A 3F 3J 3K
332 3H 3G 3B 3D 3A 3F 3L 3I
333 3H 3G 3B 3D 3A 3F 3I 3K
334 3H 3G 3B 3D 3A 3F 3I 3J
335 3E 3J 3B 3A 3I 3D 3L 3K
336 3E 3J 3B 3D 3A 3H 3L 3K
337 3E 3I 3B 3D 3A 3H 3L 3K
338 3E 3J 3B 3D 3A 3H 3L 3I
339 3E 3J 3B 3D 3A 3H 3I 3K
340 3E 3J 3B 3D 3A 3G 3L 3K
341 3E 3G 3B 3A 3I 3D 3L 3K
342 3E 3J 3B 3D 3A 3G 3L 3I
343 3E 3J 3B 3D 3A 3G 3I 3K
344 3E 3G 3B 3D 3A 3H 3L 3K
345 3H 3J 3B 3D 3A 3G 3L 3E
346 3H 3J 3B 3D 3A 3G 3E 3K
347 3E 3G 3B 3D 3A 3H 3L 3I
348 3E 3G 3B 3D 3A 3H 3I 3K
349 3H 3J 3B 3D 3A 3G 3E 3I
350 3E 3J 3B 3D 3A 3F 3L 3K
351 3E 3I 3B 3D 3A 3F 3L 3K
352 3E 3J 3B 3D 3A 3F 3L 3I
353 3E 3J 3B 3D 3A 3F 3I 3K
354 3H 3E 3B 3D 3A 3F 3L 3K
355 3H 3J 3B 3D 3A 3F 3L 3E
356 3H 3J 3B 3D 3A 3F 3E 3K
357 3H 3E 3B 3D 3A 3F 3L 3I
358 3H 3E 3B 3D 3A 3F 3I 3K
359 3H 3J 3B 3D 3A 3F 3E 3I
360 3E 3G 3B 3D 3A 3F 3L 3K
361 3E 3G 3B 3D 3A 3F 3L 3J
362 3E 3G 3B 3D 3A 3F 3J 3K
363 3E 3G 3B 3D 3A 3F 3L 3I
364 3E 3G 3B 3D 3A 3F 3I 3K
365 3E 3G 3B 3D 3A 3F 3I 3J
366 3H 3G 3B 3D 3A 3F 3L 3E
367 3H 3G 3B 3D 3A 3F 3E 3K
368 3H 3G 3B 3D 3A 3F 3E 3J
369 3H 3G 3B 3D 3A 3F 3E 3I
370 3I 3J 3B 3C 3A 3H 3L 3K
371 3I 3J 3B 3C 3A 3G 3L 3K
372 3H 3J 3B 3C 3A 3G 3L 3K
373 3I 3G 3B 3C 3A 3H 3L 3K
374 3H 3J 3B 3C 3A 3G 3L 3I
375 3H 3J 3B 3C 3A 3G 3I 3K
376 3I 3J 3B 3C 3A 3F 3L 3K
377 3H 3J 3B 3C 3A 3F 3L 3K
378 3H 3I 3B 3C 3A 3F 3L 3K
379 3H 3J 3B 3C 3A 3F 3L 3I
380 3H 3J 3B 3C 3A 3F 3I 3K
381 3C 3J 3B 3F 3A 3G 3L 3K
382 3I 3G 3B 3C 3A 3F 3L 3K
383 3C 3J 3B 3F 3A 3G 3L 3I
384 3C 3J 3B 3F 3A 3G 3I 3K
385 3H 3G 3B 3C 3A 3F 3L 3K
386 3H 3G 3B 3C 3A 3F 3L 3J
387 3H 3G 3B 3C 3A 3F 3J 3K
388 3H 3G 3B 3C 3A 3F 3L 3I
389 3H 3G 3B 3C 3A 3F 3I 3K
390 3H 3G 3B 3C 3A 3F 3I 3J
391 3E 3J 3B 3A 3I 3C 3L 3K
392 3E 3J 3B 3C 3A 3H 3L 3K
393 3E 3I 3B 3C 3A 3H 3L 3K
394 3E 3J 3B 3C 3A 3H 3L 3I
395 3E 3J 3B 3C 3A 3H 3I 3K
396 3E 3J 3B 3C 3A 3G 3L 3K
397 3E 3G 3B 3A 3I 3C 3L 3K
398 3E 3J 3B 3C 3A 3G 3L 3I
399 3E 3J 3B 3C 3A 3G 3I 3K
400 3E 3G 3B 3C 3A 3H 3L 3K
401 3H 3J 3B 3C 3A 3G 3L 3E
402 3H 3J 3B 3C 3A 3G 3E 3K
403 3E 3G 3B 3C 3A 3H 3L 3I
404 3E 3G 3B 3C 3A 3H 3I 3K
405 3H 3J 3B 3C 3A 3G 3E 3I
406 3E 3J 3B 3C 3A 3F 3L 3K
407 3E 3I 3B 3C 3A 3F 3L 3K
408 3E 3J 3B 3C 3A 3F 3L 3I
409 3E 3J 3B 3C 3A 3F 3I 3K
410 3H 3E 3B 3C 3A 3F 3L 3K
411 3H 3J 3B 3C 3A 3F 3L 3E
412 3H 3J 3B 3C 3A 3F 3E 3K
413 3H 3E 3B 3C 3A 3F 3L 3I
414 3H 3E 3B 3C 3A 3F 3I 3K
415 3H 3J 3B 3C 3A 3F 3E 3I
416 3E 3G 3B 3C 3A 3F 3L 3K
417 3E 3G 3B 3C 3A 3F 3L 3J
418 3E 3G 3B 3C 3A 3F 3J 3K
419 3E 3G 3B 3C 3A 3F 3L 3I
420 3E 3G 3B 3C 3A 3F 3I 3K
421 3E 3G 3B 3C 3A 3F 3I 3J
422 3H 3G 3B 3C 3A 3F 3L 3E
423 3H 3G 3B 3C 3A 3F 3E 3K
424 3H 3G 3B 3C 3A 3F 3E 3J
425 3H 3G 3B 3C 3A 3F 3E 3I
426 3I 3J 3B 3C 3A 3D 3L 3K
427 3H 3J 3B 3C 3A 3D 3L 3K
428 3H 3I 3B 3C 3A 3D 3L 3K
429 3H 3J 3B 3C 3A 3D 3L 3I
430 3H 3J 3B 3C 3A 3D 3I 3K
431 3C 3J 3B 3D 3A 3G 3L 3K
432 3I 3G 3B 3C 3A 3D 3L 3K
433 3C 3J 3B 3D 3A 3G 3L 3I
434 3C 3J 3B 3D 3A 3G 3I 3K
435 3H 3G 3B 3C 3A 3D 3L 3K
436 3H 3G 3B 3C 3A 3D 3L 3J
437 3H 3G 3B 3C 3A 3D 3J 3K
438 3H 3G 3B 3C 3A 3D 3L 3I
439 3H 3G 3B 3C 3A 3D 3I 3K
440 3H 3G 3B 3C 3A 3D 3I 3J
441 3C 3J 3B 3D 3A 3F 3L 3K
442 3C 3I 3B 3D 3A 3F 3L 3K
443 3C 3J 3B 3D 3A 3F 3L 3I
444 3C 3J 3B 3D 3A 3F 3I 3K
445 3H 3F 3B 3C 3A 3D 3L 3K
446 3C 3J 3B 3D 3A 3F 3L 3H
447 3H 3J 3B 3C 3A 3F 3D 3K
448 3H 3F 3B 3C 3A 3D 3L 3I
449 3H 3F 3B 3C 3A 3D 3I 3K
450 3H 3J 3B 3C 3A 3F 3D 3I
451 3C 3G 3B 3D 3A 3F 3L 3K
452 3C 3G 3B 3D 3A 3F 3L 3J
453 3C 3G 3B 3D 3A 3F 3J 3K
454 3C 3G 3B 3D 3A 3F 3L 3I
455 3C 3G 3B 3D 3A 3F 3I 3K
456 3C 3G 3B 3D 3A 3F 3I 3J
457 3C 3G 3B 3D 3A 3F 3L 3H
458 3H 3G 3B 3C 3A 3F 3D 3K
459 3H 3G 3B 3C 3A 3F 3D 3J
460 3H 3G 3B 3C 3A 3F 3D 3I
461 3E 3J 3B 3C 3A 3D 3L 3K
462 3E 3I 3B 3C 3A 3D 3L 3K
463 3E 3J 3B 3C 3A 3D 3L 3I
464 3E 3J 3B 3C 3A 3D 3I 3K
465 3H 3E 3B 3C 3A 3D 3L 3K
466 3H 3J 3B 3C 3A 3D 3L 3E
467 3H 3J 3B 3C 3A 3D 3E 3K
468 3H 3E 3B 3C 3A 3D 3L 3I
469 3H 3E 3B 3C 3A 3D 3I 3K
470 3H 3J 3B 3C 3A 3D 3E 3I
471 3E 3G 3B 3C 3A 3D 3L 3K
472 3E 3G 3B 3C 3A 3D 3L 3J
473 3E 3G 3B 3C 3A 3D 3J 3K
474 3E 3G 3B 3C 3A 3D 3L 3I
475 3E 3G 3B 3C 3A 3D 3I 3K
476 3E 3G 3B 3C 3A 3D 3I 3J
477 3H 3G 3B 3C 3A 3D 3L 3E
478 3H 3G 3B 3C 3A 3D 3E 3K
479 3H 3G 3B 3C 3A 3D 3E 3J
480 3H 3G 3B 3C 3A 3D 3E 3I
481 3C 3E 3B 3D 3A 3F 3L 3K
482 3C 3J 3B 3D 3A 3F 3L 3E
483 3C 3J 3B 3D 3A 3F 3E 3K
484 3C 3E 3B 3D 3A 3F 3L 3I
485 3C 3E 3B 3D 3A 3F 3I 3K
486 3C 3J 3B 3D 3A 3F 3E 3I
487 3H 3F 3B 3C 3A 3D 3L 3E
488 3H 3E 3B 3C 3A 3F 3D 3K
489 3H 3J 3B 3C 3A 3F 3D 3E
490 3H 3E 3B 3C 3A 3F 3D 3I
491 3C 3G 3B 3D 3A 3F 3L 3E
492 3C 3G 3B 3D 3A 3F 3E 3K
493 3C 3G 3B 3D 3A 3F 3E 3J
494 3C 3G 3B 3D 3A 3F 3E 3I
495 3H 3G 3B 3C 3A 3F 3D 3E
"""

def generar_matriz_terceros(texto):
    matriz = {}
    lineas = texto.strip().split("\n")
    for linea in lineas:
        partes = linea.split()
        # Filtramos solo las líneas que empiezan por número (1 a 495) y contienen "3"
        if len(partes) >= 9 and partes[0].isdigit() and partes[1].startswith("3"):
            terceros = [p.replace("3", "") for p in partes[1:9]]
            clave = "".join(sorted(terceros)) # Ej: "EFGHIJKL"
            matriz[clave] = {
                "1A": terceros[0], "1B": terceros[1], "1D": terceros[2], 
                "1E": terceros[3], "1G": terceros[4], "1I": terceros[5], 
                "1K": terceros[6], "1L": terceros[7]
            }
    return matriz

# Creamos el diccionario ultra-rápido al iniciar la app
MATRIZ_TERCEROS = generar_matriz_terceros(TEXTO_FIFA_TERCEROS)

NIVEL_EQUIPOS = {
    # Nivel 1 - Favoritos
    "Argentina": 1,
    "Francia": 1,
    "España": 1,

    # Nivel 2 - Aspirantes
    "Brasil": 2,
    "Inglaterra": 2,
    "Portugal": 2,
    "Alemania": 2,
    "Países Bajos": 2,

    # Nivel 3 - Muy competitivos
    "Uruguay": 3,
    "Croacia": 3,
    "Colombia": 3,
    "Marruecos": 3,
    "Bélgica": 3,
    "Japón": 3,

    # Nivel 4 - Equipos peligrosos
    "Suiza": 4,
    "México": 4,
    "Estados Unidos": 4,
    "Senegal": 4,
    "Corea del Sur": 4,
    "República Checa": 4,
    "Turquía": 4,
    "Suecia": 4,
    "Austria": 4,
    "Ecuador": 4,
    "Noruega": 4,

    # Nivel 5 - Clase media
    "Canadá": 5,
    "Paraguay": 5,
    "Australia": 5,
    "Costa de Marfil": 5,
    "Argelia": 5,
    "Egipto": 5,
    "Irán": 5,
    "Ghana": 5,
    "Bosnia Herzegovina": 5,
    "Escocia": 5,
    "Cabo Verde": 5,
    "Arabia Saudí": 5,
    "Uzbekistán": 5,
    "Panamá": 5,

    # Nivel 6 - Outsiders
    "Sudáfrica": 6,
    "Qatar": 6,
    "Haití": 6,
    "Curaçao": 6,
    "Túnez": 6,
    "Iraq": 6,
    "Nueva Zelanda": 6,
    "Jordania": 6,
    "Congo": 6
}


CONTINENTES = {
    "Francia": "UEFA", "España": "UEFA", "Inglaterra": "UEFA", "Alemania": "UEFA", "Países Bajos": "UEFA",
    "Portugal": "UEFA", "Croacia": "UEFA", "Bélgica": "UEFA", "Suiza": "UEFA", "República Checa": "UEFA",
    "Turquía": "UEFA", "Suecia": "UEFA", "Austria": "UEFA", "Bosnia Herzegovina": "UEFA", "Escocia": "UEFA",
    "Argentina": "CONMEBOL", "Brasil": "CONMEBOL", "Uruguay": "CONMEBOL", "Colombia": "CONMEBOL", 
    "Ecuador": "CONMEBOL", "Paraguay": "CONMEBOL",
    "México": "CONCACAF", "Estados Unidos": "CONCACAF", "Canadá": "CONCACAF", "Panamá": "CONCACAF", 
    "Haití": "CONCACAF", "Curaçao": "CONCACAF",
    "Marruecos": "CAF", "Senegal": "CAF", "Costa de Marfil": "CAF", "Argelia": "CAF", "Egipto": "CAF", 
    "Ghana": "CAF", "Sudáfrica": "CAF", "Cabo Verde": "CAF", "Congo": "CAF", "Túnez": "CAF",
    "Japón": "AFC", "Corea del Sur": "AFC", "Irán": "AFC", "Arabia Saudí": "AFC", "Qatar": "AFC", 
    "Iraq": "AFC", "Uzbekistán": "AFC", "Jordania": "AFC",
    "Australia": "AFC", "Nueva Zelanda": "OFC"
}

COLORES_BANDERAS = {
    "México": ["#006847", "#CE1126"], "Sudáfrica": ["#007A4D", "#FFCD00"], 
    "Corea del Sur": ["#CD2E3A", "#0047A0"], "República Checa": ["#D7141A", "#11457E"],
    "Canadá": ["#FF0000", "#FFFFFF"], "Bosnia Herzegovina": ["#002395", "#FECB00"], 
    "Qatar": ["#8D1B3D", "#FFFFFF"], "Suiza": ["#FF0000", "#FFFFFF"],
    "Brasil": ["#009739", "#FEDD00"], "Marruecos": ["#C1272D", "#006233"], 
    "Haití": ["#00209F", "#D21034"], "Escocia": ["#0065BF", "#FFFFFF"],
    "Estados Unidos": ["#B22234", "#3C3B6E"], "Paraguay": ["#D52B1E", "#0038A8"], 
    "Australia": ["#00008B", "#FF0000"], "Turquía": ["#E30A17", "#FFFFFF"],
    "Alemania": ["#000000", "#FFCE00"], "Curaçao": ["#002B7F", "#F9E814"], 
    "Costa de Marfil": ["#FF8200", "#009E60"], "Ecuador": ["#FFDD00", "#0046AE"],
    "Países Bajos": ["#AE1C28", "#21468B"], "Japón": ["#BC002D", "#FFFFFF"], 
    "Suecia": ["#006AA7", "#FECC00"], "Túnez": ["#E70013", "#FFFFFF"],
    "España": ["#AA151B", "#F1BF00"], "Cabo Verde": ["#003893", "#FFD700"], 
    "Arabia Saudí": ["#006C35", "#FFFFFF"], "Uruguay": ["#0038A8", "#FFFFFF"],
    "Bélgica": ["#000000", "#FFD935"], "Egipto": ["#CE1126", "#000000"], 
    "Irán": ["#239F40", "#DA0000"], "Nueva Zelanda": ["#00247D", "#FFFFFF"],
    "Francia": ["#002395", "#ED2939"], "Senegal": ["#00853F", "#E31B23"], 
    "Iraq": ["#CE1126", "#007A3D"], "Noruega": ["#BA0C2F", "#00205B"],
    "Argentina": ["#74ACDF", "#FFFFFF"], "Argelia": ["#006233", "#D21034"], 
    "Austria": ["#ED2939", "#FFFFFF"], "Jordania": ["#000000", "#CE1126"],
    "Portugal": ["#FF0000", "#006600"], "Congo": ["#002B7F", "#F7D117"], 
    "Uzbekistán": ["#0099B5", "#1EB53A"], "Colombia": ["#FCD116", "#003893"],
    "Inglaterra": ["#CE1126", "#FFFFFF"], "Croacia": ["#FF0000", "#171796"], 
    "Ghana": ["#EF3340", "#FFCD00"], "Panamá": ["#DA121A", "#072357"]
}

GRUPOS_2026 = {
    "Grupo A": ["México", "Sudáfrica", "Corea del Sur", "República Checa"],
    "Grupo B": ["Canadá", "Bosnia Herzegovina", "Qatar", "Suiza"],
    "Grupo C": ["Brasil", "Marruecos", "Haití", "Escocia"],
    "Grupo D": ["Estados Unidos", "Paraguay", "Australia", "Turquía"],
    "Grupo E": ["Alemania", "Curaçao", "Costa de Marfil", "Ecuador"],
    "Grupo F": ["Países Bajos", "Japón", "Suecia", "Túnez"],
    "Grupo G": ["Bélgica", "Egipto", "Irán", "Nueva Zelanda"],
    "Grupo H": ["España", "Cabo Verde", "Arabia Saudí", "Uruguay"],
    "Grupo I": ["Francia", "Senegal", "Iraq", "Noruega"],
    "Grupo J": ["Argentina", "Argelia", "Austria", "Jordania"],
    "Grupo K": ["Portugal", "Congo", "Uzbekistán", "Colombia"],
    "Grupo L": ["Inglaterra", "Croacia", "Ghana", "Panamá"]
}

JORNADAS = {
    "Jornada 1": [
        ("México", "Sudáfrica"), ("Corea del Sur", "República Checa"),
        ("Canadá", "Bosnia Herzegovina"), ("Estados Unidos", "Paraguay"),
        ("Qatar", "Suiza"), ("Brasil", "Marruecos"),
        ("Haití", "Escocia"), ("Australia", "Turquía"),
        ("Alemania", "Curaçao"), ("Países Bajos", "Japón"),
        ("Costa de Marfil", "Ecuador"), ("Suecia", "Túnez"),
        ("España", "Cabo Verde"), ("Bélgica", "Egipto"),
        ("Arabia Saudí", "Uruguay"), ("Irán", "Nueva Zelanda"),
        ("Francia", "Senegal"), ("Iraq", "Noruega"),
        ("Argentina", "Argelia"), ("Austria", "Jordania"),
        ("Portugal", "Congo"), ("Inglaterra", "Croacia"),
        ("Ghana", "Panamá"), ("Uzbekistán", "Colombia")
    ],
    "Jornada 2": [
        ("República Checa", "Sudáfrica"), ("Suiza", "Bosnia Herzegovina"),
        ("Canadá", "Qatar"), ("México", "Corea del Sur"),
        ("Estados Unidos", "Australia"), ("Escocia", "Marruecos"),
        ("Brasil", "Haití"), ("Turquía", "Paraguay"),
        ("Países Bajos", "Suecia"), ("Alemania", "Costa de Marfil"),
        ("Ecuador", "Curaçao"), ("Túnez", "Japón"),
        ("España", "Arabia Saudí"), ("Bélgica", "Irán"),
        ("Uruguay", "Cabo Verde"), ("Nueva Zelanda", "Egipto"),
        ("Argentina", "Austria"), ("Francia", "Iraq"),
        ("Noruega", "Senegal"), ("Jordania", "Argelia"),
        ("Portugal", "Uzbekistán"), ("Inglaterra", "Ghana"),
        ("Panamá", "Croacia"), ("Colombia", "Congo")
    ],
    "Jornada 3": [
        ("Bosnia Herzegovina", "Qatar"), ("Suiza", "Canadá"),
        ("Marruecos", "Haití"), ("Escocia", "Brasil"),
        ("República Checa", "México"), ("Sudáfrica", "Corea del Sur"),
        ("Curaçao", "Costa de Marfil"), ("Ecuador", "Alemania"),
        ("Japón", "Suecia"), ("Túnez", "Países Bajos"),
        ("Paraguay", "Australia"), ("Turquía", "Estados Unidos"),
        ("Noruega", "Francia"), ("Senegal", "Iraq"),
        ("Cabo Verde", "Arabia Saudí"), ("Uruguay", "España"),
        ("Egipto", "Irán"), ("Nueva Zelanda", "Bélgica"),
        ("Croacia", "Ghana"), ("Panamá", "Inglaterra"),
        ("Colombia", "Portugal"), ("Congo", "Uzbekistán"),
        ("Argelia", "Austria"), ("Jordania", "Argentina")
    ]}

LOGOS = {
    # Grupo A
    "México": f"{LOGOS_DIR}mexico.png", "Sudáfrica": f"{LOGOS_DIR}sudafrica.png", 
    "Corea del Sur": f"{LOGOS_DIR}corea.png", "República Checa": f"{LOGOS_DIR}chequia.png",
    
    # Grupo B
    "Canadá": f"{LOGOS_DIR}canada.png", "Bosnia Herzegovina": f"{LOGOS_DIR}bosnia.png", 
    "Qatar": f"{LOGOS_DIR}qatar.png", "Suiza": f"{LOGOS_DIR}suiza.png",
    
    # Grupo C
    "Brasil": f"{LOGOS_DIR}brasil.png", "Marruecos": f"{LOGOS_DIR}marruecos.png", 
    "Haití": f"{LOGOS_DIR}haiti.png", "Escocia": f"{LOGOS_DIR}escocia.png",
    
    # Grupo D
    "Estados Unidos": f"{LOGOS_DIR}eeuu.png", "Paraguay": f"{LOGOS_DIR}paraguay.png", 
    "Australia": f"{LOGOS_DIR}australia.png", "Turquía": f"{LOGOS_DIR}turquia.png",
    
    # Grupo E
    "Alemania": f"{LOGOS_DIR}alemania.png", "Curaçao": f"{LOGOS_DIR}curazao.png", 
    "Costa de Marfil": f"{LOGOS_DIR}costa.png", "Ecuador": f"{LOGOS_DIR}ecuador.png",
    
    # Grupo F
    "Países Bajos": f"{LOGOS_DIR}holanda.png", "Japón": f"{LOGOS_DIR}japon.png", 
    "Suecia": f"{LOGOS_DIR}suecia.png", "Túnez": f"{LOGOS_DIR}tunez.png",
    
    # Grupo G
    "Bélgica": f"{LOGOS_DIR}belgica.png", "Egipto": f"{LOGOS_DIR}egipto.png", 
    "Irán": f"{LOGOS_DIR}iran.png", "Nueva Zelanda": f"{LOGOS_DIR}zelanda.png",
    
    # Grupo H
    "España": f"{LOGOS_DIR}españa.png", "Cabo Verde": f"{LOGOS_DIR}cabo.png", 
    "Arabia Saudí": f"{LOGOS_DIR}arabia.png", "Uruguay": f"{LOGOS_DIR}uruguay.png",
    
    # Grupo I
    "Francia": f"{LOGOS_DIR}francia.png", "Senegal": f"{LOGOS_DIR}senegal.png", 
    "Iraq": f"{LOGOS_DIR}irak.png", "Noruega": f"{LOGOS_DIR}noruega.png",
    
    # Grupo J
    "Argentina": f"{LOGOS_DIR}argentina.png", "Argelia": f"{LOGOS_DIR}argelia.png", 
    "Austria": f"{LOGOS_DIR}austria.png", "Jordania": f"{LOGOS_DIR}jordania.png",
    
    # Grupo K
    "Portugal": f"{LOGOS_DIR}portugal.png", "Congo": f"{LOGOS_DIR}congo.png", 
    "Uzbekistán": f"{LOGOS_DIR}uzbekistan.png", "Colombia": f"{LOGOS_DIR}colombia.png",
    
    # Grupo L
    "Inglaterra": f"{LOGOS_DIR}inglaterra.png", "Croacia": f"{LOGOS_DIR}croacia.png", 
    "Ghana": f"{LOGOS_DIR}ghana.png", "Panamá": f"{LOGOS_DIR}panama.png",
}
SCORING_WC = {
    "Normal": {"signo": 0.5, "diff": 0.75, "exacto": 1.0, "pasa": 0.5},
    "Esquizo": {"signo": 1.0, "diff": 1.5, "exacto": 3.0, "pasa": 1.0}
}

# --- FRASES MÍTICAS ---
FRASES_POR_PUESTO = {
    1: [
        ("Ganar, ganar y volver a ganar.", "Luis Aragonés"),
        ("Siuuuuu.", "CR7"),
        ("Ganar no es lo más importante, es lo único.", "Luis Aragonés"),
        ("Los segundos son los primeros de los perdedores.", "Ayrton Senna"),
        ("El éxito es la suma de pequeños esfuerzos repetidos cada día.", "Anónimo"),
        ("Somos los mejores.", "Pep Guardiola"),
        ("El trabajo da sus frutos.", "Carlo Ancelotti"),
        ("Mentalidad ganadora.", "Cristiano Ronaldo"),
        ("El campeón se levanta siempre.", "Anónimo"),
        ("Nada supera a la victoria.", "Anónimo"),
        ("Objetivo cumplido.", "Anónimo"),
        ("Esto es para la historia.", "Anónimo"),
        ("Nacidos para ganar.", "Anónimo"),
        ("Arriba del todo.", "Anónimo"),
        ("La cima es nuestra.", "Anónimo")
    ],

    2: [
        ("Perder una final es lo peor.", "Messi"),
        ("Lo intentamos.", "Sergio Ramos"),
        ("Estuvimos cerca.", "Anónimo"),
        ("Duele, pero volveremos.", "Anónimo"),
        ("Caer está permitido, levantarse es obligatorio.", "Anónimo"),
        ("Nos faltó muy poco.", "Anónimo"),
        ("Aprendemos de las derrotas.", "Anónimo"),
        ("El próximo será nuestro.", "Anónimo"),
        ("Orgullosos del equipo.", "Anónimo"),
        ("No fue suficiente.", "Anónimo"),
        ("Rozando la gloria.", "Anónimo"),
        ("Competimos hasta el final.", "Anónimo"),
        ("Subcampeones con honor.", "Anónimo"),
        ("Volveremos más fuertes.", "Anónimo"),
        ("A un paso del sueño.", "Anónimo")
    ],

    3: [
        ("Partido a partido.", "Simeone"),
        ("Ni tan mal.", "Anónimo"),
        ("El podio siempre es buen lugar.", "Anónimo"),
        ("Sumar siempre es importante.", "Anónimo"),
        ("Objetivo cumplido a medias.", "Anónimo"),
        ("Regularidad ante todo.", "Anónimo"),
        ("Constancia y trabajo.", "Anónimo"),
        ("Paso firme.", "Anónimo"),
        ("Siempre competitivos.", "Anónimo"),
        ("Temporada sólida.", "Anónimo"),
        ("Ahí estamos.", "Anónimo"),
        ("En la pelea.", "Anónimo"),
        ("Trabajo silencioso.", "Anónimo"),
        ("Punto a punto.", "Anónimo"),
        ("Ni arriba ni abajo.", "Anónimo")
    ],

    4: [
        ("El fútbol es así.", "Boskov"),
        ("Hay que seguir.", "Ancelotti"),
        ("Nos faltó ese último paso.", "Anónimo"),
        ("Morir en la orilla.", "Anónimo"),
        ("A las puertas de todo.", "Anónimo"),
        ("Casi, pero no.", "Anónimo"),
        ("Nos quedamos ahí.", "Anónimo"),
        ("Buen intento.", "Anónimo"),
        ("Detalles que marcan diferencias.", "Anónimo"),
        ("Aprender y mejorar.", "Anónimo"),
        ("El año que viene más.", "Anónimo"),
        ("Competimos bien.", "Anónimo"),
        ("No alcanzó.", "Anónimo"),
        ("Todo suma.", "Anónimo"),
        ("Seguimos creciendo.", "Anónimo")
    ],

    5: [
        ("¿Por qué?", "Mourinho"),
        ("Fútbol es fútbol.", "Boskov"),
        ("A veces se gana, a veces se aprende.", "Anónimo"),
        ("Temporada irregular.", "Anónimo"),
        ("Podría haber sido peor.", "Anónimo"),
        ("Ni frío ni calor.", "Anónimo"),
        ("En tierra de nadie.", "Anónimo"),
        ("Sin pena ni gloria.", "Anónimo"),
        ("Mucho que mejorar.", "Anónimo"),
        ("Hay margen.", "Anónimo"),
        ("Esto es largo.", "Anónimo"),
        ("No era el plan.", "Anónimo"),
        ("Toca reflexionar.", "Anónimo"),
        ("Nada decidido.", "Anónimo"),
        ("Seguimos vivos.", "Anónimo")
    ],

    6: [
        ("Ni fu ni fa.", "La grada"),
        ("Dominamos en posesión moral.", "La Sotana vibes"),
        ("Prometía mucho en pretemporada.", "La Sotana vibes"),
        ("Aspirábamos a más, conseguimos menos.", "La grada"),
        ("Objetivo: no hacer el ridículo.", "La grada"),
        ("El míster vende humo, nosotros compramos.", "La Sotana vibes"),
        ("Salvamos los muebles, pero la casa se quema.", "La Sotana vibes"),
        ("La prensa dice que jugamos bien. Mentira.", "La grada"),
        ("Un punto que sabe a absolutamente nada.", "La Sotana vibes"),
        ("Estancados en la mediocridad premium.", "La Sotana vibes"),
        ("Empate técnico entre las ganas de jugar y las de irse de fiesta.", "La Sotana vibes"),
        ("Un partido serio... durante 7 minutos.", "La Sotana vibes"),
        ("Clasificación engañosa (para mal).", "La Sotana vibes"),
        ("Competimos... a nuestra manera.", "La grada"),
        ("Nos faltó todo.", "La Sotana vibes")
    ],

    7: [
        ("Prefiero no hablar.", "Mourinho"),
        ("Hay que levantarse.", "CR7"),
        ("Momento complicado.", "Anónimo"),
        ("Esto no ha terminado.", "Anónimo"),
        ("Toca sufrir.", "Anónimo"),
        ("Hay que apretar los dientes.", "Anónimo"),
        ("Salir del bache.", "Anónimo"),
        ("Unidos saldremos.", "Anónimo"),
        ("Trabajo y más trabajo.", "Anónimo"),
        ("Remar contra corriente.", "Anónimo"),
        ("No bajamos los brazos.", "Anónimo"),
        ("Pelear hasta el final.", "Anónimo"),
        ("Esto se levanta.", "Anónimo"),
        ("Día duro.", "Anónimo"),
        ("Paso atrás.", "Anónimo")
    ],

    8: [
        ("Defendemos con la mirada.", "La Sotana vibes"),
        ("El rival parecía el Brasil del 70.", "La Sotana vibes"),
        ("Proyecto ilusionante (para el rival).", "La grada"),
        ("Nos remontan hasta en el FIFA.", "La Sotana vibes"),
        ("Más blandos que el pan de molde.", "La Sotana vibes"),
        ("El VAR tampoco nos salva.", "La grada"),
        ("Estamos probando cosas (ninguna funciona).", "La Sotana vibes"),
        ("Entrenamos sin balón, se nota.", "La Sotana vibes"),
        ("Nuestro objetivo es participar.", "La grada"),
        ("Temporada histórica... para olvidar.", "La Sotana vibes"),
        ("El descenso nos guiña el ojo.", "La Sotana vibes"),
        ("Jugamos a sorprender… y lo logramos.", "La grada"),
        ("El míster tiene un plan (nadie sabe cuál).", "La Sotana vibes"),
        ("Somos un meme con patas.", "Twitter futbolero"),
        ("Menos fútbol que una tarde en el Ikea.", "La Sotana vibes")
    ],

    9: [
        ("Estamos en la UVI.", "Clemente"),
        ("Salimos como nunca...", "Di Stéfano"),
        ("Tocar fondo para impulsarse.", "Anónimo"),
        ("Situación crítica.", "Anónimo"),
        ("Hora de reaccionar.", "Anónimo"),
        ("No queda margen.", "Anónimo"),
        ("Sufrir para sobrevivir.", "Anónimo"),
        ("Cada punto es oro.", "Anónimo"),
        ("Final tras final.", "Anónimo"),
        ("Salvar la categoría.", "Anónimo"),
        ("Resistir es ganar.", "Anónimo"),
        ("Con el agua al cuello.", "Anónimo"),
        ("Última bala.", "Anónimo"),
        ("Orgullo y corazón.", "Anónimo"),
        ("Nunca rendirse.", "Anónimo")
    ],

    10: [
        ("Salimos como nunca perdemos como siempre", "Di Stéfano"),
        ("Descenso speedrun any%.", "La Sotana vibes"),
        ("El Titanic tenía mejor planificación.", "La Sotana vibes"),
        ("Nos pitan y no sabemos si es penalti o final.", "La grada"),
        ("Somos el sparring oficial de la liga.", "La Sotana vibes"),
        ("Cada jornada, un trauma nuevo.", "La Sotana vibes"),
        ("El calendario pide perdón.", "La grada"),
        ("Defensa de mantequilla.", "La Sotana vibes"),
        ("Tenemos más excusas que puntos.", "La Sotana vibes"),
        ("Modo supervivencia activado.", "La grada"),
        ("Esto ya es contenido.", "La Sotana vibes"),
        ("El descenso no es amenaza, es destino.", "La Sotana vibes"),
        ("Jugamos sin red.", "La grada"),
        ("La clasificación no miente (ojalá lo hiciera).", "La Sotana vibes"),
        ("Directos a la bancarrota moral.", "La Sotana vibes")
    ]
}

LOGROS_DATA = {
    "guru": {"icon": "🔮", "name": "El Gurú", "desc": "Pleno en Esquizo."},
    "cima": {"icon": "🏔️", "name": "En la Cima", "desc": "Líder general."},
    "pleno": {"icon": "💯", "name": "Pleno", "desc": "Puntuado en los 10."}
}

# Colores de bandera para el anillo dinámico
# Formato: "Selección": [Color1, Color2]
COLORES_BANDERAS = {
    "España": ["#FF0000", "#FFFF00"],      # Rojo y Amarillo
    "Argentina": ["#74ACDF", "#FFFFFF"],   # Celeste y Blanco
    "México": ["#006847", "#CE1126"],      # Verde y Rojo
    "Brasil": ["#009739", "#FEDD00"],      # Verde y Amarillo
    "Francia": ["#002395", "#ED2939"],     # Azul y Rojo
    # ... seguiremos con las demás
}

# Diccionario para las Stats por continente

# --- 2. FUNCIONES DE APOYO ---
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=10)
def leer_datos(pestaña):
    try:
        # Tu ID de hoja actual
        # 1. El ID que sacamos de tu enlace
        sheet_id = "1TL2MTxCixfAKs_3EuhVc0ENZSWub3lF7LBey3BT62-A"       
        # 2. La URL formateada para descargar cada pestaña como CSV
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={pestaña}"
        df = pd.read_csv(url)
        
        if not df.empty:
            # 1. Blindaje de Usuario: Siempre a texto para evitar errores con nombres numéricos
            if 'Usuario' in df.columns:
                df['Usuario'] = df['Usuario'].astype(str)
            
            # 2. Blindaje de Puntos: Aseguramos que sean números por si hay comas en el Excel
            columnas_numericas = ['P_L', 'P_V', 'R_L', 'R_V', 'Puntos']
            for col in columnas_numericas:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)
            if 'Ojo_con' in df.columns:
                df['Ojo_con'] = df['Ojo_con'].astype(str).replace(['nan', 'NaN', 'None'], 'Ninguno').fillna('Ninguno')
            
         # 3. Normalización de Prórroga (Opcional pero recomendado para tu nueva lógica)
            if 'Hubo_Prorroga' in df.columns:
                df['Hubo_Prorroga'] = df['Hubo_Prorroga'].astype(str).str.upper().str.strip()

        return df
    except Exception as e:
        # En caso de error, devolvemos un DataFrame vacío para que la App no "pete"
        return pd.DataFrame()

def safe_float(valor):
    try:
        if pd.isna(valor) or str(valor).strip() == "": return 0.0
        return float(str(valor).replace(',', '.'))
    except: return 0.0

def get_logo(equipo):
    path = LOGOS.get(equipo)
    if path and os.path.exists(path): return path
    return None

def calcular_puntos_wc(p_l, p_v, r_l, r_v, tipo_partido, p_pasa=None, r_pasa=None, hubo_prorroga=False):
    # 1. ESCUDO: Forzamos a que todo sea número. Si hay un nulo o texto, devolvemos 0.
    try:
        p_l = int(float(p_l))
        p_v = int(float(p_v))
        r_l = int(float(r_l))
        r_v = int(float(r_v))
    except (ValueError, TypeError):
        return 0.0

    puntos_base = 0.0
    
    # 2. Lógica de Puntos Base (Marcador a los 90')
    signo_p = (p_l > p_v) - (p_l < p_v)
    signo_r = (r_l > r_v) - (r_l < r_v)
    
    if p_l == r_l and p_v == r_v:
    puntos += 1.0  # Pleno
    elif signo_p == signo_r:
        if signo_p != 0 and (p_l - p_v == r_l - r_v):
            puntos += 0.75 # Diferencia
        else:
            puntos += 0.5  # Signo
            
    # 3. Lógica para partidos de Eliminatoria (Quien pasa de ronda)
    puntos_pasa = 0.0
    if tipo_partido in ["Octavos", "Cuartos", "Semis", "Final"] or hubo_prorroga:
        if p_pasa and r_pasa and p_pasa != "Ninguno" and r_pasa != "Ninguno":
            if p_pasa == r_pasa:
                puntos_pasa += 0.5

    # 4. 🔥 APLICACIÓN DE MULTIPLICADORES DINÁMICOS
    # Si quieres que sea TRIPLE (como dice tu texto de apuestas), multiplicamos por 3.
    # Si prefieres el doble, cambia el 3.0 por 2.0 y el 2.0 por 1.5.
    if tipo_partido == "Esquizo":
        total_puntos = (puntos_base * 3.0) + (puntos_pasa * 2.0) # El bonus de pasar pasa de 0.5 a 1.0
    elif tipo_partido == "Doble":
        total_puntos = (puntos_base * 2.0) + puntos_pasa
    else:
        total_puntos = puntos_base + puntos_pasa
                
    return total_puntos

def calcular_puntos_bracket(user_bracket, real_bracket):
    """
    Sistema Híbrido: Puntos por avance de equipo (escalado) + Bonus por partido exacto.
    """
    pts = 0.0
    if user_bracket is None or real_bracket is None: return 0.0

    # 1. FASE DE GRUPOS (0.5 pts)
    for g in ["Grupo A", "Grupo B", "Grupo C", "Grupo D", "Grupo E", "Grupo F", 
              "Grupo G", "Grupo H", "Grupo I", "Grupo J", "Grupo K", "Grupo L"]:
        if user_bracket.get(f"{g}_1") == real_bracket.get(f"{g}_1") and pd.notna(real_bracket.get(f"{g}_1")): pts += 0.5
        if user_bracket.get(f"{g}_2") == real_bracket.get(f"{g}_2") and pd.notna(real_bracket.get(f"{g}_2")): pts += 0.5

    # Los 8 Mejores Terceros (0.5 pts)
    u_terceros = set(str(user_bracket.get("MejoresTerceros", "")).split(","))
    r_terceros = set(str(real_bracket.get("MejoresTerceros", "")).split(","))
    u_terceros.discard(""); r_terceros.discard("")
    pts += len(u_terceros.intersection(r_terceros)) * 0.5

    # 2. AVANCE DE EQUIPOS (ESCALADO: 0.5 -> 1.0 -> 1.5 -> 2.0)
    r_octavos = [real_bracket.get(f"W16_{i}") for i in range(16) if pd.notna(real_bracket.get(f"W16_{i}"))]
    r_cuartos = [real_bracket.get(f"W8_{i}") for i in range(8) if pd.notna(real_bracket.get(f"W8_{i}"))]
    r_semis = [real_bracket.get(f"W4_{i}") for i in range(4) if pd.notna(real_bracket.get(f"W4_{i}"))]
    r_final = [real_bracket.get(f"WS_{i}") for i in range(2) if pd.notna(real_bracket.get(f"WS_{i}"))]
    r_campeon = real_bracket.get("Campeon")

    for eq in set([user_bracket.get(f"W16_{i}") for i in range(16)]):
        if eq in r_octavos and eq is not None: pts += 0.5  
    for eq in set([user_bracket.get(f"W8_{i}") for i in range(8)]):
        if eq in r_cuartos and eq is not None: pts += 1.0  
    for eq in set([user_bracket.get(f"W4_{i}") for i in range(4)]):
        if eq in r_semis and eq is not None: pts += 1.5  
    for eq in set([user_bracket.get(f"WS_{i}") for i in range(2)]):
        if eq in r_final and eq is not None: pts += 2.0  
        
    if user_bracket.get("Campeon") == r_campeon and r_campeon is not None:
        pts += 4.0  # Campeón del Mundo

    # 3. CRUCES EXACTOS (Bonus extra)
    def cruce_exacto(u1, u2, list_r_matches):
        if not u1 or not u2: return False
        return any(set([u1, u2]) == set([r1, r2]) for r1, r2 in list_r_matches)

    r_matches_8vos = [(real_bracket.get(f"W16_{i*2}"), real_bracket.get(f"W16_{i*2+1}")) for i in range(8)]
    r_matches_4tos = [(real_bracket.get(f"W8_{i*2}"), real_bracket.get(f"W8_{i*2+1}")) for i in range(4)]
    r_matches_semis = [(real_bracket.get(f"W4_{i*2}"), real_bracket.get(f"W4_{i*2+1}")) for i in range(2)]
    r_matches_final = [(real_bracket.get("WS_0"), real_bracket.get("WS_1"))]

    for i in range(8):
        if cruce_exacto(user_bracket.get(f"W16_{i*2}"), user_bracket.get(f"W16_{i*2+1}"), r_matches_8vos): pts += 0.5
    for i in range(4):
        if cruce_exacto(user_bracket.get(f"W8_{i*2}"), user_bracket.get(f"W8_{i*2+1}"), r_matches_4tos): pts += 1.0
    for i in range(2):
        if cruce_exacto(user_bracket.get(f"W4_{i*2}"), user_bracket.get(f"W4_{i*2+1}"), r_matches_semis): pts += 1.0
    if cruce_exacto(user_bracket.get("WS_0"), user_bracket.get("WS_1"), r_matches_final): pts += 2.0

    return pts

def simular_temporada_completa(df_hero, df_p_all, df_r_all, df_b_all):
    """
    Simulación de Montecarlo Ultra-PRO: Proyecta el final de la porra 5.000 veces.
    Analiza el Bracket completo de cada usuario casilla por casilla y estima
    dinámicamente sus puntos futuros ponderando cada elección según el NIVEL_EQUIPOS.
    """
    usuarios = df_hero['Usuario'].tolist()
    puntos_actuales = df_hero.set_index('Usuario')['Puntos'].to_dict()
    
    # 1. Identificar partidos diarios pendientes
    pendientes = df_r_all[df_r_all['Finalizado'] == "NO"]
    num_pend_normal = len(pendientes[pendientes['Tipo'] != "Esquizo"])
    num_pend_esquizo = len(pendientes[pendientes['Tipo'] == "Esquizo"])
    
    # 2. Rescatar Bracket del ADMIN (Para saber qué parte del torneo ya es real)
    admin_b = df_b_all[df_b_all['Usuario'].str.upper() == 'ADMIN']
    r_bracket = admin_b.iloc[0] if not admin_b.empty else None
    
    # 3. PRE-PROCESAMIENTO: Calcular el "Score de Calidad y Probabilidad" del Bracket de cada usuario
    # Evaluamos qué tan viable es el mapa del torneo de cada porrista
    probabilidad_bracket_usuario = {}
    
    for u in usuarios:
        u_bracket_row = df_b_all[df_b_all['Usuario'] == u]
        if u_bracket_row.empty:
            probabilidad_bracket_usuario[u] = 0.0
            continue
            
        u_bracket = u_bracket_row.iloc[0]
        score_fase_grupos = 0.0
        score_eliminatorias = 0.0
        
        # A) Evaluar Fase de Grupos (Clasificados 1º y 2º)
        for g in ["Grupo A", "Grupo B", "Grupo C", "Grupo D", "Grupo E", "Grupo F", 
                  "Grupo G", "Grupo H", "Grupo I", "Grupo J", "Grupo K", "Grupo L"]:
            eq1 = u_bracket.get(f"{g}_1")
            eq2 = u_bracket.get(f"{g}_2")
            
            # Un equipo Nivel 1 tiene 85% de probabilidad de pasar. Un Nivel 5 un 20%.
            if eq1 in NIVEL_EQUIPOS: score_fase_grupos += max(0.2, 1.0 - (NIVEL_EQUIPOS[eq1] - 1) * 0.16) * 0.5
            if eq2 in NIVEL_EQUIPOS: score_fase_grupos += max(0.2, 1.0 - (NIVEL_EQUIPOS[eq2] - 1) * 0.16) * 0.5
            
        # B) Evaluar Supervivencia en Rondas de Eliminación Directa
        # Octavos (W16)
        for i in range(16):
            eq = u_bracket.get(f"W16_{i}")
            if eq in NIVEL_EQUIPOS: score_eliminatorias += max(0.15, 1.0 - (NIVEL_EQUIPOS[eq] - 1) * 0.20) * 0.5
        # Cuartos (W8)
        for i in range(8):
            eq = u_bracket.get(f"W8_{i}")
            if eq in NIVEL_EQUIPOS: score_eliminatorias += max(0.10, 1.0 - (NIVEL_EQUIPOS[eq] - 1) * 0.22) * 1.0
        # Semis (W4)
        for i in range(4):
            eq = u_bracket.get(f"W4_{i}")
            if eq in NIVEL_EQUIPOS: score_eliminatorias += max(0.05, 1.0 - (NIVEL_EQUIPOS[eq] - 1) * 0.24) * 1.5
        # Finalistas (WS)
        for i in range(2):
            eq = u_bracket.get(f"WS_{i}")
            if eq in NIVEL_EQUIPOS: score_eliminatorias += max(0.05, 1.0 - (NIVEL_EQUIPOS[eq] - 1) * 0.24) * 2.0
            
        # Campeón del Mundo
        camp = u_bracket.get("Campeon")
        if camp in NIVEL_EQUIPOS:
            score_eliminatorias += max(0.02, 1.0 - (NIVEL_EQUIPOS[camp] - 1) * 0.24) * 4.0
            
        # Puntuación potencial total estimada del cuadro del usuario
        probabilidad_bracket_usuario[u] = score_fase_grupos + score_eliminatorias

    # 4. Calcular el "ADN de acierto" diario de cada porrista
    perfil_usuario = {}
    df_terminados = df_r_all[df_r_all['Finalizado'] == "SI"]
    
    for u in usuarios:
        u_p = df_p_all[df_p_all['Usuario'] == u]
        m_fin = pd.merge(u_p, df_terminados, on=['Jornada', 'Partido'])
        
        if not m_fin.empty:
            m_fin['Pts'] = m_fin.apply(lambda x: calcular_puntos_wc(
                x.P_L, x.P_V, x.R_L, x.R_V, x.Tipo, 
                getattr(x, 'P_Pasa', None), x.get('R_Pasa'), x.get('Hubo_Prorroga') == "SI"
            ), axis=1)
            
            media_n = m_fin[m_fin['Tipo'] != "Esquizo"]['Pts'].mean() if not m_fin[m_fin['Tipo'] != "Esquizo"].empty else 0.4
            media_e = m_fin[m_fin['Tipo'] == "Esquizo"]['Pts'].mean() if not m_fin[m_fin['Tipo'] == "Esquizo"].empty else 0.8
            desvio = m_fin['Pts'].std() if len(m_fin) > 1 else 0.2
        else:
            media_n, media_e, desvio = 0.45, 1.35, 0.25
            
        perfil_usuario[u] = {'n': media_n, 'e': media_e, 'std': desvio}

    # 5. Ejecución de Montecarlo (5.000 iteraciones)
    conteo_puestos = {u: [0] * len(usuarios) for u in usuarios}
    suma_puestos = {u: 0 for u in usuarios}
    
    # Determinamos cuánto del bracket queda por jugar según los partidos que faltan
    factor_bracket_restante = 1.0 if num_pend_normal > 20 else (num_pend_normal / 48.0)

    for _ in range(5000):
        resultados_iteracion = []
        
        for u in usuarios:
            # A) Simulación de su rendimiento en partidos del día a día
            pts_n = np.random.normal(perfil_usuario[u]['n'], perfil_usuario[u]['std'], num_pend_normal).sum()
            pts_e = np.random.normal(perfil_usuario[u]['e'], perfil_usuario[u]['std'] * 1.5, num_pend_esquizo).sum()
            
            # B) Simulación del Bracket inteligente usando el clasificador de nivel de equipos
            # Introducemos una fluctuación competitiva orgánica (para simular sorpresas del Mundial)
            fluctuacion_mundial = np.random.normal(1.0, 0.12)
            puntos_proyectados_bracket = probabilidad_bracket_usuario[u] * factor_bracket_restante * fluctuacion_mundial
            
            # C) Si el admin ya validó aciertos reales en la hoja, los sumamos limpiamente
            puntos_ya_consolidados_bracket = 0.0
            if r_bracket is not None:
                u_bracket_row = df_b_all[df_b_all['Usuario'] == u]
                if not u_bracket_row.empty:
                    puntos_ya_consolidados_bracket = calcular_puntos_bracket(u_bracket_row.iloc[0], r_bracket)
            
            # Suma final del universo simulado
            total_sim = (puntos_actuales[u] + 
                         max(0, pts_n) + 
                         max(0, pts_e) + 
                         max(0, puntos_proyectados_bracket) - puntos_ya_consolidados_bracket)
            
            resultados_iteracion.append((u, total_sim))
            
        resultados_iteracion.sort(key=lambda x: x[1], reverse=True)
        
        for i, (u, pts) in enumerate(resultados_iteracion):
            conteo_puestos[u][i] += 1
            suma_puestos[u] += (i + 1)

    data_final = []
    for u in usuarios:
        fila = {"Usuario": u}
        fila["Puesto Medio"] = suma_puestos[u] / 5000
        for i in range(len(usuarios)):
            fila[f"P{i+1}"] = (conteo_puestos[u][i] / 5000) * 100
        data_final.append(fila)
        
    return pd.DataFrame(data_final).sort_values("Puesto Medio")



def analizar_adn_pro(usuario, df_p, df_r):
    df_m = pd.merge(df_p[df_p['Usuario'] == usuario], df_r[df_r['Finalizado'] == "SI"], on=['Jornada', 'Partido'])
    if df_m.empty: return None
    df_m['Pts'] = df_m.apply(lambda x: calcular_puntos_wc(x.P_L, x.P_V, x.R_L, x.R_V, x.Tipo), axis=1)
    pts_eq = {}
    for _, r in df_m.iterrows():
        l, v = r['Partido'].split('-')
        pts_eq[l] = pts_eq.get(l, 0) + r['Pts']
        pts_eq[v] = pts_eq.get(v, 0) + r['Pts']
    ex = len(df_m[df_m.apply(lambda x: x.P_L == x.R_L and x.P_V == x.R_V, axis=1)])
    sig = len(df_m[df_m['Pts'] > 0]) - ex
    return {
        "amuleto": max(pts_eq, key=pts_eq.get) if pts_eq else "N/A",
        "bestia": min(pts_eq, key=pts_eq.get) if pts_eq else "N/A",
        "exactos": ex, "signos": sig, "fallos": len(df_m)-(ex+sig),
        "avg_g": (df_m['P_L']+df_m['P_V']).mean(), "real_g": (df_m['R_L']+df_m['R_V']).mean()
    }


@st.cache_data(ttl=60)
def simular_oraculo(usuarios, df_p_all, df_r_all, jornada_sel):
    # 1. Resultados posibles a los 90'
    res_sim = [(0,0), (1,0), (0,1), (1,1), (2,1), (1,2), (2,2), (2,0), (0,2)]
    
    pend = df_r_all[(df_r_all['Jornada'] == jornada_sel) & (df_r_all['Finalizado'] == "NO")]
    if pend.empty or len(pend) > 3: return None
    
    # Identificamos los equipos de cada partido pendiente
    p_id = pend['Partido'].tolist()
    t_id = pend['Tipo'].tolist()
    
    # ¿Es jornada de eliminatorias? (Check simple por nombre de jornada)
    es_ko = any(x in jornada_sel for x in ["Dieciseisavos", "Octavos", "Cuartos", "Semis", "Final"])

    victorias = {u: 0 for u in usuarios}
    
    # Creamos los combos de resultados
    combos = list(itertools.product(res_sim, repeat=len(p_id)))
    
    total_escenarios = 0

    for c in combos:
        # Si es KO, para cada empate en el combo tenemos 2 posibilidades (Pasa A o Pasa B)
        # Para simplificar y no hacer explotar el procesador, simulamos el pase de ronda
        # de forma lógica: si el marcador no es empate, pasa el que ha ganado.
        # Si es empate, simulamos ambos pases.
        
        escenarios_internos = [[]]
        for i, marcador in enumerate(c):
            g_l, g_v = marcador
            loc, vis = p_id[i].split('-')
            
            if es_ko and g_l == g_v:
                # Si es empate en KO, añadimos dos variantes: pasa uno o pasa otro
                nuevos = []
                for esc in escenarios_internos:
                    nuevos.append(esc + [(g_l, g_v, loc, True)]) # Pasa Local
                    nuevos.append(esc + [(g_l, g_v, vis, True)]) # Pasa Visitante
                escenarios_internos = nuevos
            else:
                # Si no es empate o no es KO, el pase es el lógico o no existe
                quien_pasa = loc if g_l > g_v else (vis if g_v > g_l else None)
                for esc in escenarios_internos:
                    esc.append((g_l, g_v, quien_pasa, False))

        for esc_final in escenarios_internos:
            total_escenarios += 1
            puntos_escenario = {u: 0.0 for u in usuarios}
            
            for u in usuarios:
                u_p = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == jornada_sel)]
                
                # Puntos de partidos ya finalizados en la jornada
                fin_j = df_r_all[(df_r_all['Jornada'] == jornada_sel) & (df_r_all['Finalizado'] == "SI")]
                for r_fin in fin_j.itertuples():
                    pred = u_p[u_p['Partido'] == r_fin.Partido]
                    if not pred.empty:
                        # Usamos la nueva función de puntos
                        puntos_escenario[u] += calcular_puntos_wc(
                            pred.iloc[0]['P_L'], pred.iloc[0]['P_V'], 
                            r_fin.R_L, r_fin.R_V, r_fin.Tipo,
                            pred.iloc[0].get('P_Pasa'), r_fin.R_Pasa, 
                            r_fin.Hubo_Prorroga == "SI"
                        )

                # Puntos de partidos simulados
                for i, (sim_l, sim_v, sim_pasa, prorroga) in enumerate(esc_final):
                    pred = u_p[u_p['Partido'] == p_id[i]]
                    if not pred.empty:
                        puntos_escenario[u] += calcular_puntos_wc(
                            pred.iloc[0]['P_L'], pred.iloc[0]['P_V'],
                            sim_l, sim_v, t_id[i],
                            pred.iloc[0].get('P_Pasa'), sim_pasa, prorroga
                        )
            
            # Ganador del escenario
            mx = max(puntos_escenario.values())
            ganadores = [u for u, p in puntos_escenario.items() if p == mx]
            for g in ganadores:
                victorias[g] += 1 / len(ganadores)

    return {u: (v / total_escenarios) * 100 for u, v in victorias.items()}

def get_now_madrid():
    # Definimos la zona horaria de España
    tz = pytz.timezone('Europe/Madrid')
    # Obtenemos la hora actual en esa zona y le quitamos la información de zona 
    # para que sea compatible con las fechas de tu Excel (naive datetime)
    return datetime.datetime.now(tz).replace(tzinfo=None)

# Fecha y hora del partido inaugural (Ejemplo: 11 de Junio a las 21:00)
FECHA_INAUGURAL = datetime.datetime(2026, 6, 11, 21, 0, 0)
mercado_abierto = get_now_madrid() < FECHA_INAUGURAL

# --- 3. APP ---
st.set_page_config(page_title="Porros League 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏆 Mundial Porros League 2026")
        u_in, p_in = st.text_input("Usuario"), st.text_input("Contraseña", type="password")
        c1, c2 = st.columns(2)
        if c1.button("Entrar", use_container_width=True):
            df_u = leer_datos("Usuarios")
            user = df_u[(df_u['Usuario'].astype(str) == u_in) & (df_u['Password'].astype(str) == p_in)]
            if not user.empty:
                st.session_state.autenticado, st.session_state.user, st.session_state.rol = True, u_in, user.iloc[0]['Rol']; st.rerun()
            else: st.error("❌ Credenciales incorrectas")
        if c2.button("Registrarse", use_container_width=True):
            df_u = leer_datos("Usuarios")
            
            # 1. Validaciones previas
            if u_in == "" or p_in == "":
                st.warning("⚠️ No seas 'pechofrío', pon un usuario y contraseña.")
            elif u_in in df_u['Usuario'].values:
                st.error("❌ Este usuario ya está en la convocatoria.")
            else:
                try:
                    # 2. Registro en la pestaña "Usuarios"
                    nueva_cuenta = pd.DataFrame([{"Usuario": u_in, "Password": p_in, "Rol": "user"}])
                    df_u_act = pd.concat([df_u, nueva_cuenta], ignore_index=True)
                    conn.update(worksheet="Usuarios", data=df_u_act)

                    # 3. CREACIÓN DE FILA EN PuntosBase (EL ARREGLO)
                    # Leemos la tabla de puntos actual para no borrar a nadie
                    df_pb_actual = leer_datos("PuntosBase")
                    nueva_fila_puntos = pd.DataFrame([{"Usuario": u_in, "Puntos": 0.0}])
                    df_pb_act = pd.concat([df_pb_actual, nueva_fila_puntos], ignore_index=True)
                    conn.update(worksheet="PuntosBase", data=df_pb_act)

                    # 4. Feedback y limpieza
                    st.success(f"✅ ¡Fichado! {u_in}, ya puedes loguearte.")
                    st.balloons()
                    
                    # Limpiamos caché para que el login reconozca al nuevo usuario inmediatamente
                    st.cache_data.clear()
                    time.sleep(1.5)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error crítico en el registro: {e}")
else:
    # 1. CARGA DE DATOS
    df_perf = leer_datos("ImagenesPerfil")
    # Cargamos también los logs para que ChatG-O-L los vea
    df_r_all, df_p_all, df_u_all, df_base, df_logs_all = leer_datos("Resultados"), leer_datos("Predicciones"), leer_datos("Usuarios"), leer_datos("PuntosBase"), leer_datos("Logs")
    # --- 🛡️ MURO DE SEGURIDAD ACTUALIZADO ---
    # Verificamos si las variables son None (error de carga) o si falta la tabla crítica de Usuarios
    if df_u_all is None or df_u_all.empty:
        st.error("❌ No se pudo cargar la tabla de Usuarios. Revisa la conexión con GSheets.")
        ()
    
    # Si Resultados o Predicciones están vacíos, creamos un DataFrame vacío con sus columnas 
    # para que el resto de la lógica no explote, pero permitimos que la App siga.
    if df_r_all.empty:
        st.warning("⚠️ La tabla de Resultados está vacía. El Admin debe inicializar los partidos.")
        # Opcional: df_r_all = pd.DataFrame(columns=['Jornada', 'Partido', 'R_L', 'R_V', 'Finalizado', 'Tipo', 'Hora_Inicio'])
    
    if df_p_all.empty:
        # Esto es normal si nadie ha apostado aún. No detenemos la app.
        pass
    foto_dict = df_perf.set_index('Usuario')['ImagenPath'].to_dict() if not df_perf.empty else {}
    u_jugadores = [u for u in df_u_all['Usuario'].unique() if u not in df_u_all[df_u_all['Rol']=='admin']['Usuario'].tolist()]

    # --- CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; color: #31333F; }
        .hero-bg { background: #f8f9fa; border-radius: 20px; padding: 25px; margin-bottom: 25px; border: 1px solid #dee2e6; }
        .kpi-box { background: white; border-radius: 12px; padding: 12px; text-align: center; border: 1px solid #eee; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
        .kpi-label { font-size: 0.75em; color: #6c757d; font-weight: bold; text-transform: uppercase; }
        .kpi-value { font-size: 1.6em; font-weight: 800; color: #2baf2b; display: block; }
        .panini-card { background: #f8f9fb; border-radius: 15px; padding: 20px; border: 1px solid #e0e0e0; margin-bottom: 20px; }
        .quote-text { color: #4f4f4f; font-style: italic; border-left: 3px solid #2baf2b; padding-left: 10px; margin: 10px 0; }
        .pos-badge { background-color: #2baf2b; color: white; padding: 5px 15px; border-radius: 50%; font-weight: bold; }
        .match-box { background: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #eee; border-left: 5px solid #2baf2b; margin-bottom: 10px; }
        .crown { font-size: 2em; position: absolute; top: -35px; left: 35px; transform: rotate(-15deg); z-index: 10; }
        .section-tag { font-size: 0.7em; background: #31333F; color: white; padding: 2px 8px; border-radius: 5px; margin-bottom: 5px; display: inline-block; }
        .match-box-locked { background: #e9ecef !important; opacity: 0.8; border-left: 5px solid #6c757d !important; filter: grayscale(0.5); }
        .lock-icon { font-size: 1.2em; cursor: help; }
        /* Estilos para el Podio */
        .podium-1 { background: linear-gradient(135deg, #fffdf0 0%, #fff9c4 100%) !important; border: 2px solid #ffd700 !important; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.2); transform: scale(1.02); }
        .podium-2 { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important; border: 2px solid #c0c0c0 !important; }
        .podium-3 { background: linear-gradient(135deg, #fff5f0 0%, #ffe0cc 100%) !important; border: 2px solid #cd7f32 !important; }
        .medal-icon { font-size: 1.8em; margin-bottom: 5px; display: block; }
        /* Estilos de Zona */
        .zone-champions { border-left: 8px solid #ffd700 !important; background: linear-gradient(90deg, #fffdf0 0%, #ffffff 100%) !important; }
        .zone-danger { border-left: 8px solid #2baf2b !important; background: linear-gradient(90deg, #f0fff0 0%, #ffffff 100%) !important; }
        
        /* Anillos en Clasificación */
        .ring-avatar { border-radius: 50%; padding: 3px; display: inline-block; line-height: 0; }
        .ring-gold { background: linear-gradient(45deg, #ffd700, #ffae00); box-shadow: 0 0 10px rgba(255,215,0,0.3); }
        .ring-silver { background: linear-gradient(45deg, #c0c0c0, #8e8e8e); }
        .ring-bronze { background: linear-gradient(45deg, #cd7f32, #a0522d); }
        .ring-green { background: linear-gradient(45deg, #39FF14, #2baf2b); }
        /* Tarjeta de partido estilo App */   

    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚽ Menú Liga")
        
        # --- MEJORA: SALTO AUTOMÁTICO DE JORNADA ---
        lista_jornadas = list(JORNADAS.keys())
        indice_defecto = 0
        for i, nombre_j in enumerate(lista_jornadas):
            pendientes = df_r_all[(df_r_all['Jornada'] == nombre_j) & (df_r_all['Finalizado'] == "NO")]
            if not pendientes.empty:
                indice_defecto = i
                break
        
        j_global = st.selectbox("📅 Seleccionar Jornada:", lista_jornadas, index=indice_defecto, key="side_j")
        st.divider()
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False; st.rerun()

    # --- CÁLCULO DE DASHBOARD HERO (Versión Mundial) ---
    stats_hero = []
    df_b_all = leer_datos("Brackets") # Cargamos los brackets
    # El bracket real es el que rellena el ADMIN
    admin_b = df_b_all[df_b_all['Usuario'].str.upper() == 'ADMIN']
    r_bracket = admin_b.iloc[0] if not admin_b.empty else None

    for u in u_jugadores:
        pb_row = df_base[df_base['Usuario'] == u]
        p_base = safe_float(pb_row['Puntos'].values[0]) if not pb_row.empty else 0.0
        
        u_p_hist = df_p_all[df_p_all['Usuario'] == u]
        p_acum = p_base
        
        # 1. PUNTOS POR PARTIDOS DIARIOS
        for r in u_p_hist.itertuples():
            m = df_r_all[(df_r_all['Jornada'] == r.Jornada) & (df_r_all['Partido'] == r.Partido) & (df_r_all['Finalizado'] == "SI")]
            if not m.empty:
                p_acum += calcular_puntos_wc(
                    r.P_L, r.P_V, 
                    m.iloc[0]['R_L'], m.iloc[0]['R_V'], 
                    m.iloc[0]['Tipo'],
                    getattr(r, 'P_Pasa', None),
                    m.iloc[0].get('R_Pasa'),
                    m.iloc[0].get('Hubo_Prorroga') == "SI"
                )

        # 2. PUNTOS POR EL BRACKET
        u_bracket_row = df_b_all[df_b_all['Usuario'] == u]
        if not u_bracket_row.empty and r_bracket is not None:
            p_acum += calcular_puntos_bracket(u_bracket_row.iloc[0], r_bracket)

        stats_hero.append({"Usuario": u, "Puntos": p_acum})
    
    df_hero = pd.DataFrame(stats_hero).sort_values("Puntos", ascending=False).reset_index(drop=True)
    df_hero['Posicion'] = range(1, len(df_hero) + 1)
    lider = df_hero.iloc[0] if not df_hero.empty else {"Usuario": "Nadie", "Puntos": 0.0}

    es_admin = st.session_state.rol == "admin"
    if es_admin:
        mi_pos = "ADMIN"
        mi_puntos_hoy = 0.00
    else:
        mi_pos_query = df_hero[df_hero['Usuario'] == st.session_state.user]['Posicion']
        mi_pos = f"#{int(mi_pos_query.values[0])}" if not mi_pos_query.empty else "-"
        u_p_hoy = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global)]
        mi_puntos_hoy = 0.0
        for r in u_p_hoy.itertuples():
            m = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Partido'] == r.Partido) & (df_r_all['Finalizado'] == "SI")]
            if not m.empty:
                mi_puntos_hoy += calcular_puntos_wc(r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'])

    prox_p = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "NO")].sort_values("Hora_Inicio").head(1)
    # Verificamos si hay partidos antes de calcular el tiempo
    hay_proximo = not prox_p.empty
    
    st.title(f"Hola, {st.session_state.user} 👋")

    # --- RENDER DASHBOARD HERO ---
    # --- 1. LÓGICA DE CÁLCULO: LÍDER Y LAGARTO(S) ---
    # Buscamos la última jornada que tenga partidos finalizados
    jornadas_con_finalizados = df_r_all[df_r_all['Finalizado'] == "SI"]['Jornada'].unique()
    lagartos_nombres = []
    puntos_lagarto = 0.0
    nombre_ultima_j = "-"

    if len(jornadas_con_finalizados) > 0:
        nombre_ultima_j = jornadas_con_finalizados[-1]
        puntos_last_j = []
        
        for u in u_jugadores:
            u_p_last = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == nombre_ultima_j)]
            pts_j = 0.0
            for r in u_p_last.itertuples():
                m_res = df_r_all[(df_r_all['Jornada'] == nombre_ultima_j) & (df_r_all['Partido'] == r.Partido) & (df_r_all['Finalizado'] == "SI")]
                if not m_res.empty:
                    pts_j += calcular_puntos_wc(r.P_L, r.P_V,m_res.iloc[0]['R_L'], m_res.iloc[0]['R_V'], m_res.iloc[0]['Tipo'], getattr(r, 'P_Pasa', None), m_res.iloc[0].get('R_Pasa'), m_res.iloc[0].get('Hubo_Prorroga') == "SI")
            puntos_last_j.append({"Usuario": u, "Puntos": pts_j})
        
        if puntos_last_j:
            df_last_j = pd.DataFrame(puntos_last_j)
            puntos_lagarto = df_last_j['Puntos'].min()
            # Obtenemos todos los que tengan la puntuación mínima (por si hay empate)
            lagartos_nombres = df_last_j[df_last_j['Puntos'] == puntos_lagarto]['Usuario'].tolist()

    # --- 2. DISEÑO VISUAL DE LA CABECERA ---
    with st.container():
        st.markdown('<div class="hero-bg">', unsafe_allow_html=True)
        # Ajustamos columnas: Lider (1.2), Lagarto (1.2), Espacio (0.1), Datos (3.2)
        col_lider, col_lagarto, col_sep, col_datos = st.columns([1.2, 1.2, 0.1, 3.2])
        
        # --- COLUMNA LÍDER GENERAL ---
        with col_lider:
            st.markdown('<span class="section-tag">LÍDER GENERAL</span>', unsafe_allow_html=True)
            st.markdown('<div style="position: relative; text-align: center;"><span class="crown">👑</span>', unsafe_allow_html=True)
            # 1. Sacamos qué equipo puso el líder como campeón en su Bracket
            # (Asumiendo que tenemos una tabla llamada df_brackets)
            try:
                equipo_fav = df_b_all[df_b_all['Usuario'] == lider['Usuario']]['Campeon'].values[0]
                colores = COLORES_BANDERAS.get(equipo_fav, ["#ffd700", "#ffae00"]) 
                estilo_anillo = f"background: linear-gradient(45deg, {colores[0]}, {colores[1]});"
            except:
                estilo_anillo = ""
            
            # 2. En el HTML del Avatar
            st.markdown(f'<div class="ring-avatar" style="{estilo_anillo}">', unsafe_allow_html=True)
            f_l = foto_dict.get(lider['Usuario'])
            if f_l and os.path.exists(str(f_l)): 
                st.image(f_l, width=80)
            else: 
                st.markdown("<h1 style='margin:0;'>👤</h1>", unsafe_allow_html=True)
            st.markdown(f"<small><b>{lider['Usuario']}</b></small><br><span style='color:#daa520; font-weight:bold; font-size:1.1em;'>{lider['Puntos']:.2f} Pts</span></div>", unsafe_allow_html=True)
        
        # --- COLUMNA LAGARTO(S) DE LA ÚLTIMA JORNADA ---
        with col_lagarto:
            st.markdown(f'<span class="section-tag" style="background:#2baf2b;">LAGARTO {nombre_ultima_j}</span>', unsafe_allow_html=True)
            st.markdown('<div style="position: relative; text-align: center;"><span style="font-size:2em; position:absolute; top:-35px; left:35px; transform:rotate(15deg);">🦎</span>', unsafe_allow_html=True)
            
            if len(lagartos_nombres) == 1:
                # Si solo hay uno, mostramos su foto
                f_p = foto_dict.get(lagartos_nombres[0])
                if f_p and os.path.exists(str(f_p)): 
                    st.image(f_p, width=80)
                else: 
                    st.markdown("<h1 style='margin:0;'>👤</h1>", unsafe_allow_html=True)
                st.markdown(f"<small><b>{lagartos_nombres[0]}</b></small>", unsafe_allow_html=True)
            elif len(lagartos_nombres) > 1:
                # Si hay empate, mostramos icono de plaga y los nombres
                st.markdown("<h1 style='margin:10px 0;'>🦎🦎</h1>", unsafe_allow_html=True)
                nombres_fmt = " & ".join(map(str, lagartos_nombres))
                st.markdown(f"<div style='line-height:1.1; margin-bottom:5px;'><small><b>{nombres_fmt}</b></small></div>", unsafe_allow_html=True)
            else:
                st.markdown("<h1 style='margin:10px 0;'>-</h1>", unsafe_allow_html=True)
            
            st.markdown(f"<span style='color:#2baf2b; font-weight:bold; font-size:1.1em;'>{puntos_lagarto:.2f} Pts</span></div>", unsafe_allow_html=True)

        # --- COLUMNA DE DATOS DEL USUARIO Y CONTADOR ---
        # --- COLUMNA DE DATOS DEL USUARIO Y CONTADOR ---
        with col_datos:
            st.markdown(f'<span class="section-tag">{"PANEL CONTROL" if es_admin else "TUS ESTADÍSTICAS"}</span>', unsafe_allow_html=True)
            c2, c3, c4 = st.columns(3)
            with c2: 
                st.markdown(f'<div class="kpi-box"><span class="kpi-label">Tu Puesto</span><span class="kpi-value">{mi_pos}</span></div>', unsafe_allow_html=True)
            
            with c3:
                if hay_proximo:
                    ahora_madrid = get_now_madrid()
                    diff = datetime.datetime.strptime(str(prox_p.iloc[0]['Hora_Inicio']), "%Y-%m-%d %H:%M:%S") - ahora_madrid
                    ts = int(diff.total_seconds())
                    if ts > 0:
                        h = (ts % 86400) // 3600
                        m = (ts % 3600) // 60
                        color = "#ff4b4b" if ts < 7200 else "#2baf2b"
                        st.markdown(f'<div class="kpi-box"><span class="kpi-label">Cierre en</span><span class="kpi-value" style="color:{color}; font-size: 1.2em;">{h:02d}h {m:02d}m</span></div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="kpi-box"><span class="kpi-label">Mercado</span><span class="kpi-value" style="color:#6c757d;">Cerrado</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="kpi-box"><span class="kpi-label">Jornada</span><span class="kpi-value">Finalizada</span></div>', unsafe_allow_html=True)
            
            with c4: 
                st.markdown(f'<div class="kpi-box"><span class="kpi-label">Puntos Hoy</span><span class="kpi-value" style="color:#007bff;">{mi_puntos_hoy:.2f}</span></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
    usa_oraculo = 1 <= len(df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "NO")]) <= 3
    # Busca esta línea y añade "📜 VAR" al final
    tabs = st.tabs([
    "✍️ Apuestas", 
    "🌳 Bracket",      # <--- NUEVA: Para rellenar el cuadro
    "👀 La Grada", 
    "📊 Clasificación", 
    "🏅 Palmarés", 
    "📈 Stats PRO", 
    "🏆 Detalles",
    "🔮 Simulador", 
    "🎲 Oráculo", 
    "⚙️ Admin", 
    "📜 VAR"
    ])

    with tabs[0]: # --- ✍️ PESTAÑA APUESTAS (ADAPTADA MUNDIAL) ---
        st.markdown("""
        <style>
            .bet-card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 15px; }
            .bet-card-locked { background: #f1f5f9; padding: 20px; border-radius: 15px; border: 1px solid #cbd5e1; opacity: 0.8; margin-bottom: 15px; }
            .team-label { font-weight: 800; font-size: 0.9em; color: #1e293b; text-align: center; margin-bottom: 5px; text-transform: uppercase; }
            .vs-box { text-align: center; font-weight: 900; color: #94a3b8; padding-top: 10px; }
            .ko-tag { background: #fee2e2; color: #ef4444; font-size: 0.7em; padding: 2px 8px; border-radius: 10px; font-weight: bold; margin-bottom: 5px; display: inline-block; }
        </style>
        """, unsafe_allow_html=True)

        if es_admin:
            st.warning("🛡️ Acceso restringido: Los administradores no participan en las porras.")
            st.info("Tu función es supervisar el Mundial y actualizar los resultados desde la pestaña **⚙️ Admin**.")
            st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnh6Znd6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/fNuXfHoZY3nqE/giphy.gif", width=400)
        else:
            # --- NUEVO: SECCIÓN OJO CON... (REVELACIÓN) ---
            st.markdown("### 👀 Tu Equipo Revelación")
            st.caption("¿Qué selección dará la sorpresa en el Mundial? ¡Se bloqueará en cuanto empiece el torneo!")
            
            # Rescatamos el valor actual de PuntosBase
            row_ojo = df_base[df_base['Usuario'] == st.session_state.user]
            actual_ojo = str(row_ojo.iloc[0].get("Ojo_con", "Ninguno")) if not row_ojo.empty and "Ojo_con" in row_ojo.columns else "Ninguno"
            if actual_ojo.lower() == "nan" or actual_ojo == "": actual_ojo = "Ninguno"
            
            todos_los_equipos = ["Ninguno"] + sorted(list(CONTINENTES.keys()))
            idx_ojo = todos_los_equipos.index(actual_ojo) if actual_ojo in todos_los_equipos else 0
            
            col_sel_ojo, col_btn_ojo = st.columns([3, 1])
            with col_sel_ojo:
                nuevo_ojo = st.selectbox("Ojo con...", todos_los_equipos, index=idx_ojo, disabled=not mercado_abierto, label_visibility="collapsed", key="ojo_apuestas")
            
            with col_btn_ojo:
                if mercado_abierto and nuevo_ojo != actual_ojo:
                    if st.button("💾 Guardar Revelación", use_container_width=True, type="primary"):
                        df_pb_upd = df_base.copy()
                        
                        # 🔥 BLINDAJE CRÍTICO: Forzamos la columna a tipo String (Texto) para evitar el TypeError
                        if 'Ojo_con' in df_pb_upd.columns:
                            df_pb_upd['Ojo_con'] = df_pb_upd['Ojo_con'].astype(str)
                        else:
                            df_pb_upd['Ojo_con'] = "Ninguno"
                            
                        idx_pb = df_pb_upd[df_pb_upd['Usuario'] == st.session_state.user].index
                        if len(idx_pb) > 0:
                            df_pb_upd.loc[idx_pb, 'Ojo_con'] = nuevo_ojo
                        else:
                            df_pb_upd = pd.concat([df_pb_upd, pd.DataFrame([{"Usuario": st.session_state.user, "Puntos": 0.0, "Ojo_con": nuevo_ojo}])], ignore_index=True)
                        
                        # Aseguramos que la columna no guarde flotantes raros como "nan" antes de subir
                        df_pb_upd['Ojo_con'] = df_pb_upd['Ojo_con'].fillna("Ninguno")
                        
                        conn.update(worksheet="PuntosBase", data=df_pb_upd)
                        st.cache_data.clear()
                        st.success("¡Guardado!")
                        time.sleep(1)
                        st.rerun()
            
            st.divider()
            # --- ZONA DE EXPLICACIÓN DE PUNTUACIÓN ---
            with st.container():
                col_rules1, col_rules2 = st.columns(2)
                
                with col_rules1:
                    st.markdown("""
                    <div class="rules-box">
                        <h5 style='margin-top:0; color:#1e3a8a;'>🟢 Partidos Normales</h5>
                        <ul style='font-size:0.9em; margin-bottom:5px; color:#334155; padding-left:20px;'>
                            <li>💯 <b>+1.00 pto</b> - <b>Resultado Exacto:</b> Clavas el marcador.</li>
                            <li>📐 <b>+0.75 pts</b> - <b>Diferencia de Goles:</b> Aciertas ganador y diferencia.</li>
                            <li>⚖️ <b>+0.50 pts</b> - <b>Signo (1X2):</b> Aciertas quién gana o empata.</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_rules2:
                    st.markdown("""
                    <div class="esquizo-box">
                        <h5 style='margin-top:0; color:#92400e;'>🔥 Partidos Esquizos (¡Puntuación Doble!)</h5>
                        <p style='font-size:0.85em; color:#78350f; margin-bottom:8px;'>¡Cuidado con estos! Hay pocos por jornada y pueden cambiarlo todo:</p>
                        <ul style='font-size:0.9em; margin-bottom:5px; color:#78350f; padding-left:20px;'>
                            <li>💯 <b>+3.00 pts</b> - <b>Resultado Exacto.</b></li>
                            <li>📐 <b>+1.50 pts</b> - <b>Diferencia de Goles.</b></li>
                            <li>⚖️ <b>+1.00 pto</b> - <b>Signo (1X2).</b></li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
                if any(x in j_global for x in ["Dieciseisavos", "Octavos", "Cuartos", "Semis", "Final"]):
                    st.markdown("""
                    <div class="rules-box" style="border-left-color: #ef4444; background-color: #fffafb;">
                        <small style="color:#b91c1c; font-weight:bold; text-transform:uppercase;">⚠️ Regla Especial de Eliminatorias</small><br>
                        <span style='font-size:0.85em; color:#7f1d1d;'>
                            El marcador cuenta para los <b>90' reglamentarios</b>. Si el partido va a la prórroga, el bonus por acertar <b>"¿Quién clasifica?"</b> te dará <b>+0.50 pts</b> en partidos Normales y <b>+1.00 pto</b> si el partido está marcado como <b>Esquizo</b>.
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            # Recuperar predicciones actuales del usuario
            u_preds = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global)]
            
            # --- [LÓGICA DE ORDENACIÓN] ---
            df_partidos_ordenados = df_r_all[df_r_all['Jornada'] == j_global].copy()
            df_partidos_ordenados['Hora_DT'] = pd.to_datetime(df_partidos_ordenados['Hora_Inicio'])
            df_partidos_ordenados = df_partidos_ordenados.sort_values('Hora_DT', ascending=True)
            
            lista_partidos_cronologica = []
            for _, row in df_partidos_ordenados.iterrows():
                try:
                    loc, vis = row['Partido'].split('-')
                    lista_partidos_cronologica.append((loc, vis))
                except: continue 
            
            env = []
            st.markdown(f"### 🗓️ Tu Hoja de Apuestas: {j_global}")
            
            # Detectamos si es ronda de eliminación (KO)
            es_ronda_ko = any(x in j_global for x in ["Dieciseisavos", "Octavos", "Cuartos", "Semis", "Final"])

            for i, (loc, vis) in enumerate(lista_partidos_cronologica):
                m_id = f"{loc}-{vis}"
                
                # Cargar datos guardados (incluyendo P_Pasa)
                dl, dv, dp, d_pasa = 0, 0, "NO", loc
                if not u_preds.empty:
                    match_data = u_preds[u_preds['Partido'] == m_id]
                    if not match_data.empty:
                        dl = int(match_data.iloc[0]['P_L'])
                        dv = int(match_data.iloc[0]['P_V'])
                        dp = match_data.iloc[0]['Publica']
                        d_pasa = match_data.iloc[0].get('P_Pasa', loc)
                
                # Lógica de Bloqueo por tiempo y rescate de Tipo de Partido
                res_info = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Partido'] == m_id)]
                lock = False
                hora_partido = ""
                tipo_partido = "Normal" # Por defecto
                
                if not res_info.empty:
                    hora_partido = res_info.iloc[0]['Hora_Inicio']
                    tipo_partido = res_info.iloc[0]['Tipo']
                    lock = get_now_madrid() > datetime.datetime.strptime(str(hora_partido), "%Y-%m-%d %H:%M:%S")

                # --- RENDER DE LA TARJETA ---
                card_class = "bet-card-locked" if lock else "bet-card"
                st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                
                # --- NUEVA SEÑALIZACIÓN DINÁMICA DE PARTIDO ESQUIZO ---
                col_tags1, col_tags2 = st.columns([3, 1])
                with col_tags1:
                    if tipo_partido == "Esquizo":
                        st.markdown('<span class="ko-tag" style="background:#fef3c7; color:#d97706; border: 1px solid #f59e0b;">🔥 PARTIDO ESQUIZO (PUNTUACIÓN TRIPLE)</span>', unsafe_allow_html=True)
                    elif tipo_partido == "Doble":
                        st.markdown('<span class="ko-tag" style="background:#e0f2fe; color:#0369a1; border: 1px solid #0ea5e9;">🔄 PARTIDO DOBLE</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="ko-tag" style="background:#f0fdf4; color:#16a34a; border: 1px solid #22c55e;">⚽ Partido Normal</span>', unsafe_allow_html=True)
                
                with col_tags2:
                    if es_ronda_ko:
                        st.markdown('<span class="ko-tag" style="float:right;">🛑 ELIMINATORIA</span>', unsafe_allow_html=True)

                # Cuerpo de la tarjeta de apuestas
                c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 1, 2, 1, 1.5])
                
                with c1: # Escudo Local
                    log_l = get_logo(loc)
                    if log_l: st.image(log_l, width=50)
                
                with c2: # Marcador Local
                    st.markdown(f'<p class="team-label">{loc}</p>', unsafe_allow_html=True)
                    pl = st.number_input("G", 0, 9, dl, key=f"pl_{i}_{j_global}", disabled=lock, label_visibility="collapsed")
                
                with c3: # VS
                    st.markdown('<div class="vs-box">VS</div>', unsafe_allow_html=True)
                    if lock: st.markdown('<p style="text-align:center;">🔒</p>', unsafe_allow_html=True)
                    else:
                        try:
                            dt_p = datetime.datetime.strptime(str(hora_partido), "%Y-%m-%d %H:%M:%S")
                            st.markdown(f'<p style="text-align:center; font-size:0.65em; color:#64748b; font-weight:bold;">{dt_p.strftime("%d/%m %H:%M")}</p>', unsafe_allow_html=True)
                        except: st.markdown('<p style="text-align:center;">-</p>', unsafe_allow_html=True)

                with c4: # Marcador Visitante
                    st.markdown(f'<p class="team-label">{vis}</p>', unsafe_allow_html=True)
                    pv = st.number_input("G", 0, 9, dv, key=f"pv_{i}_{j_global}", disabled=lock, label_visibility="collapsed")
                
                with c5: # Escudo Visitante
                    log_v = get_logo(vis)
                    if log_v: st.image(log_v, width=50)
                
                with c6: # Visibilidad
                    st.markdown("<p style='font-size:0.7em; text-align:center; font-weight:bold;'>👁️ PÚBLICA</p>", unsafe_allow_html=True)
                    pub = st.checkbox("Ver", dp=="SI", key=f"pb_{i}_{j_global}", disabled=lock, label_visibility="collapsed")
                
                # --- [FILA RONDAS KO] ---
                pasa_res = None
                if es_ronda_ko:
                    st.markdown("<br>", unsafe_allow_html=True)
                    col_pasa1, col_pasa2 = st.columns([2, 4])
                    with col_pasa1:
                        st.markdown("<p style='font-size:0.85em; font-weight:bold; margin-top:10px;'>🏆 ¿Quién clasifica?</p>", unsafe_allow_html=True)
                        st.caption("Solo cuenta si hay empate tras 90'.")
                    with col_pasa2:
                        lista_equipos = [loc, vis]
                        idx_defecto = lista_equipos.index(d_pasa) if d_pasa in lista_equipos else 0
                        pasa_res = st.selectbox("Selecciona equipo", lista_equipos, index=idx_defecto, key=f"pasa_{i}_{j_global}", disabled=lock, label_visibility="collapsed")

                st.markdown('</div>', unsafe_allow_html=True)
                
                # Guardamos datos en la lista de envío
                tiene_prediccion_previa = not u_preds[u_preds['Partido'] == m_id].empty if not u_preds.empty else False
                if not lock or tiene_prediccion_previa:
                    env.append({
                        "Usuario": st.session_state.user, 
                        "Jornada": j_global, 
                        "Partido": m_id, 
                        "P_L": pl, 
                        "P_V": pv, 
                        "P_Pasa": pasa_res, # Guardamos quién pasa
                        "Publica": "SI" if pub else "NO"
                    })

            # --- BOTÓN DE GUARDADO ---
            st.markdown("---")
            # --- BOTÓN DE GUARDADO ---
            st.markdown("---")
            # --- BOTÓN DE GUARDADO ---
            st.markdown("---")
            # --- BOTÓN DE GUARDADO ---
            st.markdown("---")
            if st.button("💾 GUARDAR MIS PRONÓSTICOS", use_container_width=True, type="primary"):
                # 1. Comparar con lo anterior para el log del VAR
                preds_viejas = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global)]
                
                if preds_viejas.empty:
                    log_msg = f"📝 Creó sus primeras predicciones del Mundial ({j_global})"
                else:
                    cambios = []
                    # Detectamos si es ronda de eliminación para activar el check de quién pasa
                    es_ronda_ko = any(x in j_global for x in ["Dieciseisavos", "Octavos", "Cuartos", "Semis", "Final"])

                    for r_nuevo in env:
                        m_viejo = preds_viejas[preds_viejas['Partido'] == r_nuevo['Partido']]
                        if not m_viejo.empty:
                            # Tu lógica original exacta con int():
                            cambio_goles = (r_nuevo['P_L'] != int(m_viejo.iloc[0]['P_L'])) or (r_nuevo['P_V'] != int(m_viejo.iloc[0]['P_V']))
                            
                            # Lógica para controlar el bug del None vs NaN en eliminatorias
                            cambio_pasa = False
                            if es_ronda_ko:
                                p_nuevo = str(r_nuevo.get('P_Pasa', '')).strip().lower()
                                p_viejo = str(m_viejo.iloc[0].get('P_Pasa', '')).strip().lower()
                                # Si los textos son 'nan' o 'none', los tratamos como vacíos para que no den falso positivo
                                if p_nuevo in ['none', 'nan', '']: p_nuevo = 'vacio'
                                if p_viejo in ['none', 'nan', '']: p_viejo = 'vacio'
                                cambio_pasa = (p_nuevo != p_viejo)

                            if cambio_goles or cambio_pasa:
                                cambios.append(r_nuevo['Partido'])
                    
                    if cambios:
                        lista_partidos_txt = ", ".join(cambios)
                        log_msg = f"🔄 Modificó sus porras en: {lista_partidos_txt} ({j_global})"
                    else:
                        log_msg = f"📝 Re-guardó predicciones sin cambios ({j_global})"

                # 2. Actualizar base de datos (Predicciones)
                otras_preds = df_p_all[~((df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global))]
                df_final_p = pd.concat([otras_preds, pd.DataFrame(env)], ignore_index=True)
                conn.update(worksheet="Predicciones", data=df_final_p)
                
                # 3. Escribir en el VAR (Logs)
                log_entry = pd.DataFrame([{
                    "Fecha": get_now_madrid().strftime("%Y-%m-%d %H:%M:%S"),
                    "Usuario": st.session_state.user,
                    "Accion": log_msg
                }])
                df_l_existente = conn.read(worksheet="Logs", ttl=0)
                conn.update(worksheet="Logs", data=pd.concat([df_l_existente, log_entry], ignore_index=True))
                
                # 4. Feedback y Refresco
                st.cache_data.clear()
                st.cache_resource.clear()
                st.success(f"✅ ¡Hecho! El VAR ha registrado: {log_msg}")
                time.sleep(1.2)
                st.rerun()

    
    with tabs[1]: # --- 🌳 PESTAÑA SUPER BRACKET (MUNDIAL 2026) ---
            st.markdown("## 🧬 Similitud de Brackets")
            st.caption("Analizamos vuestros cuadros del Mundial. Quién comparte tus mismos clasificados, cruces y campeones.")
            
            # Re-leemos los brackets frescos
            df_b_sim = leer_datos("Brackets")
            
            if not df_b_sim.empty and len(u_jugadores) > 1:
                # Filtramos solo las filas de los usuarios jugadores (quitando al ADMIN para el cálculo de copia)
                df_b_players = df_b_sim[df_b_sim['Usuario'].isin(u_jugadores)].copy()
                
                # Identificamos las columnas de predicciones del bracket (quitando la columna Usuario)
                columnas_bracket = [c for c in df_b_players.columns if c not in ['Usuario', 'Usuario_Lower']]
                
                if columnas_bracket:
                    # Transponemos para tener las columnas de predicciones como filas y los usuarios como columnas
                    df_pivot_b = df_b_players.set_index('Usuario')[columnas_bracket].T.fillna("N/A")
                    
                    pares_bracket_sim = []
                    # Iteramos por todas las combinaciones posibles de parejas de jugadores
                    for u1, u2 in itertools.combinations(u_jugadores, 2):
                        if u1 in df_pivot_b.columns and u2 in df_pivot_b.columns:
                            # Contamos coincidencias exactas en celdas (mismo 1º, mismo 2º, mismo campeón, etc.)
                            coincidencias = np.sum(df_pivot_b[u1].astype(str).str.strip().str.lower() == df_pivot_b[u2].astype(str).str.strip().str.lower())
                            total_items_bracket = len(columnas_bracket)
                            porcentaje_b_sim = (coincidencias / total_items_bracket) * 100
                            
                            pares_bracket_sim.append({
                                "Jugador 1": u1,
                                "Jugador 2": u2,
                                "Porcentaje": porcentaje_b_sim,
                                "Coincidencias": coincidencias,
                                "Total": total_items_bracket
                            })
                    
                    if pares_bracket_sim:
                        df_sim_b_pares = pd.DataFrame(pares_bracket_sim)
                        
                        top_afinidades_b = df_sim_b_pares.sort_values(by="Porcentaje", ascending=False).head(5)
                        top_rivalidades_b = df_sim_b_pares.sort_values(by="Porcentaje", ascending=True).head(5)
                        
                        col_izq_bsim, col_der_bsim = st.columns(2)
                        
                        # --- COLUMNA IZQUIERDA: BRACKETS CLONADOS ---
                        with col_izq_bsim:
                            st.markdown("##### 🤝 Mismo Mapa a la Final (Mayor Similitud)")
                            for _, fila in top_afinidades_b.iterrows():
                                pct = fila['Porcentaje']
                                color_alert = "#e0f2fe" if pct > 45 else "#f8f9fa"
                                border_alert = "#bae6fd" if pct > 45 else "#e2e8f0"
                                
                                st.markdown(f"""
                                    <div style="background:{color_alert}; padding:10px; border-radius:10px; border:1px solid {border_alert}; margin-bottom:8px;">
                                        <div style="display:flex; justify-content:space-between; align-items:center;">
                                            <span style="font-weight:bold; color:#1e293b;">{fila['Jugador 1']} & {fila['Jugador 2']}</span>
                                            <span style="font-size:1.1em; font-weight:800; color:#0369a1;">{pct:.1f}%</span>
                                        </div>
                                        <small style="color:#475569;">Comparten exactamente <b>{fila['Coincidencias']}</b> de {fila['Total']} posiciones del cuadro.</small>
                                    </div>
                                """, unsafe_allow_html=True)
                    
                        # --- COLUMNA DERECHA: BRACKETS CRUZADOS ---
                        with col_der_bsim:
                            st.markdown("##### ⚔️ Visiones Cruzadas (Menor Similitud)")
                            for _, fila in top_rivalidades_b.iterrows():
                                pct = fila['Porcentaje']
                                color_alert = "#fff1f2" if pct < 25 else "#f8f9fa"
                                border_alert = "#ffe4e6" if pct < 25 else "#e2e8f0"
                                
                                st.markdown(f"""
                                    <div style="background:{color_alert}; padding:10px; border-radius:10px; border:1px solid {border_alert}; margin-bottom:8px;">
                                        <div style="display:flex; justify-content:space-between; align-items:center;">
                                            <span style="font-weight:bold; color:#1e293b;">{fila['Jugador 1']} vs {fila['Jugador 2']}</span>
                                            <span style="font-size:1.1em; font-weight:800; color:#9f1239;">{pct:.1f}%</span>
                                        </div>
                                        <small style="color:#475569;">Solo coinciden en <b>{fila['Coincidencias']}</b> de {fila['Total']} casillas del cuadro.</small>
                                    </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("Faltan datos cruzados en los cuadros guardados.")
                else:
                    st.info("Estructura de columnas del bracket no identificada.")
            else:
                st.info("Esperando a que los usuarios guarden sus Brackets para calcular el termómetro.")
            
            st.divider()
            st.header("🌳 El Súper Bracket del Mundial")
            st.caption("Define las posiciones de los grupos, los mejores terceros y el camino a la gloria.")
            
            # --- ZONA DE EXPLICACIÓN DE PUNTUACIÓN DEL BRACKET ---
            with st.expander("📊 📜 Ver Reglamento de Puntos del Súper Bracket", expanded=False):
                st.markdown("""
                A diferencia de la porra diaria, el Súper Bracket premia la **supervivencia** de tus equipos seleccionados y los cruces exactos:
                
                | Hito o Fase Alcanzada | Puntos por Acierto |
                | :--- | :--- |
                | 🏁 **Clasificados de Grupo** (1º y 2º puesto) | **+0.50 pts** por equipo exacto |
                | 🎯 **Elegir Mejor Tercero** clasificado | **+0.50 pts** por equipo acertado |
                | 🛡️ **Avance a Octavos de Final** | **+0.50 pts** por equipo que metes en la fase |
                | 📊 **Avance a Cuartos de Final** | **+1.00 pto** por equipo que metes en la fase |
                | ⚔️ **Avance a Semifinales** | **+1.50 pts** por equipo que metes en la fase |
                | 🥇 **Avance a la Gran Final** | **+2.00 pts** por equipo que metes en la fase |
                | 🏆 **Acertar Campeón del Mundo** | **+4.00 pts** |
                
                **🔥 Bonus Extra por Cruces Exactos:**
                Si clavas los dos equipos que se enfrentan en una llave (sin importar el orden de local/visitante), te llevas un bonus adicional: **+0.50 pts** en 16vos, **+1.00 pto** en 8vos y 4tos, y **+2.00 pts** en la Final.
                """)
                
            FECHA_INAUGURAL = datetime.datetime(2026, 6, 11, 21, 0, 0)
            mercado_abierto = get_now_madrid() < FECHA_INAUGURAL
            
            # --- NUEVO: LLAVE MAESTRA DEL ADMIN ---
            es_admin = (st.session_state.user == "ADMIN")
            puede_editar = mercado_abierto or es_admin
            
            if not mercado_abierto:
                if es_admin:
                    st.warning("👑 **MODO ADMIN.** El mercado está cerrado para los jugadores, pero tú tienes permisos para actualizar el Cuadro Oficial.")
                else:
                    st.error(f"🔒 **MERCADO CERRADO.** No se admiten más cambios.")
            else:
                st.success(f"🔓 **MERCADO ABIERTO.** Tienes hasta el 11 de junio a las 21:00.")
        
            df_b_all = leer_datos("Brackets")
            b_prev = df_b_all[df_b_all['Usuario'] == st.session_state.user]
            
            st.subheader("1️⃣ Posiciones de la Fase de Grupos")
            ganadores_grupos = {}
            todos_los_terceros = []
        
            c_g1, c_g2, c_g3 = st.columns(3)
            for idx, (nombre_g, equipos) in enumerate(GRUPOS_2026.items()):
                target_col = [c_g1, c_g2, c_g3][idx % 3]
                with target_col:
                    with st.container(border=True):
                        st.markdown(f"**{nombre_g}**")
                        def_p1 = b_prev.iloc[0][f"{nombre_g}_1"] if not b_prev.empty else equipos[0]
                        def_p2 = b_prev.iloc[0][f"{nombre_g}_2"] if not b_prev.empty else equipos[1]
                        def_p3 = b_prev.iloc[0][f"{nombre_g}_3"] if not b_prev.empty else equipos[2]
        
                        p1 = st.selectbox(f"1º", equipos, index=equipos.index(def_p1) if def_p1 in equipos else 0, key=f"p1_{nombre_g}", disabled=not puede_editar)
                        op2 = [e for e in equipos if e != p1]
                        p2 = st.selectbox(f"2º", op2, index=op2.index(def_p2) if def_p2 in op2 else 0, key=f"p2_{nombre_g}", disabled=not puede_editar)
                        op3 = [e for e in op2 if e != p2]
                        p3 = st.selectbox(f"3º", op3, index=op3.index(def_p3) if def_p3 in op3 else 0, key=f"p3_{nombre_g}", disabled=not puede_editar)
                        p4 = [e for e in op3 if e != p3][0]
                        st.caption(f"4º puesto: {p4}")
        
                        ganadores_grupos[f"{nombre_g}_1"] = p1
                        ganadores_grupos[f"{nombre_g}_2"] = p2
                        ganadores_grupos[f"{nombre_g}_3"] = p3
                        todos_los_terceros.append(p3)
        
            st.divider()
        
            st.subheader("🎯 2️⃣ Elección de Mejores Terceros")
            def_terc_str = b_prev.iloc[0]["MejoresTerceros"] if not b_prev.empty and "MejoresTerceros" in b_prev.columns else ""
            def_terceros_list = def_terc_str.split(",") if def_terc_str else []
            
            seleccion_terceros = st.multiselect(
                "Selecciona exactamente 8:",
                options=todos_los_terceros,
                default=[t for t in def_terceros_list if t in todos_los_terceros],
                max_selections=8,
                key="ms_terceros",
                disabled=not puede_editar
            )
        
            if len(seleccion_terceros) < 8:
                st.warning(f"⚠️ Seleccionados: {len(seleccion_terceros)}/8. El cuadro se activará al elegir 8.")
            else:
                st.subheader("🏟️ 3️⃣ Dieciseisavos de Final (Matriz FIFA)")
                
                grupos_3ros = []
                mapa_pais_letra = {}
                for pais in seleccion_terceros:
                    for g_name in GRUPOS_2026.keys():
                        if ganadores_grupos[f"{g_name}_3"] == pais:
                            letra = g_name.replace("Grupo ", "")
                            grupos_3ros.append(letra)
                            mapa_pais_letra[letra] = pais
                            break
                
                clave_3ros = "".join(sorted(grupos_3ros))
                
                if clave_3ros not in MATRIZ_TERCEROS:
                    st.error("❌ ¡Combinación Imposible! Según la FIFA, es matemáticamente imposible que pasen esos 8 terceros juntos. Revisa tu selección.")
                else: 
                    cruces_3ros = MATRIZ_TERCEROS[clave_3ros]
                    
                    cruces_16 = [
                        (ganadores_grupos["Grupo A_2"], ganadores_grupos["Grupo B_2"]),
                        (ganadores_grupos["Grupo E_1"], mapa_pais_letra[cruces_3ros["1E"]]),
                        (ganadores_grupos["Grupo F_1"], ganadores_grupos["Grupo C_2"]),
                        (ganadores_grupos["Grupo C_1"], ganadores_grupos["Grupo F_2"]),
                        (ganadores_grupos["Grupo I_1"], mapa_pais_letra[cruces_3ros["1I"]]),
                        (ganadores_grupos["Grupo E_2"], ganadores_grupos["Grupo I_2"]),
                        (ganadores_grupos["Grupo A_1"], mapa_pais_letra[cruces_3ros["1A"]]),
                        (ganadores_grupos["Grupo L_1"], mapa_pais_letra[cruces_3ros["1L"]]),
                        (ganadores_grupos["Grupo D_1"], mapa_pais_letra[cruces_3ros["1D"]]),
                        (ganadores_grupos["Grupo G_1"], mapa_pais_letra[cruces_3ros["1G"]]),
                        (ganadores_grupos["Grupo K_2"], ganadores_grupos["Grupo L_2"]),
                        (ganadores_grupos["Grupo H_1"], ganadores_grupos["Grupo J_2"]),
                        (ganadores_grupos["Grupo B_1"], mapa_pais_letra[cruces_3ros["1B"]]),
                        (ganadores_grupos["Grupo J_1"], ganadores_grupos["Grupo H_2"]),
                        (ganadores_grupos["Grupo K_1"], mapa_pais_letra[cruces_3ros["1K"]]),
                        (ganadores_grupos["Grupo D_2"], ganadores_grupos["Grupo G_2"]) 
                    ]
        
                    ganadores_16 = []
                    cols_16 = st.columns(4)
                    for i, (loc, vis) in enumerate(cruces_16):
                        with cols_16[i // 4]:
                            st.markdown(f"<small>M{73+i}</small>", unsafe_allow_html=True)
                            def_w16 = b_prev.iloc[0][f"W16_{i}"] if not b_prev.empty and f"W16_{i}" in b_prev.columns else loc
                            res_16 = st.radio(f"{loc} vs {vis}", [loc, vis], index=[loc, vis].index(def_w16) if def_w16 in [loc, vis] else 0, key=f"radio_16_{i}", disabled=not puede_editar, label_visibility="collapsed")
                            ganadores_16.append(res_16)
        
                    st.subheader("🛡️ 4️⃣ Octavos de Final (Orden FIFA)")
                    cruces_8 = [
                        (ganadores_16[1], ganadores_16[4]),
                        (ganadores_16[0], ganadores_16[2]),
                        (ganadores_16[3], ganadores_16[5]),
                        (ganadores_16[6], ganadores_16[7]),
                        (ganadores_16[10], ganadores_16[11]),
                        (ganadores_16[8], ganadores_16[9]),
                        (ganadores_16[13], ganadores_16[15]),
                        (ganadores_16[12], ganadores_16[14])
                    ]
                    
                    ganadores_8 = []
                    cols_8 = st.columns(4)
                    for i, (loc, vis) in enumerate(cruces_8):
                        with cols_8[i // 2]:
                            st.markdown(f"<small>M{89+i}</small>", unsafe_allow_html=True)
                            def_w8 = b_prev.iloc[0][f"W8_{i}"] if not b_prev.empty and f"W8_{i}" in b_prev.columns else loc
                            res_8 = st.radio(f"{loc}-{vis}", [loc, vis], index=[loc, vis].index(def_w8) if def_w8 in [loc, vis] else 0, key=f"radio_8_{i}", disabled=not puede_editar)
                            ganadores_8.append(res_8)
        
                    st.subheader("📊 5️⃣ Cuartos de Final")
                    cruces_4 = [
                        (ganadores_8[0], ganadores_8[1]), (ganadores_8[4], ganadores_8[5]),
                        (ganadores_8[2], ganadores_8[3]), (ganadores_8[6], ganadores_8[7]) 
                    ]
                    
                    ganadores_4 = []
                    cols_4 = st.columns(2)
                    for i, (loc, vis) in enumerate(cruces_4):
                        with cols_4[i // 2]:
                            def_w4 = b_prev.iloc[0][f"W4_{i}"] if not b_prev.empty and f"W4_{i}" in b_prev.columns else loc
                            res_4 = st.radio(f"Cuarto {i+1}", [loc, vis], index=[loc, vis].index(def_w4) if def_w4 in [loc, vis] else 0, key=f"radio_4_{i}", disabled=not puede_editar)
                            ganadores_4.append(res_4)
        
                    st.subheader("⚔️ 6️⃣ Semifinales")
                    cols_2 = st.columns(2)
                    ganadores_semi = []
                    perdedores_semi = []
                    for i in range(0, 4, 2):
                        loc, vis = ganadores_4[i], ganadores_4[i+1]
                        with cols_2[i // 2]:
                            def_ws = b_prev.iloc[0][f"WS_{i//2}"] if not b_prev.empty and f"WS_{i//2}" in b_prev.columns else loc
                            ws = st.radio(f"Semifinal {i//2 + 1}", [loc, vis], index=[loc, vis].index(def_ws) if def_ws in [loc, vis] else 0, key=f"radio_s_{i}", disabled=not puede_editar)
                            ganadores_semi.append(ws)
                            perdedores_semi.append(vis if ws == loc else loc)
        
                    st.divider()
                    col_f, col_t = st.columns(2)
                    with col_t:
                        st.subheader("🥉 Tercer Puesto")
                        t3_l, t3_v = perdedores_semi[0], perdedores_semi[1]
                        def_t3 = b_prev.iloc[0]["TercerPuesto"] if not b_prev.empty and "TercerPuesto" in b_prev.columns else t3_l
                        res_t3 = st.selectbox("Ganador Bronce", [t3_l, t3_v], index=[t3_l, t3_v].index(def_t3) if def_t3 in [t3_l, t3_v] else 0, key="sb_t3", disabled=not puede_editar)
                    
                    with col_f:
                        st.subheader("🏆 Gran Final")
                        f_l, f_v = ganadores_semi[0], ganadores_semi[1]
                        def_cam = b_prev.iloc[0]["Campeon"] if not b_prev.empty and "Campeon" in b_prev.columns else f_l
                        campeon = st.selectbox("CAMPEÓN DEL MUNDO", [f_l, f_v], index=[f_l, f_v].index(def_cam) if def_cam in [f_l, f_v] else 0, key="sb_final", disabled=not puede_editar)
                        st.markdown(f"<h2 style='text-align:center; color:#ffd700;'>🥇 {campeon}</h2>", unsafe_allow_html=True)
        
                    st.divider()
                    st.subheader("⚽ 8️⃣ Premios Individuales")
                    clp1, clp2, clp3 = st.columns(3)
                    with clp1:
                        def_pi = b_prev.iloc[0]["Pichichi"] if not b_prev.empty and "Pichichi" in b_prev.columns else ""
                        pichichi = st.text_input("Pichichi (Goleador)", value=def_pi, disabled=not puede_editar)
                    with clp2:
                        def_za = b_prev.iloc[0]["Zamora"] if not b_prev.empty and "Zamora" in b_prev.columns else ""
                        zamora = st.text_input("Zamora (Portero)", value=def_za, disabled=not puede_editar)
                    with clp3:
                        def_mv = b_prev.iloc[0]["MVP"] if not b_prev.empty and "MVP" in b_prev.columns else ""
                        mvp = st.text_input("MVP del Torneo", value=def_mv, disabled=not puede_editar)
        
                    st.divider()
                    
                    # --- NUEVO: CONDICIÓN DEL BOTÓN ---
                    if puede_editar:
                        texto_boton = "👑 GUARDAR BRACKET OFICIAL (ADMIN)" if es_admin else "💾 GUARDAR TODO EL BRACKET Y PREMIOS"
                        if st.button(texto_boton, use_container_width=True, type="primary"):
                            try:
                                datos = {"Usuario": st.session_state.user, "MejoresTerceros": ",".join(seleccion_terceros), "TercerPuesto": res_t3, "Campeon": campeon, "Pichichi": pichichi, "Zamora": zamora, "MVP": mvp}
                                for g in GRUPOS_2026.keys():
                                    datos[f"{g}_1"] = ganadores_grupos[f"{g}_1"]
                                    datos[f"{g}_2"] = ganadores_grupos[f"{g}_2"]
                                    datos[f"{g}_3"] = ganadores_grupos[f"{g}_3"]
                                for i, v in enumerate(ganadores_16): datos[f"W16_{i}"] = v
                                for i, v in enumerate(ganadores_8): datos[f"W8_{i}"] = v
                                for i, v in enumerate(ganadores_4): datos[f"W4_{i}"] = v
                                for i, v in enumerate(ganadores_semi): datos[f"WS_{i}"] = v
        
                                df_b_act = pd.concat([df_b_all[df_b_all['Usuario'] != st.session_state.user], pd.DataFrame([datos])], ignore_index=True)
                                conn.update(worksheet="Brackets", data=df_b_act)
                                
                                log_e = pd.DataFrame([{"Fecha": get_now_madrid().strftime("%Y-%m-%d %H:%M:%S"), "Usuario": st.session_state.user, "Accion": f"🌳 BRACKET: Actualizó su cuadro {'oficial' if es_admin else 'completo'}. Campeón: {campeon}"}])
                                conn.update(worksheet="Logs", data=pd.concat([leer_datos("Logs"), log_e], ignore_index=True))
                                
                                st.success("✅ ¡Bracket y Premios guardados correctamente!")
                                st.balloons()
                                st.cache_data.clear()
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al guardar: {e}")

    
    with tabs[2]: # --- 🔮 PESTAÑA LA GRADA (TENDENCIAS + REVELACIONES) ---
        st.header("👀 Qué han puesto los demás")
        ahora = get_now_madrid()
        # --- ZONA DE EXPLICACIÓN DE REVELACIONES Y LOGS ---
        st.info("""
        ℹ️ **¿Cómo se calculan las puntuaciones visibles en las revelaciones?**
        Los marcadores desplegados a continuación se evalúan automáticamente cuando el Administrador cierra el acta. 
        
        Si el partido es **Esquizo**, verás que los aciertos sumarán el triple en plenos (**3.00 pts**), el doble en signos (**1.00 pto**) o diferencia (**1.50 pts**). ¡Fíjate bien en el tipo de partido en cada tarjeta expandible!
        """)
        
        # Detectamos si es ronda de eliminación (KO)
        es_ronda_ko = any(x in j_global for x in ["Dieciseisavos", "Octavos", "Cuartos", "Semis", "Final"])

        # --- [SABIDURÍA POPULAR: TENDENCIAS] ---
        st.markdown("### 🔮 Sabiduría Popular (Tendencias)")
        preds_j = df_p_all[df_p_all['Jornada'] == j_global]

        if not preds_j.empty:
            with st.expander("📊 Ver tendencias de voto del grupo", expanded=True):
                # Usamos los partidos definidos en JORNADAS para esta jornada
                for loc, vis in JORNADAS[j_global]:
                    m_id = f"{loc}-{vis}"
                    m_preds = preds_j[preds_j['Partido'] == m_id]
                    total = len(m_preds)
                    
                    if total > 0:
                        # 1. Tendencia del Marcador (90 min)
                        v_l = len(m_preds[m_preds['P_L'] > m_preds['P_V']])
                        v_x = len(m_preds[m_preds['P_L'] == m_preds['P_V']])
                        v_v = len(m_preds[m_preds['P_L'] < m_preds['P_V']])
                        p_l, p_x, p_v = (v_l/total)*100, (v_x/total)*100, (v_v/total)*100

                        st.markdown(f"**{m_id}** (Marcador 90')")
                        st.markdown(f"""
                            <div style="display: flex; height: 18px; border-radius: 4px; overflow: hidden; background: #f1f5f9; margin-bottom:10px;">
                                <div style="width: {p_l}%; background: #3b82f6; color: white; font-size: 0.7em; text-align: center; line-height: 18px;" title="Gana {loc}">{p_l:.0f}%</div>
                                <div style="width: {p_x}%; background: #94a3b8; color: white; font-size: 0.7em; text-align: center; line-height: 18px;" title="Empate">{p_x:.0f}%</div>
                                <div style="width: {p_v}%; background: #f59e0b; color: white; font-size: 0.7em; text-align: center; line-height: 18px;" title="Gana {vis}">{p_v:.0f}%</div>
                            </div>
                        """, unsafe_allow_html=True)

                        # 2. Tendencia de Clasificación (Solo en KO)
                        if es_ronda_ko:
                            v_pasa_l = len(m_preds[m_preds['P_Pasa'] == loc])
                            v_pasa_v = len(m_preds[m_preds['P_Pasa'] == vis])
                            p_p_l, p_p_v = (v_pasa_l/total)*100, (v_pasa_v/total)*100
                            
                            st.markdown(f"<small>¿Quién clasifica? (Favorito: {'**'+loc+'**' if p_p_l > p_p_v else '**'+vis+'**'})</small>", unsafe_allow_html=True)
                            st.markdown(f"""
                                <div style="display: flex; height: 8px; border-radius: 10px; overflow: hidden; background: #e2e8f0; margin-bottom: 20px;">
                                    <div style="width: {p_p_l}%; background: #ef4444;"></div>
                                    <div style="width: {p_p_v}%; background: #1e293b;"></div>
                                </div>
                            """, unsafe_allow_html=True)

        st.divider()

        # --- [REVELACIONES: PARTIDOS EMPEZADOS O FINALIZADOS] ---
        df_r_all['Hora_DT'] = pd.to_datetime(df_r_all['Hora_Inicio'], errors='coerce')
        revelados = df_r_all[(df_r_all['Jornada'] == j_global) & ((df_r_all['Finalizado'] == "SI") | (ahora > df_r_all['Hora_DT']))]
        
        if not revelados.empty:
            st.markdown("### ✅ Apuestas Reveladas")
            revelados = revelados.sort_values("Hora_DT", ascending=True)

            for _, match in revelados.iterrows():
                m_id = match['Partido']
                es_final = match['Finalizado'] == "SI"
                res_real = f"{int(match['R_L'])}-{int(match['R_V'])}"
                tipo_p = match['Tipo']
                
                # Info de prórroga para la tabla
                txt_extra = f" (Pasa: {match['R_Pasa']})" if (es_final and match['Hubo_Prorroga'] == "SI") else ""
                estado_tag = "🔴 FINALIZADO" if es_final else "⏱️ EN JUEGO"
                
                with st.expander(f"📊 {m_id} — {estado_tag} (Real: {res_real}{txt_extra})"):
                    preds_match = df_p_all[(df_p_all['Jornada'] == j_global) & (df_p_all['Partido'] == m_id)]
                    
                    if not preds_match.empty:
                        resumen_partido = []
                        for _, p in preds_match.iterrows():
                            # USAMOS LA NUEVA FUNCIÓN DE PUNTOS
                            pts = calcular_puntos_wc(
                                p['P_L'], p['P_V'], match['R_L'], match['R_V'], 
                                tipo_p, p.get('P_Pasa'), match.get('R_Pasa'), 
                                match['Hubo_Prorroga'] == "SI"
                            ) if es_final else "Pte..."
                            
                            fila = {
                                "Jugador": p['Usuario'],
                                "Apostó": f"{int(p['P_L'])}-{int(p['P_V'])}",
                                "Puntos": pts
                            }
                            # Si es KO, mostramos a quién eligió para pasar
                            if es_ronda_ko:
                                fila["Pasa?"] = p.get('P_Pasa', '-')
                            
                            resumen_partido.append(fila)
                        
                        df_resumen = pd.DataFrame(resumen_partido)
                        st.table(df_resumen.sort_values("Puntos", ascending=False) if es_final else df_resumen.sort_values("Jugador"))
        else:
            st.info("Aún no ha empezado ningún partido de esta fase. ¡Las cartas siguen ocultas!")

        # =====================================================================
        # 🔮 NUEVA SECCIÓN: MATRIZ DE SIMILITUD Y ALMAS GEMELAS (CON EFECTO ESCALA)
        # =====================================================================
        st.write("")
        st.markdown("### 🧬 Grado de Afinidad entre Porristas")
        st.caption("¿Quién copia a quién? Medimos la similitud exacta analizando la distancia de goles y el signo de vuestros pronósticos.")

        # 1. Selectores para elegir la vista (General o por Jornada)
        tipo_similitud = st.radio("Ámbito del análisis:", ["Histórico General", "Esta Jornada Específica"], horizontal=True, key="rad_sim_tipo")

        # Función matemática para calcular el % de similitud en un partido
        def calcular_similitud_partido(l1, v1, l2, v2):
            # Si el marcador es exactamente idéntico -> 100%
            if l1 == l2 and v1 == v2:
                return 100.0
            
            # Error absoluto de goles (efecto escala)
            error_goles = abs(l1 - l2) + abs(v1 - v2)
            
            # Verificar si coinciden en el signo (1, X, 2)
            signo1 = (l1 > v1) - (l1 < v1)
            signo2 = (l2 > v2) - (l2 < v2)
            coincide_signo = (signo1 == signo2)
            
            # Base de afinidad por cercanía de goles
            # Cada gol de diferencia resta 15% de afinidad a partir de 100
            afinidad = max(0.0, 100.0 - (error_goles * 15.0))
            
            # Si ni siquiera coinciden en el signo (1X2), penalizamos fuertemente un 50% extra
            if not coincide_signo:
                afinidad = max(0.0, afinidad - 50.0)
                
            return afinidad

        # Obtener jornadas finalizadas o en juego (que tengan alguna predicción)
        jornadas_validas = df_p_all['Jornada'].unique().tolist()

        # Estructura para almacenar resultados de las parejas
        parejas_data = []

        # Generar todas las combinaciones únicas de parejas de jugadores
        if len(u_jugadores) >= 2:
            todas_parejas = list(itertools.combinations(u_jugadores, 2))
            
            for u1, u2 in todas_parejas:
                similitudes_fases = []
                total_partidos_compartidos_historico = 0
                
                # Analizamos fase por fase
                for j_fase in jornadas_validas:
                    # Si el usuario eligió ver una jornada específica y no es esta, nos la saltamos en el bucle
                    if tipo_similitud == "Esta Jornada Específica" and j_fase != j_global:
                        continue
                        
                    # Filtrar las apuestas de ambos usuarios en esta jornada específica
                    p_u1 = df_p_all[(df_p_all['Usuario'] == u1) & (df_p_all['Jornada'] == j_fase)]
                    p_u2 = df_p_all[(df_p_all['Usuario'] == u2) & (df_p_all['Jornada'] == j_fase)]
                    
                    # Cruzar partidos en los que AMBOS hayan apostado
                    df_cruce = pd.merge(p_u1, p_u2, on='Partido', suffixes=('_1', '_2'))
                    
                    if not df_cruce.empty:
                        # Calcular la similitud de cada partido compartido en esta fase
                        valores_partidos = []
                        for row in df_cruce.itertuples():
                            val = calcular_similitud_partido(int(row.P_L_1), int(row.P_V_1), int(row.P_L_2), int(row.P_V_2))
                            valores_partidos.append(val)
                        
                        # Guardamos el promedio de esta fase concreta
                        similitudes_fases.append(np.mean(valores_partidos))
                        total_partidos_compartidos_historico += len(df_cruce)

                # Si comparten datos en el ámbito seleccionado, calculamos su nota final
                if similitudes_fases:
                    # Si es General, hacemos el promedio exacto de los porcentajes de las fases terminadas
                    porcentaje_final = np.mean(similitudes_fases)
                    
                    parejas_data.append({
                        "Pareja": f"👥 **{u1}** & **{u2}**",
                        "Similitud": porcentaje_final,
                        "Partidos": total_partidos_compartidos_historico
                    })

            # 2. Renderizar los Rankings (Top 5 Almas Gemelas y Top 5 Polos Opuestos)
            if parejas_data:
                df_parejas = pd.DataFrame(parejas_data)
                
                col_clones, col_enemigos = st.columns(2, gap="medium")
                
                with col_clones:
                    st.markdown("##### 🐑 Almas Gemelas (Más parecidos)")
                    top_clones = df_parejas.sort_values("Similitud", ascending=False).head(5)
                    
                    for idx, row in enumerate(top_clones.itertuples(), 1):
                        medalla = "🥇" if idx == 1 else ("🥈" if idx == 2 else ("🥉" if idx == 3 else f"#{idx}"))
                        st.markdown(f"""
                            <div style="background:#f0fff4; padding:10px; border-radius:8px; border-left:4px solid #2baf2b; margin-bottom:8px;">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <span style="font-size:0.9em;">{medalla} {row.Pareja}</span>
                                    <span style="font-weight:900; color:#2baf2b; font-size:1.1em;">{row.Similitud:.1f}%</span>
                                </div>
                                <div style="text-align:right;"><small style="color:#666; font-size:0.75em;">{row.Partidos} partidos analizados</small></div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                with col_enemigos:
                    st.markdown("##### ⚔️ Polos Opuestos (Menos parecidos)")
                    top_enemigos = df_parejas.sort_values("Similitud", ascending=True).head(5)
                    
                    for idx, row in enumerate(top_enemigos.itertuples(), 1):
                        icon_demonio = "👹" if idx == 1 else "⚡"
                        st.markdown(f"""
                            <div style="background:#fff5f5; padding:10px; border-radius:8px; border-left:4px solid #ff4b4b; margin-bottom:8px;">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <span style="font-size:0.9em;">{icon_demonio} {row.Pareja}</span>
                                    <span style="font-weight:900; color:#ff4b4b; font-size:1.1em;">{row.Similitud:.1f}%</span>
                                </div>
                                <div style="text-align:right;"><small style="color:#666; font-size:0.75em;">{row.Partidos} partidos analizados</small></div>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Aún no hay suficientes porras guardadas para cruzar las afinidades del grupo.")
        else:
            st.warning("Se necesitan al menos 2 jugadores registrados para activar el buscador de almas gemelas.")

        # --- [PRÓXIMOS PARTIDOS: PÚBLICAS] ---
        st.divider()
        st.markdown("### 🔒 Próximos Partidos (Públicas)")
        p_futuras = df_p_all[(df_p_all['Jornada'] == j_global) & (~df_p_all['Partido'].isin(revelados['Partido'])) & (df_p_all['Publica'] == "SI")]

        if not p_futuras.empty:
            for u in p_futuras['Usuario'].unique():
                if u != st.session_state.user:
                    with st.expander(f"👤 Apuestas de {u}"):
                        cols_mostrar = ['Partido', 'P_L', 'P_V']
                        if es_ronda_ko: cols_mostrar.append('P_Pasa')
                        st.table(p_futuras[p_futuras['Usuario'] == u][cols_mostrar])
                     
    with tabs[3]: # --- 📊 CLASIFICACIÓN PREMIUM ---
            st.header("📊 Clasificación Premium")
            tipo_r = st.radio("Ranking:", ["General", "Jornada"], horizontal=True, key="tipo_ranking_radio")
            pts_l = []
            
            # Cargamos los brackets para saber el campeón elegido por cada uno
            df_b_all = leer_datos("Brackets")
            admin_b = df_b_all[df_b_all['Usuario'] == "ADMIN"]
            r_bracket = admin_b.iloc[0] if not admin_b.empty else None
            
            # 1. Cálculo de puntos (Adaptado 100% al Mundial)
            for u in u_jugadores:
                # Averiguamos a qué selección va este usuario
                campeon_usr = "Ninguno"
                u_bracket = df_b_all[df_b_all['Usuario'] == u]
                if not u_bracket.empty and "Campeon" in u_bracket.columns:
                    campeon_usr = str(u_bracket.iloc[0]["Campeon"])

                # --- EL ARREGLO CRÍTICO AQUÍ ---
                # Rescatamos el 'Ojo con' de PuntosBase para este usuario específico
                pb_r = df_base[df_base['Usuario'] == u]
                ojo_con_usr = str(pb_r['Ojo_con'].values[0]) if not pb_r.empty and 'Ojo_con' in pb_r.columns else "Ninguno"
                if ojo_con_usr.lower() == "nan" or ojo_con_usr == "": ojo_con_usr = "Ninguno"

                p_a = 0.0
                if tipo_r == "General":
                    p_a = safe_float(pb_r['Puntos'].values[0]) if not pb_r.empty else 0.0
                    u_p_h = df_p_all[df_p_all['Usuario'] == u]
                    
                    # Sumamos puntos del Bracket si existe
                    if not u_bracket.empty and r_bracket is not None:
                        p_a += calcular_puntos_bracket(u_bracket.iloc[0], r_bracket)
                else: 
                    u_p_h = df_p_all[(df_p_all['Usuario']==u) & (df_p_all['Jornada']==j_global)]
                
                # Sumamos puntos de los partidos
                for r in u_p_h.itertuples():
                    m = df_r_all[(df_r_all['Jornada']==r.Jornada)&(df_r_all['Partido']==r.Partido)&(df_r_all['Finalizado']=="SI")]
                    if not m.empty: 
                        p_a += calcular_puntos_wc(
                            r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'],
                            getattr(r, 'P_Pasa', None), m.iloc[0].get('R_Pasa'), m.iloc[0].get('Hubo_Prorroga') == "SI"
                        )
                
                # 🔥 PASO CLAVE: Metemos 'Ojo_con' dentro del diccionario para que df_rk lo tenga disponible
                pts_l.append({"Usuario": u, "Puntos": p_a, "Campeon": campeon_usr, "Ojo_con": ojo_con_usr})
            
            df_rk = pd.DataFrame(pts_l).sort_values("Puntos", ascending=False).reset_index(drop=True)
            df_rk['Posicion'] = range(1, len(df_rk)+1)
            
            pts_lider = df_rk.iloc[0]['Puntos'] if not df_rk.empty else 0
            total_usuarios = len(df_rk)
    
            # 2. Renderizado de Tarjetas Premium
            for i, row in df_rk.iterrows():
                pos = row['Posicion']
                pts_actuales = row['Puntos']
                mi_campeon = row['Campeon']
                
                # --- LÓGICA DE ZONAS ---
                zone_class = ""
                if pos <= 3: 
                    zone_class = "zone-champions"
                elif pos >= total_usuarios - 1 and total_usuarios > 3: 
                    zone_class = "zone-danger"
                
                medal_html = f'<span class="pos-badge">#{pos}</span>'
                if pos == 1: medal_html = '<span style="font-size:1.5em;">🥇</span>'
                elif pos == 2: medal_html = '<span style="font-size:1.5em;">🥈</span>'
                elif pos == 3: medal_html = '<span style="font-size:1.5em;">🥉</span>'
    
                f_t = random.choice(FRASES_POR_PUESTO.get(pos if pos <= 7 else 7))
                porcentaje = (pts_actuales / pts_lider * 100) if pts_lider > 0 else 0
    
                # --- ESTÉTICA DE LA SELECCIÓN ---
                # Sacamos los colores de la bandera. Si no ha elegido a nadie aún, gris por defecto.
                colores = COLORES_BANDERAS.get(mi_campeon, ["#cbd5e1", "#94a3b8"])
                estilo_anillo = f"background: linear-gradient(135deg, {colores[0]}, {colores[1]}); padding: 4px; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px {colores[0]}80;"
                
                # Sacamos el logo para ponerlo en pequeñito
                logo_path = get_logo(mi_campeon)
                logo_b64 = ""
                # Truco para incrustar la imagen local en HTML fácilmente
                if logo_path and os.path.exists(logo_path):
                    import base64
                    with open(logo_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode()
                    logo_b64 = f'<img src="data:image/png;base64,{encoded_string}" width="20" style="vertical-align: middle; margin-left: 8px;">'
    
                # --- RENDER CARD ---
                st.markdown(f'<div class="panini-card {zone_class}" style="margin-bottom:15px; padding:15px; border-radius:15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #eee; background: white;">', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([0.5, 1, 2.5, 2])
                
                with c1: # Puesto
                    st.markdown(f'<div style="text-align:center; margin-top:15px;">{medal_html}</div>', unsafe_allow_html=True)
                
                with c2: # Avatar con Anillo Dinámico de su Selección
                    st.markdown(f'<div style="text-align:center;"><div style="{estilo_anillo}">', unsafe_allow_html=True)
                    img = foto_dict.get(row['Usuario'])
                    if img and os.path.exists(str(img)): 
                        st.image(img, width=65) # Ligeramente más pequeño para que destaque el anillo
                    else: 
                        st.markdown("<h2 style='margin:10px 0; background:white; border-radius:50%; width:65px; height:65px; line-height:65px;'>👤</h2>", unsafe_allow_html=True)
                    st.markdown('</div></div>', unsafe_allow_html=True)
                
                with c3: # Nombre, Frase y Selección
                    # Añadimos el logo al lado del nombre
                    st.markdown(f'<h4 style="margin:0; color:#1e293b; display: flex; align-items: center;">{row["Usuario"]} {logo_b64}</h4>', unsafe_allow_html=True)
                    
                    # Mostramos su apuesta para el Mundial y su "Ojo con"
                    if mi_campeon != "Ninguno" and str(mi_campeon).lower() != "nan":
                        st.markdown(f'<small style="color:{colores[0]}; font-weight:bold; font-size:0.75em; text-transform:uppercase;">ESCUDERÍA {mi_campeon}</small><br>', unsafe_allow_html=True)
                    
                    mi_ojo = row.get("Ojo_con", "Ninguno")
                    if mi_ojo != "Ninguno" and str(mi_ojo).lower() != "nan":
                        st.markdown(f'<small style="color:#d97706; font-weight:bold; font-size:0.85em;">👀 Ojo con: {mi_ojo}</small><br>', unsafe_allow_html=True)
                    
                    st.markdown(f'<small style="color:#64748b; font-style:italic;">"{f_t[0]}"</small>', unsafe_allow_html=True)
                    # Barra de progreso con el color de su equipo
                    st.markdown(f"""
                        <div style="width: 80%; background-color: #f1f5f9; border-radius: 10px; height: 6px; margin-top: 5px;">
                            <div style="width: {porcentaje}%; background-color: {colores[0]}; border-radius: 10px; height: 100%;"></div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with c4: # Puntos y Gaps
                    st.markdown(f'<div style="text-align: right;"><span style="font-size: 1.4em; font-weight: 800; color: #1e293b;">{pts_actuales:.2f}</span><br><small style="font-weight:bold; color:#64748b;">PUNTOS</small></div>', unsafe_allow_html=True)
                    
                    if i > 0:
                        gap = df_rk.iloc[i-1]['Puntos'] - pts_actuales
                        if gap > 0:
                            st.markdown(f'<div style="text-align: right;"><small style="color:#f59e0b;">🎯 A {gap:.2f} pts</small></div>', unsafe_allow_html=True)
                    elif pos == 1:
                        st.markdown('<div style="text-align: right;"><small style="color:#ffd700; font-weight:bold;">🏆 LÍDER</small></div>', unsafe_allow_html=True)
    
                st.markdown('</div>', unsafe_allow_html=True)

 
    with tabs[4]: # --- 🏅 PALMARÉS (EDICIÓN MUNDIAL 2026) ---
            st.header("🏅 El Palmarés del Mundial")
            st.caption("Gloria, poder y humillación en el torneo más grande del mundo.")
            
            # --- 1. CONFIGURACIÓN INICIAL ---
            gan_act, perd_act, lider_act = [], [], []
            pts_acumulados = {u: safe_float(df_base[df_base['Usuario'] == u]['Puntos'].values[0]) if not df_base[df_base['Usuario'] == u].empty else 0.0 for u in u_jugadores}
            pts_por_partidos_puros = {u: 0.0 for u in u_jugadores}

            # --- 2. CÁLCULO DE PARTIDOS NORMALES ---
            for j_n in JORNADAS.keys():
                partidos_j = df_r_all[df_r_all['Jornada'] == j_n]
                fin_j = partidos_j[partidos_j['Finalizado'] == "SI"]
                
                if not partidos_j.empty:
                    pts_esta_j = []
                    for u in u_jugadores:
                        u_p = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == j_n)]
                        puntos_fase = 0.0
                        for r in u_p.itertuples():
                            m_real = fin_j[fin_j['Partido'] == r.Partido]
                            if not m_real.empty:
                                puntos_fase += calcular_puntos_wc(
                                    r.P_L, r.P_V, 
                                    m_real.iloc[0]['R_L'], m_real.iloc[0]['R_V'], 
                                    m_real.iloc[0]['Tipo'],
                                    getattr(r, 'P_Pasa', None),
                                    m_real.iloc[0].get('R_Pasa'),
                                    m_real.iloc[0].get('Hubo_Prorroga') == "SI"
                                )
                        pts_esta_j.append({"Usuario": u, "Puntos": puntos_fase})
                        pts_acumulados[u] += puntos_fase 
                        pts_por_partidos_puros[u] += puntos_fase

                    if pts_esta_j and len(fin_j) > 0:
                        df_res = pd.DataFrame(pts_esta_j)
                        max_p, min_p = df_res['Puntos'].max(), df_res['Puntos'].min()
                        max_general = max(pts_acumulados.values())
                        lideres_gen = [u for u, p in pts_acumulados.items() if p == max_general]
                        tag = " (En curso ⏳)" if len(fin_j) < len(partidos_j) else ""
                        gan_act.append((j_n + tag, df_res[df_res['Puntos'] == max_p]['Usuario'].tolist()))
                        perd_act.append((j_n + tag, df_res[df_res['Puntos'] == min_p]['Usuario'].tolist()))
                        lider_act.append((j_n + tag, lideres_gen))

            # --- 3. CÁLCULO SÚPER BRACKET ---
            df_b_all = leer_datos("Brackets")
            
            # Asegurarnos de que no rompe por diferencias de mayúsculas en la BBDD
            if not df_b_all.empty and 'Usuario' in df_b_all.columns:
                df_b_all['Usuario_Lower'] = df_b_all['Usuario'].astype(str).str.strip().str.lower()
                admin_b = df_b_all[df_b_all['Usuario_Lower'] == 'admin']
            else:
                admin_b = pd.DataFrame()
            
            pts_por_bracket_puros = {u: 0.0 for u in u_jugadores}
            
            if admin_b.empty:
                st.info("ℹ️ El ADMIN aún no ha publicado el Bracket Oficial. Los puntos de Bracket están ocultos.")
            else:
                admin_row = admin_b.iloc[0]
                
                # Función super blindada
                def calc_acierto(col, pts, dict_admin, dict_usr):
                    if col in dict_admin and col in dict_usr:
                        val_a = str(dict_admin[col]).strip().lower()
                        val_u = str(dict_usr[col]).strip().lower()
                        if val_a not in ["nan", "none", "", "null", "<na>"] and val_a == val_u:
                            return float(pts)
                    return 0.0

                for u in u_jugadores:
                    usr_b = df_b_all[df_b_all['Usuario'] == u]
                    pts_b = 0.0
                    
                    if not usr_b.empty:
                        usr_row = usr_b.iloc[0]
                        # 1. Grupos (0.5)
                        for g in GRUPOS_2026.keys():
                            for pos in [1, 2, 3]: pts_b += calc_acierto(f"{g}_{pos}", 0.5, admin_row, usr_row)
                        # 2. Octavos (0.5)
                        for i in range(16): pts_b += calc_acierto(f"W16_{i}", 0.5, admin_row, usr_row)
                        # 3. Cuartos (1.0)
                        for i in range(8): pts_b += calc_acierto(f"W8_{i}", 1.0, admin_row, usr_row)
                        # 4. Semis (1.5)
                        for i in range(4): pts_b += calc_acierto(f"W4_{i}", 1.5, admin_row, usr_row)
                        # 5. Finalistas (2.0)
                        for i in range(2): pts_b += calc_acierto(f"WS_{i}", 2.0, admin_row, usr_row)
                        # 6. Campeón (4.0) y Tercero (1.0)
                        pts_b += calc_acierto("Campeon", 4.0, admin_row, usr_row)
                        pts_b += calc_acierto("TercerPuesto", 1.0, admin_row, usr_row)
                        # 7. Premios Individuales (2.0)
                        pts_b += calc_acierto("Pichichi", 2.0, admin_row, usr_row)
                        pts_b += calc_acierto("Zamora", 2.0, admin_row, usr_row)
                        pts_b += calc_acierto("MVP", 2.0, admin_row, usr_row)
                    
                    pts_por_bracket_puros[u] = pts_b
                    pts_acumulados[u] += pts_b

                # Acta del Bracket
                df_res_b = pd.DataFrame([{"Usuario": k, "Puntos": v} for k, v in pts_por_bracket_puros.items()])
                if not df_res_b.empty and df_res_b['Puntos'].max() > 0:
                    max_p_b, min_p_b = df_res_b['Puntos'].max(), df_res_b['Puntos'].min()
                    max_general_b = max(pts_acumulados.values())
                    lideres_gen_b = [us for us, p in pts_acumulados.items() if p == max_general_b]
                    
                    val_campeon = str(admin_row.get('Campeon', '')).strip().lower()
                    es_bracket_terminado = val_campeon not in ["nan", "none", "", "null", "<na>"]
                    tag_b = "" if es_bracket_terminado else " (En curso ⏳)"
                    
                    gan_act.append(("Súper Bracket" + tag_b, df_res_b[df_res_b['Puntos'] == max_p_b]['Usuario'].tolist()))
                    perd_act.append(("Súper Bracket" + tag_b, df_res_b[df_res_b['Puntos'] == min_p_b]['Usuario'].tolist()))
                    lider_act.append(("Súper Bracket" + tag_b, lideres_gen_b))


            # --- NUEVA: TABLA VISUAL DE CLASIFICACIÓN GENERAL ---
            st.subheader("🏆 Clasificación General Oficial")
            datos_tabla = []
            
            # Base (Si existen puntos de inicio en PuntosBase que no sean del mundial)
            puntos_inicio = {u: safe_float(df_base[df_base['Usuario'] == u]['Puntos'].values[0]) if not df_base[df_base['Usuario'] == u].empty else 0.0 for u in u_jugadores}
            
            for u in u_jugadores:
                p_partidos = float(pts_por_partidos_puros.get(u, 0.0))
                p_bracket = float(pts_por_bracket_puros.get(u, 0.0))
                p_base = float(puntos_inicio.get(u, 0.0))
                p_total = p_base + p_partidos + p_bracket
                
                datos_tabla.append({
                    "Usuario": u,
                    "⚽ Puntos Partidos": p_partidos,
                    "🌳 Puntos Bracket": p_bracket,
                    "🌟 TOTAL": p_total
                })
                
            df_clasificacion = pd.DataFrame(datos_tabla).sort_values("🌟 TOTAL", ascending=False)
            st.dataframe(
                df_clasificacion,
                column_config={
                    "⚽ Puntos Partidos": st.column_config.NumberColumn(format="%.2f"),
                    "🌳 Puntos Bracket": st.column_config.NumberColumn(format="%.2f"),
                    "🌟 TOTAL": st.column_config.NumberColumn(format="%.2f")
                },
                use_container_width=True, 
                hide_index=True
            )

            st.divider()

            # --- 🥇 SECCIÓN GANADORES (MEDALLAS POR FASE) ---
            st.subheader("🥇 Héroes del Mundial (Ganadores de Fase)")
            count_g = {}
            for j, us in gan_act:
                if "En curso" not in j: 
                    for u in us: count_g[u] = count_g.get(u, 0) + 1
            
            if count_g:
                df_g = pd.DataFrame(list(count_g.items()), columns=['U', 'V']).sort_values('V', ascending=False)
                c_g = st.columns(4)
                for i, (_, r) in enumerate(df_g.iterrows()):
                    with c_g[i % 4]:
                        st.markdown(f"""<div style="text-align:center; padding:10px; border-radius:10px; background:linear-gradient(135deg, #fff9c4 0%, #ffeb3b 100%); border:2px solid #ffd700; margin-bottom:10px;">
                            <b style="color:#000; font-size:0.85em;">🏆 {r['U']}</b><br><span style="font-size:1.8em; font-weight:900; color:#000;">{int(r['V'])}</span><br><small style="color:#000; font-weight:bold;">MEDALLAS</small></div>""", unsafe_allow_html=True)
            else:
                st.info("Esperando al final de la primera fase para repartir medallas.")

            st.divider()

            # --- 👑 SECCIÓN LÍDERES (TRONO DEL MUNDIAL) ---
            st.subheader("👑 El Trono del Mundial (Líderes Generales)")
            st.caption("Quién ha mandado en la clasificación acumulada en cada etapa.")
            count_l = {}
            for j, us in lider_act:
                for u in us: count_l[u] = count_l.get(u, 0) + 1
            
            if count_l:
                df_l_rank = pd.DataFrame(list(count_l.items()), columns=['U', 'V']).sort_values('V', ascending=False)
                c_l = st.columns(4)
                for i, (_, r) in enumerate(df_l_rank.iterrows()):
                    with c_l[i % 4]:
                        st.markdown(f"""<div style="text-align:center; padding:10px; border-radius:10px; background:linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%); border:2px solid #0ea5e9; margin-bottom:10px;">
                            <b style="color:#0369a1; font-size:0.85em;">👑 {r['U']}</b><br><span style="font-size:1.8em; font-weight:900; color:#0369a1;">{int(r['V'])}</span><br><small style="color:#0369a1; font-weight:bold;">FASES LÍDER</small></div>""", unsafe_allow_html=True)

            st.divider()

            # --- 🦎 SECCIÓN PERDEDORES: EL LAGARTO MUNDIALISTA ---
            st.subheader("🦎 El Lagarto del Mundial")
            count_p = {}
            for j, us in perd_act:
                if "En curso" not in j:
                    for u in us: count_p[u] = count_p.get(u, 0) + 1
            
            if count_p:
                df_p_rank = pd.DataFrame(list(count_p.items()), columns=['U', 'V']).sort_values('V', ascending=False)
                c_p = st.columns(4)
                for i, (_, r) in enumerate(df_p_rank.iterrows()):
                    st_color = "#32cd32" if r['V'] >= 2 else "#6c757d"
                    with c_p[i % 4]:
                        st.markdown(f"""<div style="text-align:center; padding:10px; border-radius:10px; background:#f0fff0; border:2px solid {st_color}; margin-bottom:10px;">
                            <b style="color:#333; font-size:0.85em;">🦎 {r['U']}</b><br><span style="font-size:1.6em; font-weight:900; color:{st_color};">{int(r['V'])}</span><br><small style="color:{st_color}; font-weight:bold;">LAGARTOS</small></div>""", unsafe_allow_html=True)

            # --- 📅 ACTA HISTÓRICA DEL MUNDIAL ---
            st.divider()
            st.subheader("📅 Acta de Guerra: Resultados por Fase")
            if gan_act:
                cronologia = []
                for i in range(len(gan_act)-1, -1, -1):
                    jor = gan_act[i][0]
                    g = gan_act[i][1]
                    p = perd_act[i][1]
                    l = lider_act[i][1]
                    
                    cronologia.append({
                        "Fase / Etapa": jor,
                        "Héroe (🏆)": " & ".join(map(str, g)),
                        "Líder General (👑)": " & ".join(map(str, l)),
                        "Lagarto (🦎)": " & ".join(map(str, p))
                    })
                st.table(pd.DataFrame(cronologia))
            else:
                st.write("Aún no hay actas registradas. El Mundial está por escribir.")
    
    with tabs[5]: # --- 📈 STATS PRO (MUNDIAL EDITION) ---
        sub_tabs = st.tabs(["👤 Análisis Individual", "🌍 Mapa de Continentes", "🔥 Power Ranking", "📉 Evolución"])

        with sub_tabs[0]: # --- ANÁLISIS INDIVIDUAL ---
            u_sel = st.selectbox("Analizar jugador:", u_jugadores, key="sb_stats_pro")
            
            # --- 1. Preparación de datos y Función ADN ---
            def analizar_adn_wc(usuario, df_p, df_r):
                df_m = pd.merge(df_p[df_p['Usuario'] == usuario], df_r[df_r['Finalizado'] == "SI"], on=['Jornada', 'Partido'])
                if df_m.empty: return None, df_m
                
                # Calculamos puntos
                df_m['Pts'] = df_m.apply(lambda x: calcular_puntos_wc(
                    x.P_L, x.P_V, x.R_L, x.R_V, x.Tipo, 
                    getattr(x, 'P_Pasa', None), x.get('R_Pasa'), x.get('Hubo_Prorroga') == "SI"
                ), axis=1)
                
                # Estadísticas de acierto
                ex = len(df_m[df_m.apply(lambda x: x.P_L == x.R_L and x.P_V == x.R_V, axis=1)])
                sig = len(df_m[df_m['Pts'] > 0]) - ex
                fallos = len(df_m) - (ex + sig)
                
                # NUEVO: Medida de "Alejamiento" (Error Absoluto Medio - MAE)
                # ¿Por cuántos goles de media se equivoca este usuario por partido?
                df_m['Error_Goles'] = abs(df_m['P_L'] - df_m['R_L']) + abs(df_m['P_V'] - df_m['R_V'])
                mae = df_m['Error_Goles'].mean()
                
                return {
                    "exactos": ex, "signos": sig, "fallos": fallos,
                    "total": len(df_m), "mae": mae
                }, df_m

            adn, df_m_usuario = analizar_adn_wc(u_sel, df_p_all, df_r_all)
            
            if adn:
                # --- 2. KPIs SUPERIORES ---
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("🎯 Plenos", adn['exactos'])
                c2.metric("⚖️ Signos", adn['signos'])
                pct_acierto = (adn['exactos'] + adn['signos']) / adn['total'] * 100
                c3.metric("📈 Eficiencia", f"{pct_acierto:.1f}%")
                # Explicación del MAE: Menos es mejor
                c4.metric("📏 Desvío de Mira", f"{adn['mae']:.2f} goles", help="Error Absoluto Medio. De media, por cuántos goles te equivocas en el marcador exacto de un partido. ¡Cuanto más cerca de 0, mejor!")
                
                st.divider()
                
                # --- 3. GRÁFICOS PARALELOS: PUNTOS POR GRUPO vs REPARTO DE ACIERTOS ---
                col_g1, col_g2 = st.columns(2)
                
                with col_g1:
                    st.markdown(f"#### 🕸️ Radar de Grupos")
                    st.caption("Puntos conseguidos en cada uno de los 12 grupos.")
                    
                    # Diccionario inverso para saber a qué grupo pertenece cada equipo
                    equipo_a_grupo = {}
                    for g_name, eqs in GRUPOS_2026.items():
                        for eq in eqs:
                            equipo_a_grupo[eq] = g_name.replace("Grupo ", "")
                    
                    # Filtramos solo partidos de fase de grupos y mapeamos a qué grupo pertenece
                    df_grupos_usr = df_m_usuario[df_m_usuario['Jornada'].isin(["Jornada 1", "Jornada 2", "Jornada 3"])].copy()
                    
                    if not df_grupos_usr.empty:
                        # Sacamos el grupo mirando al equipo local
                        df_grupos_usr['Grupo'] = df_grupos_usr['Partido'].apply(lambda x: equipo_a_grupo.get(x.split('-')[0], "K.O."))
                        pts_grupo = df_grupos_usr.groupby('Grupo')['Pts'].sum().reset_index()
                        
                        # Asegurarnos de que salgan todas las letras (de la A a la L) aunque tenga 0 puntos
                        todas_letras = [chr(i) for i in range(65, 77)] # Letras de A a L
                        pts_grupo = pts_grupo.set_index('Grupo').reindex(todas_letras).fillna(0).reset_index()
                        
                        fig_radar = px.line_polar(pts_grupo, r='Pts', theta='Grupo', line_close=True,
                                                  color_discrete_sequence=['#3b82f6'])
                        fig_radar.update_traces(fill='toself')
                        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, showticklabels=True)), height=350)
                        st.plotly_chart(fig_radar, use_container_width=True)
                    else:
                        st.info("No hay datos de fase de grupos cerrados aún.")

                with col_g2:
                    st.markdown(f"#### 🍩 Distribución")
                    st.caption("Balance global entre Plenos, Signos y Fallos.")
                    fig_pie = px.pie(
                        values=[adn['exactos'], adn['signos'], adn['fallos']], 
                        names=['Plenos (Resultado)', 'Signos (1X2)', 'Fallos'], 
                        color_discrete_sequence=['#2baf2b', '#ffd700', '#ff4b4b'],
                        hole=0.4
                    )
                    fig_pie.update_layout(height=350)
                    st.plotly_chart(fig_pie, use_container_width=True)

                st.divider()

                # --- 4. MAPA DE CALOR ---
                st.markdown(f"#### 🔥 Tendencia de Marcadores")
                u_p_stats = df_p_all[df_p_all['Usuario'] == u_sel]
                if not u_p_stats.empty:
                    fig_heat = px.density_heatmap(
                        u_p_stats, x="P_L", y="P_V",
                        labels={'P_L': 'Goles Local (Apostados)', 'P_V': 'Goles Visitante (Apostados)'},
                        color_continuous_scale="Viridis", text_auto=True, nbinsx=6, nbinsy=6
                    )
                    st.plotly_chart(fig_heat, use_container_width=True)
            # --- NUEVO: ORIGEN DE LOS PUNTOS ---
                # 1. Calculamos los puntos puros de los partidos
                pts_partidos = df_m_usuario['Pts'].sum()
                
                # 2. Rescatamos los puntos del bracket
                # OJO: Aquí debes usar la variable o función que ya tengas en tu código 
                # para calcular los puntos del bracket de este usuario (u_sel). 
                # Te lo dejo como "pts_bracket", cámbialo por tu variable real.
                pts_bracket = 0 # <-- SUSTITUYE ESTO por tu cálculo de bracket
                
                pts_totales = pts_partidos + pts_bracket

                if pts_totales > 0:
                    st.write("") # Espaciador
                    st.markdown("#### 🧬 Origen del ADN de Puntos")
                    
                    # Calculamos porcentajes para que quede más pro
                    pct_partidos = (pts_partidos / pts_totales) * 100
                    pct_bracket = (pts_bracket / pts_totales) * 100
                    
                    # Gráfico de barra horizontal apilada con Plotly
                    import plotly.graph_objects as go
                    fig_origen = go.Figure()
                    
                    fig_origen.add_trace(go.Bar(
                        y=['Puntos'], x=[pts_partidos],
                        name=f'Partidos ({pct_partidos:.1f}%)',
                        orientation='h',
                        marker=dict(color='#3b82f6', line=dict(color='white', width=1)),
                        text=f"Partidos: {pts_partidos} pts",
                        textposition='inside',
                        insidetextanchor='middle'
                    ))
                    
                    fig_origen.add_trace(go.Bar(
                        y=['Puntos'], x=[pts_bracket],
                        name=f'Bracket ({pct_bracket:.1f}%)',
                        orientation='h',
                        marker=dict(color='#8b5cf6', line=dict(color='white', width=1)),
                        text=f"Bracket: {pts_bracket} pts",
                        textposition='inside',
                        insidetextanchor='middle'
                    ))
                    
                    fig_origen.update_layout(
                        barmode='stack',
                        height=120, # Muy bajito, tipo barra de progreso
                        margin=dict(l=0, r=0, t=0, b=0),
                        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        showlegend=True,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                    )
                    
                    st.plotly_chart(fig_origen, use_container_width=True)
                # -----------------------------------
            else:
                st.info("Este jugador aún no tiene partidos finalizados para analizar.")

        with sub_tabs[1]: # --- 🌍 EFECTIVIDAD POR CONTINENTE ---
            st.subheader("🌍 Especialista por Continente")
            st.caption("¿En qué confederación eres un experto y en cuál un 'vendehumo'?")
            
            # Diccionario de confederaciones (Ejemplo, habría que completarlo)
            confed = {
                "España": "UEFA", "Argentina": "CONMEBOL", "México": "CONCACAF", 
                "Japón": "AFC", "Marruecos": "CAF", "USA": "CONCACAF", "Brasil": "CONMEBOL"
            }
            
            # Lógica para cruzar datos
            df_m_cont = pd.merge(df_p_all[df_p_all['Usuario'] == u_sel], df_r_all[df_r_all['Finalizado'] == "SI"], on=['Jornada', 'Partido'])
            if not df_m_cont.empty:
                def asignar_confed(partido):
                    loc = partido.split('-')[0]
                    return confed.get(loc, "Otros")
                
                df_m_cont['Confed'] = df_m_cont['Partido'].apply(asignar_confed)
                df_m_cont['Acierto'] = df_m_cont.apply(lambda x: 1 if (np.sign(x.P_L - x.P_V) == np.sign(x.R_L - x.R_V)) else 0, axis=1)
                
                res_cont = df_m_cont.groupby('Confed')['Acierto'].mean().reset_index()
                res_cont['Acierto'] *= 100
                
                fig_cont = px.bar(res_cont, x='Confed', y='Acierto', color='Acierto',
                                 title=f"% de Acierto en el Signo por Confederación",
                                 labels={'Acierto': '% Acierto', 'Confed': 'Confederación'},
                                 color_continuous_scale="RdYlGn")
                st.plotly_chart(fig_cont, use_container_width=True)
            else:
                st.info("Necesitamos partidos finalizados para calcular tu mapa continental.")

        with sub_tabs[2]: # --- 🔥 POWER RANKING ---
            st.subheader("🔥 Power Ranking: Quién llega más fuerte")
            
            # Tomamos las últimas 2 fases (ej. Jornada 3 y Octavos)
            fases_finalizadas = df_r_all[df_r_all['Finalizado'] == "SI"]['Jornada'].unique().tolist()
            num_fases = st.slider("Analizar rendimiento en últimas fases:", 1, 5, 2)
            fases_sel = fases_finalizadas[-num_fases:] if fases_finalizadas else []
            
            if fases_sel:
                st.caption(f"Calculando puntos en: {', '.join(fases_sel)}")
                pwr_data = []
                for u in u_jugadores:
                    pts_periodo = 0.0
                    u_p_pwr = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'].isin(fases_sel))]
                    
                    for r in u_p_pwr.itertuples():
                        m = df_r_all[(df_r_all['Partido'] == r.Partido) & (df_r_all['Finalizado'] == "SI")]
                        if not m.empty:
                            pts_periodo += calcular_puntos_wc(
                                r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'],
                                getattr(r, 'P_Pasa', None), m.iloc[0].get('R_Pasa'), m.iloc[0].get('Hubo_Prorroga') == "SI"
                            )
                    pwr_data.append({"Usuario": u, "Puntos": pts_periodo})
                
                df_pwr = pd.DataFrame(pwr_data).sort_values("Puntos", ascending=False)
                st.plotly_chart(px.bar(df_pwr, x='Usuario', y='Puntos', color='Puntos', color_continuous_scale="Magma"), use_container_width=True)
            else:
                st.info("El Power Ranking se activará tras la primera fase.")

        with sub_tabs[3]: # --- 📉 EVOLUCIÓN ---
            st.subheader("📉 El Gráfico de la Verdad")
            metrica = st.radio("Eje Y:", ["Puntos Acumulados", "Puesto en la General"], horizontal=True, key="metrica_evol")
            
            # Reutilizamos la lógica de evolución con calcular_puntos_wc
            fases_todas = list(JORNADAS.keys())
            historia_wc = []
            pts_tracking = {u: safe_float(df_base[df_base['Usuario'] == u]['Puntos'].values[0]) if not df_base[df_base['Usuario'] == u].empty else 0.0 for u in u_jugadores}
            
            # Punto de partida
            for u, p in pts_tracking.items(): historia_wc.append({"Fase": "Inicio", "Usuario": u, "Puntos": p})
            
            for f in fases_todas:
                res_f = df_r_all[(df_r_all['Jornada'] == f) & (df_r_all['Finalizado'] == "SI")]
                if res_f.empty: continue
                
                for u in u_jugadores:
                    u_p_f = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == f)]
                    ganado_f = 0.0
                    for r in u_p_f.itertuples():
                        m = res_f[res_f['Partido'] == r.Partido]
                        if not m.empty:
                            ganado_f += calcular_puntos_wc(
                                r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'],
                                getattr(r, 'P_Pasa', None), m.iloc[0].get('R_Pasa'), m.iloc[0].get('Hubo_Prorroga') == "SI"
                            )
                    pts_tracking[u] += ganado_f
                    historia_wc.append({"Fase": f, "Usuario": u, "Puntos": float(pts_tracking[u])})
            
            if len(historia_wc) > len(u_jugadores):
                df_evol = pd.DataFrame(historia_wc)
                df_evol['Puesto'] = df_evol.groupby('Fase')['Puntos'].rank(ascending=False, method='min')
                
                fig_evol = px.line(df_evol, x="Fase", y="Puntos" if metrica == "Puntos Acumulados" else "Puesto", 
                                  color="Usuario", markers=True)
                if metrica == "Puesto en la General": fig_evol.update_yaxes(autorange="reversed")
                st.plotly_chart(fig_evol, use_container_width=True)
    
    with tabs[6]: # --- 🏆 DETALLES (LA LUPA DEL VAR) ---
        st.header("🏆 Desglose de Puntos por Partido")
        st.caption(f"Análisis detallado de la fase: **{j_global}**")

        # 1. Filtramos resultados finalizados de la fase seleccionada
        df_rf = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "SI")]

        if not df_rf.empty:
            # 2. Creamos una matriz vacía: Filas (Partidos) x Columnas (Usuarios)
            m_p = pd.DataFrame(index=df_rf['Partido'].unique(), columns=u_jugadores)

            for p_id in m_p.index:
                # Información real del partido (Admin)
                inf = df_rf[df_rf['Partido'] == p_id].iloc[0]
                res_real = f"{int(inf['R_L'])}-{int(inf['R_V'])}"
                if inf.get('Hubo_Prorroga') == "SI":
                    res_real += f" (Pasa: {inf.get('R_Pasa')})"

                for u in u_jugadores:
                    # Predicción del usuario
                    up = df_p_all[(df_p_all['Usuario'] == u) & 
                                  (df_p_all['Jornada'] == j_global) & 
                                  (df_p_all['Partido'] == p_id)]
                    
                    if not up.empty:
                        # --- CÁLCULO CON LÓGICA MUNDIAL ---
                        pts = calcular_puntos_wc(
                            up.iloc[0]['P_L'], 
                            up.iloc[0]['P_V'], 
                            inf['R_L'], 
                            inf['R_V'], 
                            inf['Tipo'],
                            getattr(up.iloc[0], 'P_Pasa', None), 
                            inf.get('R_Pasa'), 
                            inf.get('Hubo_Prorroga') == "SI"
                        )
                        m_p.at[p_id, u] = float(pts)
                    else:
                        m_p.at[p_id, u] = 0.0

            # 3. Formateo y Visualización Premium
            st.markdown("#### Matriz de Puntos")
            
            # Aplicamos un estilo de colores para resaltar los aciertos altos (Plenos/Esquizo)
            df_styled = m_p.astype(float).style.background_gradient(
                cmap="Greens", axis=None
            ).format("{:.2f}")

            st.dataframe(df_styled, use_container_width=True)

            # 4. Leyenda informativa para evitar dudas
            with st.expander("ℹ️ ¿Cómo se han calculado estos puntos?"):
                st.write(f"""
                - **Marcador (90'):** Se compara el resultado real con tu porra.
                - **Pase de Ronda:** Si el acta indica 'Hubo Prórroga: SI', se ha sumado el bonus (+0.5 o +1.0) si acertaste el clasificado.
                - **Tipo de partido:** Los partidos **{inf['Tipo']}** tienen multiplicadores aplicados.
                """)
        else:
            st.info(f"Todavía no hay partidos finalizados en la fase **{j_global}**. ¡Vuelve cuando pite el árbitro!")
            st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHp6Znd6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/fNuXfHoZY3nqE/giphy.gif", width=300)

    with tabs[7]: # --- 🔮 SIMULADOR (EL DESTINO DEL MUNDIAL) ---
        sub_tabs = st.tabs(["📉 Supercomputadora: Destino Final", "🏟️ El Mundial según mis Porros"])
        
        with sub_tabs[0]:
            st.header("📉 Supercomputadora: El Trono del Mundial")
            st.caption("""
                Predicción probabilística basada en Montecarlo (5.000 futuros posibles). 
                Calcula tus opciones de ganar la Porra basándose en tu ritmo de acierto actual, 
                los puntos del Bracket que quedan por repartir y los partidos de eliminación directa.
            """)
            
            # --- BOTÓN DE EJECUCIÓN ---
            if st.button("🚀 LANZAR SIMULACIÓN MUNDIALISTA", use_container_width=True, type="primary"):
                with st.spinner("🔮 El Oráculo está procesando 5.000 finales posibles..."):
                    # Le pasamos df_b_all como cuarto argumento
                    df_sim = simular_temporada_completa(df_hero, df_p_all, df_r_all, df_b_all)
                
                st.success("✅ Simulación completada. Los dioses del fútbol han hablado.")

                # --- 1. MATRIZ DE POSICIONES ---
                st.subheader("🎯 Matriz de Posiciones Finales")
                cols_puestos = [c for c in df_sim.columns if c.startswith("P") and c != "Puesto Medio"]
                
                st.dataframe(
                    df_sim.style.format({c: "{:.1f}%" for c in cols_puestos})
                    .format({"Puesto Medio": "{:.2f}"})
                    .background_gradient(subset=cols_puestos, cmap="YlGn") 
                    .highlight_max(subset=cols_puestos, color="#1e3a8a", axis=0), 
                    use_container_width=True, hide_index=True
                )

                st.divider()

                # --- 2. DASHBOARD DE PREVISIONES ---
                c1, c2 = st.columns(2)
                with c1:
                    fav = df_sim.sort_values("P1", ascending=False).iloc[0]
                    st.markdown(f"""
                        <div style="background:#f0f7ff; padding:20px; border-radius:15px; border-left:8px solid #007bff;">
                            <small style="color:#007bff; font-weight:bold;">🏆 FAVORITO AL TÍTULO DE LA PORRA</small><br>
                            <b style="font-size:1.5em; color:#1e293b;">{fav['Usuario']}</b><br>
                            <span style="font-size:1.1em; color:#1e293b;">{fav['P1']:.1f}% de opciones de ganar.</span>
                        </div>
                    """, unsafe_allow_html=True)

                with c2:
                    col_u = f"P{len(df_sim)}" 
                    lag = df_sim.sort_values(col_u, ascending=False).iloc[0]
                    st.markdown(f"""
                        <div style="background:#fff5f5; padding:20px; border-radius:15px; border-left:8px solid #ff4b4b;">
                            <small style="color:#ff4b4b; font-weight:bold;">🦎 CANDIDATO AL LAGARTO MUNDIALISTA</small><br>
                            <b style="font-size:1.5em; color:#1e293b;">{lag['Usuario']}</b><br>
                            <span style="font-size:1.1em; color:#1e293b;">{lag[col_u]:.1f}% de acabar último.</span>
                        </div>
                    """, unsafe_allow_html=True)

                # --- 3. GRÁFICO DE CAMPEONATO ---
                st.plotly_chart(px.bar(df_sim, x="Usuario", y="P1", color="P1", 
                                      title="Probabilidades de quedar 1º en la Porra (%)",
                                      color_continuous_scale="Viridis", text_auto='.1f'), use_container_width=True)
            
            else:
                st.info("Pulsa el botón para que la Supercomputadora analice los cruces del Mundial.")

        with sub_tabs[1]:
            st.header("🏟️ El Mundial según mis Porros")
            st.markdown("Calculadora en tiempo real: Así quedarían los Grupos y los Dieciseisavos según tus apuestas.")
            
            usr_sim = st.selectbox("Generar simulación basada en:", u_jugadores, key="sb_sim_porros")
            
            if st.button("📊 Generar Simulación de Cuadro", use_container_width=True, type="primary"):
                # 1. Inicializar diccionario con todos los equipos del torneo a 0
                sim_equipos = {}
                for g_equipos in GRUPOS_2026.values():
                    for eq in g_equipos:
                        sim_equipos[eq] = {"Equipo": eq, "PJ": 0, "V": 0, "E": 0, "D": 0, "GF": 0, "GC": 0, "DG": 0, "Pts": 0}
                
                # 2. Filtrar las predicciones del usuario solo para las 3 primeras jornadas
                preds_usr = df_p_all[(df_p_all['Usuario'] == usr_sim) & (df_p_all['Jornada'].isin(["Jornada 1", "Jornada 2", "Jornada 3"]))]
                
                # Calcular resultados virtuales con FILTRO ANTI-ESPIONAJE ESTRICTO (Solo Finalizados)
                for p in preds_usr.itertuples():
                    try:
                        tl, tv = p.Partido.split('-')
                        gl, gv = int(p.P_L), int(p.P_V)
                        
                        match_info = df_r_all[df_r_all['Partido'] == p.Partido]
                        if not match_info.empty:
                            # NUEVO FILTRO: Miramos explícitamente si el Admin lo ha marcado como finalizado
                            esta_finalizado = (match_info.iloc[0]['Finalizado'] == "SI")
                            
                            # Lógica de visibilidad
                            es_mi_simulacion = (usr_sim == st.session_state.user)
                            es_publica = (getattr(p, 'Publica', 'NO') == 'SI')
                            
                            # Solo contamos el partido si es tuyo, si está FINALIZADO o si el rival lo puso Público
                            if es_mi_simulacion or esta_finalizado or es_publica:
                                if tl in sim_equipos and tv in sim_equipos:
                                    sim_equipos[tl]["PJ"] += 1
                                    sim_equipos[tv]["PJ"] += 1
                                    sim_equipos[tl]["GF"] += gl
                                    sim_equipos[tl]["GC"] += gv
                                    sim_equipos[tv]["GF"] += gv
                                    sim_equipos[tv]["GC"] += gl
                                    
                                    if gl > gv:
                                        sim_equipos[tl]["Pts"] += 3; sim_equipos[tl]["V"] += 1; sim_equipos[tv]["D"] += 1
                                    elif gv > gl:
                                        sim_equipos[tv]["Pts"] += 3; sim_equipos[tv]["V"] += 1; sim_equipos[tl]["D"] += 1
                                    else:
                                        sim_equipos[tl]["Pts"] += 1; sim_equipos[tv]["Pts"] += 1; sim_equipos[tl]["E"] += 1; sim_equipos[tv]["E"] += 1
                    except: continue
                
                # Calcular la Diferencia de Goles
                for eq in sim_equipos.keys():
                    sim_equipos[eq]["DG"] = sim_equipos[eq]["GF"] - sim_equipos[eq]["GC"]

                # 3. Extraer y ordenar Grupos
                st.divider()
                st.subheader(f"📋 Clasificación Proyectada de {usr_sim}")
                if usr_sim != st.session_state.user:
                    st.info("🔒 Modo Anti-Espionaje Activo: Solo estás viendo los puntos de los partidos que el Admin ya ha marcado como FINALIZADOS.")
                ganadores_sim = {}
                lista_terceros = []
                cols_g = st.columns(3) 
                
                for idx, (nombre_g, equipos_g) in enumerate(GRUPOS_2026.items()):
                    datos_g = [sim_equipos[eq] for eq in equipos_g]
                    datos_g.sort(key=lambda x: (x["Pts"], x["DG"], x["GF"]), reverse=True)
                    
                    ganadores_sim[f"{nombre_g}_1"] = datos_g[0]["Equipo"]
                    ganadores_sim[f"{nombre_g}_2"] = datos_g[1]["Equipo"]
                    ganadores_sim[f"{nombre_g}_3"] = datos_g[2]["Equipo"]
                    
                    letra = nombre_g.replace("Grupo ", "")
                    tercero_info = datos_g[2].copy()
                    tercero_info["Grupo"] = letra
                    lista_terceros.append(tercero_info)
                    
                    with cols_g[idx % 3]:
                        st.markdown(f"<span style='color:#3b82f6; font-weight:bold;'>{nombre_g.upper()}</span>", unsafe_allow_html=True)
                        df_g = pd.DataFrame(datos_g)[["Equipo", "PJ", "DG", "Pts"]]
                        st.dataframe(df_g, hide_index=True, use_container_width=True)

                # 4. Los Mejores Terceros
                st.divider()
                st.subheader("🎯 Tabla de los 12 Terceros")
                lista_terceros.sort(key=lambda x: (x["Pts"], x["DG"], x["GF"]), reverse=True)
                mejores_8 = lista_terceros[:8]
                
                df_3ros = pd.DataFrame(lista_terceros)[["Grupo", "Equipo", "PJ", "Pts", "DG", "GF"]]
                
                def pintar_clasificados(col):
                    return ['background-color: #dcfce7' if i < 8 else 'background-color: #fee2e2' for i in range(len(col))]
                
                st.dataframe(df_3ros.style.apply(pintar_clasificados, axis=0), hide_index=True, use_container_width=True)

                # 5. Generar Cruces de Dieciseisavos (La Matriz FIFA)
                st.divider()
                st.subheader("⚔️ Consecuencia: Dieciseisavos de Final")
                st.caption("Aplicando la matriz del Anexo C del reglamento FIFA a los 8 mejores terceros clasificados.")
                
                grupos_clasificados = [t["Grupo"] for t in mejores_8]
                clave_matriz = "".join(sorted(grupos_clasificados))
                
                if clave_matriz in MATRIZ_TERCEROS:
                    cruces_3ros = MATRIZ_TERCEROS[clave_matriz]
                    mapa_letra_pais = {t["Grupo"]: t["Equipo"] for t in mejores_8}
                    
                    cruces_16_sim = [
                        (ganadores_sim["Grupo A_2"], ganadores_sim["Grupo B_2"]),
                        (ganadores_sim["Grupo E_1"], mapa_letra_pais[cruces_3ros["1E"]]),
                        (ganadores_sim["Grupo F_1"], ganadores_sim["Grupo C_2"]),
                        (ganadores_sim["Grupo C_1"], ganadores_sim["Grupo F_2"]),
                        (ganadores_sim["Grupo I_1"], mapa_letra_pais[cruces_3ros["1I"]]),
                        (ganadores_sim["Grupo E_2"], ganadores_sim["Grupo I_2"]),
                        (ganadores_sim["Grupo A_1"], mapa_letra_pais[cruces_3ros["1A"]]),
                        (ganadores_sim["Grupo L_1"], mapa_letra_pais[cruces_3ros["1L"]]),
                        (ganadores_sim["Grupo D_1"], mapa_letra_pais[cruces_3ros["1D"]]),
                        (ganadores_sim["Grupo G_1"], mapa_letra_pais[cruces_3ros["1G"]]),
                        (ganadores_sim["Grupo K_2"], ganadores_sim["Grupo L_2"]),
                        (ganadores_sim["Grupo H_1"], ganadores_sim["Grupo J_2"]),
                        (ganadores_sim["Grupo B_1"], mapa_letra_pais[cruces_3ros["1B"]]),
                        (ganadores_sim["Grupo J_1"], ganadores_sim["Grupo H_2"]),
                        (ganadores_sim["Grupo K_1"], mapa_letra_pais[cruces_3ros["1K"]]),
                        (ganadores_sim["Grupo D_2"], ganadores_sim["Grupo G_2"]) 
                    ]
                    
                    cols_c = st.columns(4)
                    for i, (loc, vis) in enumerate(cruces_16_sim):
                        with cols_c[i % 4]:
                            st.markdown(f"""
                            <div style="background:#ffffff; border: 1px solid #e2e8f0; border-left:5px solid #1e293b; padding:15px; margin-bottom:15px; border-radius:10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                                <small style="color:#64748b; font-weight:bold; letter-spacing: 1px;">R32 • Partido {73+i}</small><br>
                                <div style="margin-top:8px;">
                                    <b style="font-size:1.1em; color:#0f172a;">{loc}</b><br>
                                    <span style="color:#cbd5e1; font-weight:900; font-size:0.8em;">VS</span><br>
                                    <b style="font-size:1.1em; color:#0f172a;">{vis}</b>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.error("Error en la matriz: Faltan partidos por disputarse para determinar los cruces oficiales, o la combinación generada aún es incompleta.")
 
    with tabs[8]: # --- 🎲 ORÁCULO (EL DESTINO DE LA FASE) ---
        if usa_oraculo:
            with st.spinner("🔮 El Oráculo está analizando 5.000 futuros posibles..."):
                # Llamamos a la versión del oráculo que simula 90' + Prórrogas
                prob = simular_oraculo(u_jugadores, df_p_all, df_r_all, j_global)
            
            if prob:
                st.subheader(f"🔮 Probabilidades de Victoria: {j_global}")
                st.caption("Análisis en tiempo real de quién ganará esta fase según los partidos que quedan.")
                
                # --- DISEÑO: Gráfico Izquierda | Lista Derecha ---
                col_izq, col_der = st.columns([1.6, 1], gap="medium")

                with col_izq:
                    # --- GRÁFICO DE TENDENCIA ---
                    df_hist = leer_datos("HistoricoOraculo")
                    
                    if not df_hist.empty and 'Jornada' in df_hist.columns:
                        df_hist_j = df_hist[df_hist['Jornada'] == j_global].copy()
                        
                        if not df_hist_j.empty:
                            # Limpieza de datos para el gráfico
                            df_hist_j['Probabilidad'] = pd.to_numeric(df_hist_j['Probabilidad'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
                            df_hist_j['Fecha_DT'] = pd.to_datetime(df_hist_j['Fecha'], errors='coerce')
                            df_hist_j = df_hist_j.sort_values('Fecha_DT')

                            fig_evo = px.line(
                                df_hist_j, x="Fecha_DT", y="Probabilidad", color="Usuario",
                                markers=True, line_shape="spline",
                                color_discrete_sequence=px.colors.qualitative.Pastel
                            )
                            fig_evo.update_layout(
                                yaxis_range=[-2, 102], 
                                hovermode="x unified", 
                                xaxis_title="Evolución durante la jornada",
                                yaxis_title="Opciones de ganar la fase (%)",
                                height=450, 
                                legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5)
                            )
                            st.plotly_chart(fig_evo, use_container_width=True)
                        else:
                            st.info("⌛ Recopilando datos para el gráfico de tendencias...")
                            st.image("https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmNrNjVlaW0xZzM0MWxubDQyZGhla3V4eXVnMHU5eHcwN3NxamRtMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Jap1tdjahS0rm/giphy.gif", width=250)

                with col_der:
                    # --- LISTADO DE SUPERVIVIENTES ---
                    st.markdown("#### 🎯 Supervivientes")
                    
                    # Ordenamos de mayor a menor probabilidad
                    for u, v in sorted(prob.items(), key=lambda x: x[1], reverse=True):
                        vivo = v > 0
                        card_bg = "#f0fff4" if vivo else "#fff5f5"
                        card_border = "#2baf2b" if vivo else "#ff4b4b"
                        
                        # Cálculo del Delta (Trend)
                        delta = 0.0
                        if not df_hist.empty:
                            u_h = df_hist[(df_hist['Usuario'] == u) & (df_hist['Jornada'] == j_global)]
                            if len(u_h) > 1:
                                try:
                                    v_pre = float(str(u_h.iloc[-2]['Probabilidad']).replace(',', '.'))
                                    delta = v - v_pre
                                except: pass
                        
                        color_d = "green" if delta > 0 else "red"
                        icon_d = "▲" if delta > 0 else "▼"
                        
                        # HTML de la tarjeta de probabilidad
                        st.markdown(f"""
                            <div style="background:{card_bg}; padding:12px; border-radius:10px; border-left:5px solid {card_border}; margin-bottom:10px; opacity: {1.0 if vivo else 0.5};">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <span style="font-weight:bold; color:#31333F;">{'🟢' if vivo else '💀'} {u}</span>
                                    <span style="font-size:1.3em; font-weight:900; color:{card_border};">{v:.1f}%</span>
                                </div>
                                <div style="text-align:right; font-size:0.8em; color:{color_d if vivo else '#999'};">
                                    {f'{icon_d} {abs(delta):.1f}%' if vivo and delta != 0 else ('ELIMINADO' if not vivo else 'ESTABLE')}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if vivo:
                            st.progress(min(v/100, 1.0))
                        else:
                            st.divider()

                # --- CELEBRACIÓN DE VICTORIA ---
                if any(v >= 95 for v in prob.values()):
                    virtual_ganador = max(prob, key=prob.get)
                    st.balloons()
                    st.success(f"🏆 El Oráculo ha dictado sentencia: **{virtual_ganador}** tiene pie y medio en el Olimpo.")

        else:
            # Estado cuando hay demasiados partidos o ninguno
            st.info("🔮 El Oráculo está meditando... Se activará cuando queden entre 1 y 3 partidos para cerrar la fase.")
            st.image("https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ2IycHoyZ2pxeG9pdGU0OHYxODdsdzRldzFyd25lZDVwaTkzd3ZoMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/WPtzThAErhBG5oXLeS/giphy.gif", use_container_width=True)
    
    with tabs[9]: # --- ⚙️ PANEL DE CONTROL ADMIN (MUNDIAL 2026) ---
        if st.session_state.rol == "admin":
            st.header("⚙️ Panel de Control de Administrador")
            
            # --- SUB-PESTAÑAS ---
            t_ajustes, t_fotos, t_resultados = st.tabs([
                "⚖️ Ajustes y Bonos",
                "📸 Fotos de Perfil", 
                "⚽ Resultados Oficiales"
            ])

            # --- 1. SUB-PESTAÑA: AJUSTES (Sustituye a Puntos Base) ---
            with t_ajustes:
                st.subheader("⚖️ Gestión de Puntos Extra y Sanciones")
                st.info("Usa este formulario para sumar puntos del Bracket (Campeón, Pichichi) o aplicar sanciones.")
                
                with st.form("form_ajuste_pro"):
                    c1, c2 = st.columns(2)
                    u_target = c1.selectbox("Seleccionar Jugador:", u_jugadores)
                    pts_ajuste = c2.number_input("Puntos a añadir/restar:", value=0.0, step=0.25, help="Valores negativos para sanciones.")
                    concepto = st.text_input("Concepto del ajuste:", placeholder="Ej: Bono acierto Campeón del Mundo (+5pts)")
                    
                    submit_ajuste = st.form_submit_button("⚖️ Aplicar Cambio y Registrar en VAR", use_container_width=True)

                if submit_ajuste:
                    if concepto.strip() == "" or pts_ajuste == 0:
                        st.error("❌ Indica un concepto y una cantidad distinta de 0.")
                    else:
                        # Operación en PuntosBase
                        df_b_copy = df_base.copy()
                        # Asegurar limpieza de datos (comas por puntos)
                        df_b_copy['Puntos'] = pd.to_numeric(df_b_copy['Puntos'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)

                        if u_target in df_b_copy['Usuario'].values:
                            idx = df_b_copy[df_b_copy['Usuario'] == u_target].index
                            df_b_copy.loc[idx, 'Puntos'] += float(pts_ajuste)
                            
                            try:
                                conn.update(worksheet="PuntosBase", data=df_b_copy)
                                
                                # Log de auditoría para el VAR
                                log_entry = pd.DataFrame([{
                                    "Fecha": get_now_madrid().strftime("%Y-%m-%d %H:%M:%S"),
                                    "Usuario": "🛡️ ADMIN",
                                    "Accion": f"⚖️ AJUSTE: {pts_ajuste} pts a {u_target} ({concepto})"
                                }])
                                df_l_act = leer_datos("Logs")
                                conn.update(worksheet="Logs", data=pd.concat([df_l_act, log_entry], ignore_index=True))
                                
                                st.success(f"✅ Aplicado: {u_target} ahora tiene {pts_ajuste} puntos extra.")
                                st.cache_data.clear()
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al actualizar GSheets: {e}")

            # --- 2. SUB-PESTAÑA: FOTOS DE PERFIL ---
            with t_fotos:
                st.subheader("📸 Asignación de Avatares")
                if os.path.exists(PERFILES_DIR):
                    archivos = ["Ninguna"] + sorted([f for f in os.listdir(PERFILES_DIR) if f.endswith(('.jpeg', '.jpg', '.png', '.webp'))])
                    upd_f = []
                    for u in u_jugadores:
                        path_en_db = foto_dict.get(u, "")
                        nombre_actual = os.path.basename(path_en_db) if (isinstance(path_en_db, str) and path_en_db != "") else "Ninguna"
                        
                        col_u, col_sel = st.columns([2, 1])
                        col_u.write(f"Jugador: **{u}**")
                        idx_f = archivos.index(nombre_actual) if nombre_actual in archivos else 0
                        f_sel = col_sel.selectbox(f"Foto para {u}", archivos, index=idx_f, key=f"f_adm_{u}", label_visibility="collapsed")
                        
                        upd_f.append({"Usuario": u, "ImagenPath": f"{PERFILES_DIR}{f_sel}" if f_sel != "Ninguna" else ""})
                    
                    if st.button("🖼️ Guardar Cambios de Galería", use_container_width=True):
                        conn.update(worksheet="ImagenesPerfil", data=pd.DataFrame(upd_f))
                        st.cache_data.clear()
                        st.success("✅ Galería actualizada.")
                        st.rerun()

            # --- 3. SUB-PESTAÑA: RESULTADOS (LÓGICA WC) ---
            with t_resultados:
                st.subheader(f"🏟️ Acta de la Jornada: {j_global}")
                st.caption("Gestiona goles, prórrogas y pases de ronda.")
                
                r_env = []
                h_ops = [datetime.time(h, m).strftime("%H:%M") for h in range(0, 24) for m in [0, 15, 30, 45]]
                # Detectamos si la jornada seleccionada en el sidebar es de eliminación
                es_ko = any(x in j_global for x in ["Dieciseisavos", "Octavos", "Cuartos", "Semis", "Final"])

                for i, (loc, vis) in enumerate(JORNADAS.get(j_global, [])):
                    m_id = f"{loc}-{vis}"
                    prev = df_r_all[(df_r_all['Jornada']==j_global) & (df_r_all['Partido']==m_id)]
                    
                    # Carga de valores existentes
                    rl, rv, fin, tipo = 0, 0, False, "Normal"
                    pro, pasa = "NO", loc
                    f_val, h_val = datetime.datetime(2026, 6, 11).date(), "21:00"

                    if not prev.empty:
                        rl, rv = int(prev.iloc[0]['R_L']), int(prev.iloc[0]['R_V'])
                        fin = prev.iloc[0]['Finalizado'] == "SI"
                        tipo = prev.iloc[0]['Tipo']
                        pro = prev.iloc[0].get('Hubo_Prorroga', "NO")
                        pasa = prev.iloc[0].get('R_Pasa', loc)
                        try:
                            dt = datetime.datetime.strptime(str(prev.iloc[0]['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
                            f_val, h_val = dt.date(), dt.strftime("%H:%M")
                        except: pass

                    with st.expander(f"⚽ {m_id}", expanded=not fin):
                        c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
                        n_tipo = c1.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], index=["Normal", "Doble", "Esquizo"].index(tipo), key=f"at_{i}")
                        n_fecha = c2.date_input("Día", value=f_val, key=f"adate_{i}")
                        n_hora = c3.selectbox("Hora", h_ops, index=h_ops.index(h_val) if h_val in h_ops else 0, key=f"ah_{i}")
                        n_fin = c4.checkbox("¿Finalizado?", value=fin, key=f"afi_{i}")

                        c5, c6, c7, c8 = st.columns([1, 1, 1.5, 1.5])
                        n_rl = c5.number_input("L", 0, 9, rl, key=f"arl_{i}")
                        n_rv = c6.number_input("V", 0, 9, rv, key=f"arv_{i}")
                        
                        n_pro, n_pasa = "NO", ""
                        if es_ko:
                            n_pro = c7.selectbox("¿Hubo Prórroga?", ["NO", "SI"], index=0 if pro == "NO" else 1, key=f"apr_{i}")
                            n_pasa = c8.selectbox("¿Quién clasificó?", [loc, vis], index=[loc, vis].index(pasa) if pasa in [loc, vis] else 0, key=f"aps_{i}")
                        
                        r_env.append({
                            "Jornada": j_global, "Partido": m_id, "Tipo": n_tipo, 
                            "R_L": n_rl, "R_V": n_rv, "Hora_Inicio": f"{n_fecha} {n_hora}:00", 
                            "Finalizado": "SI" if n_fin else "NO",
                            "Hubo_Prorroga": n_pro, "R_Pasa": n_pasa
                        })

                if st.button("🏟️ PUBLICAR RESULTADOS OFICIALES", use_container_width=True, type="primary"):
                    otros = df_r_all[df_r_all['Jornada'] != j_global]
                    df_final = pd.concat([otros, pd.DataFrame(r_env)], ignore_index=True)
                    conn.update(worksheet="Resultados", data=df_final)
                    
                    st.cache_data.clear()
                    st.success("✅ ¡Acta guardada! Los puntos se han recalculado para todos.")
                    st.rerun()
        else:
            st.error("⛔ Acceso restringido al Alto Mando.")
    
    with tabs[10]: # --- 📜 PESTAÑA VAR (EL OJO QUE TODO LO VE) ---
        st.header("🏁 El VAR de la Porra")
        
        # Imagen de cabecera para dar tensión
        st.image("https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExczF4bGVvbmQ3eTVuam44dzExbXl4MDU5cmVsY24zMGdyb2dvNnpjdiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/U4DdzRe7wJP0aPI1Pa/giphy.gif", width=300)
        st.caption("Transparencia total: aquí se registra cada movimiento clave del Mundial.")

        # Usamos tu función blindada leer_datos para traer los logs más frescos
        df_logs = leer_datos("Logs")
        
        if not df_logs.empty:
            # Aseguramos que la fecha sea operable y ordenamos (lo más nuevo arriba)
            df_logs["Fecha"] = pd.to_datetime(df_logs["Fecha"], errors='coerce')
            df_logs = df_logs.sort_values("Fecha", ascending=False)
            
            st.markdown("---")
            
            # Mostramos los últimos 40 movimientos para no saturar la App
            for _, fila in df_logs.head(40).iterrows():
                usuario_log = str(fila['Usuario'])
                accion_txt = str(fila['Accion'])
                es_admin_log = "ADMIN" in usuario_log.upper() or "🛡️" in usuario_log
                
                # --- Lógica de Iconos Dinámicos del Mundial ---
                icon = "📝" # Predicción estándar
                if "⚖️ AJUSTE" in accion_txt: icon = "⚖️"
                if "⚽ OFICIAL" in accion_txt: icon = "🏟️"
                if "🔄 Modificó" in accion_txt: icon = "🔄"
                if "🌳 BRACKET" in accion_txt: icon = "🌳"
                if "🏆" in accion_txt: icon = "🏅"
                
                with st.container():
                    # Columnas: Hora | Usuario | Acción
                    c_time, c_user, c_act = st.columns([1.2, 1.2, 3])
                    
                    # 1. Fecha y Hora (Legible)
                    if pd.notnull(fila['Fecha']):
                        fecha_fmt = fila['Fecha'].strftime("%d/%m %H:%M")
                    else:
                        fecha_fmt = "??/??"
                    c_time.caption(f"🕒 {fecha_fmt}")
                    
                    # 2. Usuario con estilo (Admin vs Jugador)
                    if es_admin_log:
                        c_user.markdown(f"<span style='color:#ff4b4b; font-weight:bold;'>{usuario_log}</span>", unsafe_allow_html=True)
                    else:
                        c_user.markdown(f"**{usuario_log}**")
                    
                    # 3. Cuadro de Acción
                    if es_admin_log:
                        # Los ajustes de puntos o resultados oficiales van en azul/amarillo
                        if "⚖️" in icon:
                            c_act.warning(f"{icon} {accion_txt.replace('⚖️ AJUSTE:', '')}")
                        else:
                            c_act.info(f"{icon} {accion_txt}")
                    else:
                        # Movimientos normales de los jugadores
                        c_act.write(f"{icon} {accion_txt}")
                    
                    st.divider()
        else:
            st.info("El historial está vacío. ¡Que empiece el baile!")
            st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHp6Znd6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/fNuXfHoZY3nqE/giphy.gif", width=200)





