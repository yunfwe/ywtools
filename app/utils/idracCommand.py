#!/usr/bin/env python

import sys
import socket
import dracclient.client
import urllib3;urllib3.disable_warnings()

ips = '''172.16.1.1 172.16.16.1
172.16.1.2 172.16.16.2
172.16.1.3 172.16.16.3
172.16.1.4 172.16.16.4
172.16.1.5 172.16.16.5
172.16.1.6 172.16.16.6
172.16.1.7 172.16.16.7
172.16.1.8 172.16.16.8
172.16.1.9 172.16.16.9
172.16.1.10 172.16.16.10
172.16.1.11 172.16.16.11
172.16.1.12 172.16.16.12
172.16.1.13 172.16.16.13
172.16.1.14 172.16.16.14
172.16.1.15 172.16.16.15
172.16.1.16 172.16.16.16
172.16.1.17 172.16.16.17
172.16.1.18 172.16.16.18
172.16.1.19 172.16.16.19
172.16.1.20 172.16.16.20
172.16.1.21 172.16.16.21
172.16.1.22 172.16.16.22
172.16.1.129 172.16.16.23
172.16.1.130 172.16.16.24
172.16.1.131 172.16.16.25
172.16.1.132 172.16.16.26
172.16.1.161 172.16.16.27
172.16.1.162 172.16.16.28
172.16.1.177 172.16.16.29
172.16.1.178 172.16.16.30
172.16.1.193 172.16.16.31
172.16.1.194 172.16.16.32
172.16.2.1 172.16.16.33
172.16.2.2 172.16.16.34
172.16.2.3 172.16.16.35
172.16.2.4 172.16.16.36
172.16.2.5 172.16.16.37
172.16.2.6 172.16.16.38
172.16.2.7 172.16.16.39
172.16.2.8 172.16.16.40
172.16.2.9 172.16.16.41
172.16.2.10 172.16.16.42
172.16.2.11 172.16.16.43
172.16.2.12 172.16.16.44
172.16.2.13 172.16.16.45
172.16.2.14 172.16.16.46
172.16.2.15 172.16.16.47
172.16.2.16 172.16.16.48
172.16.2.17 172.16.16.49
172.16.2.18 172.16.16.50
172.16.2.19 172.16.16.51
172.16.2.20 172.16.16.52
172.16.2.21 172.16.16.53
172.16.2.22 172.16.16.54
172.16.2.23 172.16.16.55
172.16.2.24 172.16.16.56
172.16.2.25 172.16.16.57
172.16.2.26 172.16.16.58
172.16.2.27 172.16.16.59
172.16.2.28 172.16.16.60
172.16.2.29 172.16.16.61
172.16.2.30 172.16.16.62
172.16.2.31 172.16.16.63
172.16.2.32 172.16.16.64
172.16.2.33 172.16.16.65
172.16.2.34 172.16.16.66
172.16.2.35 172.16.16.67
172.16.2.36 172.16.16.68
172.16.2.37 172.16.16.69
172.16.2.38 172.16.16.70
172.16.2.39 172.16.16.71
172.16.2.40 172.16.16.72
172.16.2.41 172.16.16.73
172.16.2.42 172.16.16.74
172.16.2.43 172.16.16.75
172.16.2.44 172.16.16.76
172.16.2.45 172.16.16.77
172.16.2.46 172.16.16.78
172.16.2.47 172.16.16.79
172.16.2.48 172.16.16.80
172.16.2.49 172.16.16.81
172.16.2.50 172.16.16.82
172.16.2.51 172.16.16.83
172.16.2.52 172.16.16.84
172.16.2.53 172.16.16.85
172.16.2.54 172.16.16.86
172.16.2.55 172.16.16.87
172.16.2.56 172.16.16.88
172.16.2.57 172.16.16.89
172.16.2.129 172.16.16.90
172.16.2.130 172.16.16.91
172.16.2.131 172.16.16.92
172.16.2.132 172.16.16.93
172.16.2.133 172.16.16.94
172.16.2.134 172.16.16.95
172.16.2.135 172.16.16.96
172.16.2.136 172.16.16.97
172.16.2.137 172.16.16.98
172.16.2.138 172.16.16.99
172.16.2.161 172.16.16.100
172.16.2.162 172.16.16.101
172.16.2.177 172.16.16.102
172.16.2.178 172.16.16.103
172.16.2.193 172.16.16.104
172.16.2.194 172.16.16.105
172.16.3.1 172.16.16.106
172.16.3.2 172.16.16.107
172.16.3.3 172.16.16.108
172.16.3.4 172.16.16.109
172.16.3.5 172.16.16.110
172.16.3.6 172.16.16.111
172.16.3.7 172.16.16.112
172.16.3.8 172.16.16.113
172.16.3.9 172.16.16.114
172.16.3.10 172.16.16.115
172.16.3.129 172.16.16.116
172.16.3.130 172.16.16.117
172.16.3.161 172.16.16.118
172.16.3.162 172.16.16.119
172.16.3.177 172.16.16.120
172.16.3.178 172.16.16.121
172.16.3.193 172.16.16.122
172.16.3.194 172.16.16.123
172.16.4.1 172.16.16.124
172.16.4.2 172.16.16.125
172.16.4.3 172.16.16.126
172.16.4.4 172.16.16.127
172.16.4.5 172.16.16.128
172.16.4.6 172.16.16.129
172.16.4.7 172.16.16.130
172.16.4.8 172.16.16.131
172.16.4.9 172.16.16.132
172.16.4.10 172.16.16.133
172.16.4.11 172.16.16.134
172.16.4.12 172.16.16.135
172.16.4.13 172.16.16.136
172.16.4.14 172.16.16.137
172.16.4.129 172.16.16.138
172.16.4.130 172.16.16.139
172.16.4.131 172.16.16.140
172.16.4.161 172.16.16.141
172.16.4.162 172.16.16.142
172.16.4.177 172.16.16.143
172.16.4.178 172.16.16.144
172.16.4.193 172.16.16.145
172.16.4.194 172.16.16.146
172.16.6.1 172.16.16.147
172.16.6.2 172.16.16.148
172.16.6.3 172.16.16.149
172.16.6.4 172.16.16.150
172.16.6.5 172.16.16.151
172.16.6.6 172.16.16.152
172.16.6.7 172.16.16.153
172.16.6.8 172.16.16.154
172.16.6.9 172.16.16.155
172.16.6.10 172.16.16.156
172.16.6.11 172.16.16.157
172.16.6.12 172.16.16.158
172.16.6.129 172.16.16.159
172.16.6.130 172.16.16.160
172.16.6.161 172.16.16.161
172.16.6.162 172.16.16.162
172.16.6.177 172.16.16.163
172.16.6.178 172.16.16.164
172.16.6.193 172.16.16.165
172.16.6.194 172.16.16.166
172.16.7.1 172.16.16.167
172.16.7.2 172.16.16.168
172.16.7.3 172.16.16.169
172.16.7.129 172.16.16.170
172.16.7.130 172.16.16.171
172.16.7.131 172.16.16.172
172.16.7.161 172.16.16.173
172.16.7.162 172.16.16.174
172.16.7.163 172.16.16.175
172.16.7.177 172.16.16.176
172.16.7.178 172.16.16.177
172.16.7.179 172.16.16.178
172.16.7.193 172.16.16.179
172.16.7.194 172.16.16.180
172.16.7.195 172.16.16.181
172.16.8.1 172.16.16.182
172.16.8.2 172.16.16.183
172.16.8.209 172.16.16.184
172.16.8.129 172.16.16.185
172.16.8.161 172.16.16.186
172.16.8.177 172.16.16.187
172.16.8.193 172.16.16.188
172.16.8.225 172.16.16.189
172.16.8.226 172.16.16.190
172.16.9.1 172.16.16.191
172.16.9.2 172.16.16.192
172.16.9.17 172.16.16.193
172.16.10.1 172.16.16.194
172.16.10.2 172.16.16.195
172.16.10.3 172.16.16.196
172.16.10.4 172.16.16.197
172.16.10.5 172.16.16.198
172.16.10.6 172.16.16.199
172.16.10.17 172.16.16.200
172.16.10.18 172.16.16.201
172.16.10.19 172.16.16.202
172.16.10.20 172.16.16.203
172.16.10.21 172.16.16.204
172.16.10.22 172.16.16.205
172.16.10.23 172.16.16.206
172.16.10.24 172.16.16.207
172.16.10.25 172.16.16.208
172.16.10.26 172.16.16.209
172.16.10.33 172.16.16.210
172.17.1.1 172.17.16.1
172.17.1.2 172.17.16.2
172.17.1.3 172.17.16.3
172.17.1.4 172.17.16.4
172.17.1.5 172.17.16.5
172.17.1.6 172.17.16.6
172.17.1.7 172.17.16.7
172.17.1.8 172.17.16.8
172.17.1.9 172.17.16.9
172.17.1.10 172.17.16.10
172.17.1.11 172.17.16.11
172.17.1.12 172.17.16.12
172.17.1.13 172.17.16.13
172.17.1.14 172.17.16.14
172.17.1.15 172.17.16.15
172.17.1.16 172.17.16.16
172.17.1.17 172.17.16.17
172.17.1.18 172.17.16.18
172.17.1.19 172.17.16.19
172.17.1.20 172.17.16.20
172.17.1.21 172.17.16.21
172.17.1.22 172.17.16.22
172.17.1.23 172.17.16.23
172.17.1.24 172.17.16.24
172.17.1.25 172.17.16.25
172.17.1.26 172.17.16.26
172.17.1.27 172.17.16.27
172.17.1.28 172.17.16.28
172.17.1.29 172.17.16.29
172.17.1.30 172.17.16.30
172.17.1.31 172.17.16.31
172.17.1.32 172.17.16.32
172.17.1.33 172.17.16.33
172.17.1.34 172.17.16.34
172.17.1.35 172.17.16.35
172.17.1.36 172.17.16.36
172.17.1.37 172.17.16.37
172.17.1.38 172.17.16.38
172.17.1.39 172.17.16.39
172.17.1.40 172.17.16.40
172.17.1.41 172.17.16.41
172.17.1.42 172.17.16.42
172.17.1.43 172.17.16.43
172.17.1.44 172.17.16.44
172.17.1.129 172.17.16.45
172.17.1.130 172.17.16.46
172.17.1.131 172.17.16.47
172.17.1.132 172.17.16.48
172.17.1.133 172.17.16.49
172.17.1.134 172.17.16.50
172.17.1.135 172.17.16.51
172.17.1.136 172.17.16.52
172.17.1.161 172.17.16.53
172.17.1.162 172.17.16.54
172.17.1.163 172.17.16.55
172.17.1.164 172.17.16.56
172.17.1.177 172.17.16.57
172.17.1.178 172.17.16.58
172.17.1.193 172.17.16.59
172.17.1.194 172.17.16.60
172.17.2.1 172.17.16.61
172.17.2.2 172.17.16.62
172.17.2.3 172.17.16.63
172.17.2.4 172.17.16.64
172.17.2.5 172.17.16.65
172.17.2.6 172.17.16.66
172.17.2.7 172.17.16.67
172.17.2.8 172.17.16.68
172.17.2.9 172.17.16.69
172.17.2.10 172.17.16.70
172.17.2.11 172.17.16.71
172.17.2.12 172.17.16.72
172.17.2.13 172.17.16.73
172.17.2.14 172.17.16.74
172.17.2.15 172.17.16.75
172.17.2.16 172.17.16.76
172.17.2.17 172.17.16.77
172.17.2.18 172.17.16.78
172.17.2.19 172.17.16.79
172.17.2.20 172.17.16.80
172.17.2.21 172.17.16.81
172.17.2.22 172.17.16.82
172.17.2.23 172.17.16.83
172.17.2.24 172.17.16.84
172.17.2.25 172.17.16.85
172.17.2.26 172.17.16.86
172.17.2.27 172.17.16.87
172.17.2.28 172.17.16.88
172.17.2.29 172.17.16.89
172.17.2.30 172.17.16.90
172.17.2.31 172.17.16.91
172.17.2.32 172.17.16.92
172.17.2.33 172.17.16.93
172.17.2.34 172.17.16.94
172.17.2.35 172.17.16.95
172.17.2.36 172.17.16.96
172.17.2.37 172.17.16.97
172.17.2.38 172.17.16.98
172.17.2.39 172.17.16.99
172.17.2.40 172.17.16.100
172.17.2.41 172.17.16.101
172.17.2.42 172.17.16.102
172.17.2.43 172.17.16.103
172.17.2.44 172.17.16.104
172.17.2.45 172.17.16.105
172.17.2.46 172.17.16.106
172.17.2.47 172.17.16.107
172.17.2.48 172.17.16.108
172.17.2.49 172.17.16.109
172.17.2.50 172.17.16.110
172.17.2.51 172.17.16.111
172.17.2.52 172.17.16.112
172.17.2.53 172.17.16.113
172.17.2.54 172.17.16.114
172.17.2.55 172.17.16.115
172.17.2.56 172.17.16.116
172.17.2.57 172.17.16.117
172.17.2.58 172.17.16.118
172.17.2.59 172.17.16.119
172.17.2.60 172.17.16.120
172.17.2.61 172.17.16.121
172.17.2.62 172.17.16.122
172.17.2.63 172.17.16.123
172.17.2.64 172.17.16.124
172.17.2.65 172.17.16.125
172.17.2.66 172.17.16.126
172.17.2.67 172.17.16.127
172.17.2.68 172.17.16.128
172.17.2.69 172.17.16.129
172.17.2.70 172.17.16.130
172.17.2.71 172.17.16.131
172.17.2.72 172.17.16.132
172.17.2.73 172.17.16.133
172.17.2.74 172.17.16.134
172.17.2.75 172.17.16.135
172.17.2.76 172.17.16.136
172.17.2.77 172.17.16.137
172.17.2.78 172.17.16.138
172.17.2.79 172.17.16.139
172.17.2.80 172.17.16.140
172.17.2.81 172.17.16.141
172.17.2.82 172.17.16.142
172.17.2.83 172.17.16.143
172.17.2.84 172.17.16.144
172.17.2.85 172.17.16.145
172.17.2.86 172.17.16.146
172.17.2.87 172.17.16.147
172.17.2.88 172.17.16.148
172.17.2.89 172.17.16.149
172.17.2.90 172.17.16.150
172.17.2.91 172.17.16.151
172.17.2.92 172.17.16.152
172.17.2.93 172.17.16.153
172.17.2.94 172.17.16.154
172.17.2.95 172.17.16.155
172.17.2.96 172.17.16.156
172.17.2.97 172.17.16.157
172.17.2.98 172.17.16.158
172.17.2.99 172.17.16.159
172.17.2.100 172.17.16.160
172.17.2.101 172.17.16.161
172.17.2.102 172.17.16.162
172.17.2.103 172.17.16.163
172.17.2.104 172.17.16.164
172.17.2.105 172.17.16.165
172.17.2.106 172.17.16.166
172.17.2.107 172.17.16.167
172.17.2.108 172.17.16.168
172.17.2.109 172.17.16.169
172.17.2.110 172.17.16.170
172.17.2.111 172.17.16.171
172.17.2.112 172.17.16.172
172.17.2.113 172.17.16.173
172.17.2.114 172.17.16.174
172.17.2.129 172.17.16.175
172.17.2.130 172.17.16.176
172.17.2.131 172.17.16.177
172.17.2.132 172.17.16.178
172.17.2.133 172.17.16.179
172.17.2.134 172.17.16.180
172.17.2.135 172.17.16.181
172.17.2.136 172.17.16.182
172.17.2.137 172.17.16.183
172.17.2.138 172.17.16.184
172.17.2.139 172.17.16.185
172.17.2.140 172.17.16.186
172.17.2.141 172.17.16.187
172.17.2.142 172.17.16.188
172.17.2.143 172.17.16.189
172.17.2.144 172.17.16.190
172.17.2.145 172.17.16.191
172.17.2.146 172.17.16.192
172.17.2.147 172.17.16.193
172.17.2.148 172.17.16.194
172.17.2.161 172.17.16.195
172.17.2.162 172.17.16.196
172.17.2.163 172.17.16.197
172.17.2.164 172.17.16.198
172.17.2.177 172.17.16.199
172.17.2.178 172.17.16.200
172.17.2.193 172.17.16.201
172.17.2.194 172.17.16.202
172.17.3.1 172.17.16.203
172.17.3.2 172.17.16.204
172.17.3.3 172.17.16.205
172.17.3.4 172.17.16.206
172.17.3.5 172.17.16.207
172.17.3.6 172.17.16.208
172.17.3.7 172.17.16.209
172.17.3.8 172.17.16.210
172.17.3.9 172.17.16.211
172.17.3.10 172.17.16.212
172.17.3.11 172.17.16.213
172.17.3.12 172.17.16.214
172.17.3.13 172.17.16.215
172.17.3.14 172.17.16.216
172.17.3.15 172.17.16.217
172.17.3.16 172.17.16.218
172.17.3.17 172.17.16.219
172.17.3.18 172.17.16.220
172.17.3.19 172.17.16.221
172.17.3.20 172.17.16.222
172.17.3.129 172.17.16.223
172.17.3.130 172.17.16.224
172.17.3.131 172.17.16.225
172.17.3.132 172.17.16.226
172.17.3.161 172.17.16.227
172.17.3.162 172.17.16.228
172.17.3.163 172.17.16.229
172.17.3.164 172.17.16.230
172.17.3.177 172.17.16.231
172.17.3.178 172.17.16.232
172.17.4.1 172.17.16.233
172.17.4.2 172.17.16.234
172.17.4.3 172.17.16.235
172.17.4.4 172.17.16.236
172.17.4.5 172.17.16.237
172.17.4.6 172.17.16.238
172.17.4.7 172.17.16.239
172.17.4.8 172.17.16.240
172.17.4.9 172.17.16.241
172.17.4.10 172.17.16.242
172.17.4.11 172.17.16.243
172.17.4.12 172.17.16.244
172.17.4.13 172.17.16.245
172.17.4.14 172.17.16.246
172.17.4.15 172.17.16.247
172.17.4.16 172.17.16.248
172.17.4.17 172.17.16.249
172.17.4.18 172.17.16.250
172.17.4.19 172.17.17.1
172.17.4.20 172.17.17.2
172.17.4.21 172.17.17.3
172.17.4.22 172.17.17.4
172.17.4.23 172.17.17.5
172.17.4.24 172.17.17.6
172.17.4.25 172.17.17.7
172.17.4.26 172.17.17.8
172.17.4.27 172.17.17.9
172.17.4.28 172.17.17.10
172.17.4.129 172.17.17.11
172.17.4.130 172.17.17.12
172.17.4.131 172.17.17.13
172.17.4.132 172.17.17.14
172.17.4.133 172.17.17.15
172.17.4.134 172.17.17.16
172.17.4.161 172.17.17.17
172.17.4.162 172.17.17.18
172.17.4.163 172.17.17.19
172.17.4.164 172.17.17.20
172.17.4.177 172.17.17.21
172.17.4.178 172.17.17.22
172.17.4.193 172.17.17.23
172.17.4.194 172.17.17.24
172.17.6.1 172.17.17.25
172.17.6.2 172.17.17.26
172.17.6.3 172.17.17.27
172.17.6.4 172.17.17.28
172.17.6.5 172.17.17.29
172.17.6.6 172.17.17.30
172.17.6.7 172.17.17.31
172.17.6.8 172.17.17.32
172.17.6.9 172.17.17.33
172.17.6.10 172.17.17.34
172.17.6.11 172.17.17.35
172.17.6.12 172.17.17.36
172.17.6.13 172.17.17.37
172.17.6.14 172.17.17.38
172.17.6.15 172.17.17.39
172.17.6.16 172.17.17.40
172.17.6.17 172.17.17.41
172.17.6.18 172.17.17.42
172.17.6.19 172.17.17.43
172.17.6.20 172.17.17.44
172.17.6.21 172.17.17.45
172.17.6.22 172.17.17.46
172.17.6.23 172.17.17.47
172.17.6.24 172.17.17.48
172.17.6.129 172.17.17.49
172.17.6.130 172.17.17.50
172.17.6.131 172.17.17.51
172.17.6.132 172.17.17.52
172.17.6.161 172.17.17.53
172.17.6.162 172.17.17.54
172.17.6.163 172.17.17.55
172.17.6.164 172.17.17.56
172.17.6.177 172.17.17.57
172.17.6.178 172.17.17.58
172.17.6.179 172.17.17.59
172.17.6.180 172.17.17.60
172.17.6.193 172.17.17.61
172.17.6.194 172.17.17.62
172.17.7.1 172.17.17.63
172.17.7.2 172.17.17.64
172.17.7.3 172.17.17.65
172.17.7.4 172.17.17.66
172.17.7.5 172.17.17.67
172.17.7.6 172.17.17.68
172.17.7.129 172.17.17.69
172.17.7.130 172.17.17.70
172.17.7.131 172.17.17.71
172.17.7.132 172.17.17.72
172.17.7.133 172.17.17.73
172.17.7.134 172.17.17.74
172.17.7.161 172.17.17.75
172.17.7.162 172.17.17.76
172.17.7.163 172.17.17.77
172.17.7.164 172.17.17.78
172.17.7.165 172.17.17.79
172.17.7.166 172.17.17.80
172.17.7.177 172.17.17.81
172.17.7.178 172.17.17.82
172.17.7.179 172.17.17.83
172.17.7.180 172.17.17.84
172.17.7.181 172.17.17.85
172.17.7.182 172.17.17.86
172.17.7.193 172.17.17.87
172.17.7.194 172.17.17.88
172.17.7.195 172.17.17.89
172.17.7.196 172.17.17.90
172.17.7.197 172.17.17.91
172.17.7.198 172.17.17.92
172.17.8.1 172.17.17.93
172.17.8.2 172.17.17.94
172.17.8.3 172.17.17.95
172.17.8.4 172.17.17.96
172.17.8.209 172.17.17.97
172.17.8.210 172.17.17.98
172.17.8.129 172.17.17.99
172.17.8.130 172.17.17.100
172.17.8.161 172.17.17.101
172.17.8.162 172.17.17.102
172.17.8.177 172.17.17.103
172.17.8.178 172.17.17.104
172.17.8.193 172.17.17.105
172.17.8.194 172.17.17.106
172.17.8.225 172.17.17.107
172.17.8.226 172.17.17.108
172.17.9.1 172.17.17.109
172.17.9.2 172.17.17.110
172.17.10.1 172.17.17.111
172.17.10.2 172.17.17.112
172.17.10.3 172.17.17.113
172.17.10.4 172.17.17.114
172.17.10.5 172.17.17.115
172.17.10.6 172.17.17.116
172.17.10.17 172.17.17.117
172.17.10.18 172.17.17.118
172.17.10.19 172.17.17.119
172.17.10.20 172.17.17.120
172.17.10.21 172.17.17.121
172.17.10.22 172.17.17.122
172.17.10.33 172.17.17.123'''

ipc = {x.split()[0]:x.split()[1]  for x in list(set(ips.split('\n')))}

class idrac(object):
    def __init__(self, ip, username='root', password='calvin'):
        self.ip,self.username,self.password = ip,username,password
        self.client = dracclient.client.DRACClient(ip,'root','calvin')

    def ping(self):
        # 如果对端443端口不能连接就不用继续进行了
        s = socket.socket()
        if s.connect_ex((self.ip,443)) == 0:
            return True
        return False

    def getPowerState(self):
        try: return self.client.get_power_state()
        except Exception as e:
            print(str(e))
            return False

    def setPowerState(self,state):
        try:
            if self.client.set_power_state(state) is None:return True
            else: return False
        except: return False

ip = ipc.get(sys.argv[1])
if ip is None:
    print('没有这个主机')
    sys.exit(2)
cli = idrac(ip=ip)
if not cli.ping():
    print("IPMI无法连接")
    sys.exit(1)

if sys.argv[2] in ['ON','on']:
    print(cli.setPowerState('POWER_ON'))
elif sys.argv[2] in ['OFF','off']:
    print(cli.setPowerState('POWER_OFF'))
elif sys.argv[2] in ['REBOOT','reboot']:
    print(cli.setPowerState('REBOOT'))
else:
    print('不支持的操作')