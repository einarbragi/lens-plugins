"""XenoCam for Cinema 4D + Octane  -  v1.3  (single-file plugin)

Install: put this file in your Cinema 4D plugins folder
         (Edit > Preferences > Open Preferences Folder... > plugins), restart.
Use:     select a camera (or nothing) and click Extensions > XenoCam,
         or add the XenoCam tag to a camera from the Tags menu.

One cinematic lens: a classic cine prime set (12-300 mm) whose character
follows the camera's focal length, with an Era dial (modern - classic -
vintage) and a spherical / anamorphic switch. Every control
lives on the XenoCam tag on the camera.

Plugin IDs 1000005, 1000006 (tag) and 1000004 (auto set-up) are from Maxon's
free test range (1000001-1000010); CharacterLens uses 1000007-1000009. Before
sharing it widely, register free permanent IDs at developers.maxon.net.
"""
import base64, os, sys, tempfile, zlib
import c4d
from c4d import gui

PLUGIN_ID = 1000005
VERSION = "1.3"
OCTANE_CAMERA_TAG_ID = 1029524


def _unpack(blob):
    return zlib.decompress(base64.b64decode("".join(blob.split()))).decode("utf-8")


OSL_SOURCE = _unpack("""eNqtW/9z27aS/91/BV4600fJki1Klu3YcTqOHV/ePPe1E/fam8l4OrQEWTxTJENSttVe/vf77C5AApTsfGk1iSGBu4vF7mKxWCx3
d9XJ3/jZ2t1V6n90mp1Fi52sTJTqK3Uf7oz4wU+pVpM41Yuoiicq0WmpZlmhfppUUarf63SqCxX8dHWpgK2LSKXZVHd2gMrYp2qS
RGUJTKKh8iJeaFXqSgULwCWJnqosVdVcq7Msu9Pqam83VrNoESerngqH/dFgoBaLDtN6mGcleJlHRTSpMOosS5LsoWTsCQ/+T+Jt
EiXE5m01P1IP8VSX6hbj3URFoROmM43LKiuqOEt7ahoVd2qSFakuyh6oVH290uoGrMxVlE6Vnt6C32xWpbosj1WSpbcsA6HK5CaF
jhYrwemB9zitVB6nk2U5xxBMJV8WeaLVrIjTW/zbUb9GyRIkogJjJSTDKZO60dWD1pAH/rsTKWt5vi2iI2U+A8hWR6kiSRapuiVB
s+4GO+Na7AFJhwQelcqKvMNQoboHq9GtFkWl0SIr8nk8OVLZPUY28yk/LrX+Q/cwDwvgCJBnN0mglz74XZbqxWK5yMsXTPIiLueQ
JvOrPy7jMkviqZpJL0wh+189ISLHrEF3vqqs4iQhtlm7TM39zGKdwHBmmIF+UMFhPxzDStRsCSRDv8e6gpWcQFFpBek/REUuhvT2
Xherag5NKJ3ApBbLpIrzJNZiSywmFYRAhdBgQPFtCqHVOjgv4nso6GbF0GbhKEhSBe4kIDsYSlb0FIuG8SEUFhNJMEonWsWlilN1
tneuJuASi6MqdLmj/jVTcaUesvSfFaxzkceJJnJicP999fb3q5/fnv3y/vRSVRnUTd1/q0fY+m6qZ7RgvbFC9Mczrw8d6SRZTrV6
lbFH6MOBwKxg6Tvz11vfwbbj2Rbxd5rrolrC4LNllRDpIprGEEUE00xvoR+Ylgh9Ehcw7M6O+jlLVrcwMrNEaK4RkRIAUkCRLdMp
Lc2drVmSESkzynsmfloF0g3aPUUL8yaJoFCohLtr9Kaj6mz9uUU2hokGAq1eqVFny9peoUE/VeHO4Jj7BLHUt+B8uDNQXfXj7z//
S+0qGbojNFzYCN9OyMoCmnKfBiXl3nbwnZZul354xBlhkpVB/biDAagj6gig4WoRPwaYDJjrkQdY5IEzxQH14lEHOJ9YJ28fK3js
qYYDhHOMKsi4wIrOFipdLm7gEvGMjB2rtkCn+Hw42eohk51AoGvpF+nUCDyyEr2xX+6sYA2rE7iiNItLHeQZNEN4WRFEmN7+eDza
B5uMib4br+8Ov8IDdxZ/q+WX84h2NLOqA+YYY/RbH3VJ0/9elvbaU0d3F1dVlhvT+PABjo32AJVEN3AxJ+rFRR+uNH9hhbSAMzgh
I6g7okd07O/Z31hcYE/AwlYngw6H6vq65zDwG22BVb36nuRE4OoF9DmW1sZhx3Zu/RoABpsn7Pu/YLLotIYK/YHCAX9ao73Bpise
nHh7ZqQbC9gapT/yhxnVA5CbqDcvIu8QRzxBwQSoT+Z6cvcme3xR4220EgQ1z1nHWR3MnNDKpJE8qT/Fo/QiGBDVfAYvbM2t2eu/
YnpC8ErCgcaMntHc6FnRvOEYa6NshMs34nxP1CGNQ3315PiHjNE2w/fW37FkDr5cNEYhUfWWtf712uAJvY8XjUV69hY+NfAm4fwX
Alt4F4o+n/UuDPclzI5bzL6L/tDfhHj1EBfJN2G+xWSuTCT9TQTOm7BzI3p7Sbfxf4mT6gnl7LW82974WfWcZUm2LJ51+ybU/6KJ
hm3v9jOfF/4ajV8paq2qb7Pl36JigTD8Ky250fNZVFZfqeNNcj5dIuQLOPZoDnk9RP0R/0bI3XlWCRSNX8qJAkN9zl8N17eZK47g
sTUyhdH+ZygcCj4TQJibLxF5ZuzN8qxUPHv32T3OPzhKT+Ni/ZmQVdWPIuOdwS5UYUOoDbL6qo+N25yZTrPZh+E1hvpT9nraVT5J
bIktIaqwQdwsKx28ECUcAV6IYF/F944brxYUxRPBwbXXPTTdodf98UN4aDsgjYDkFZM8jtG8UuEh2u3tJgD/+CEmPinWLCD/Ytiz
oXYQq20VdgwvENLHIzoky2LN48md+j/KKYR7ak7uDz/GvXAf8p/NaBeGY9n6evGyJXIwjPNZjw4l7iHQ0nM+4VCaQ26GY25G0sBG
6XPAvxD5cCPPwkP+JQkR18hPP4SDaz4h/AnaFOMDlpvhmJuRNGOO/0GbjwEDOQ3IM9CmZkSdVutCvcKGyPSNYRz2OL0w4GZvyM1o
XxrpHI6lkV+hIIQCgqn71LFdvifyzPvOYI943xmMpTnkJhxIM5RGQEIBYbJoDrgZDtap17z3B0yemrE0h9wQeWqG0ghIKCBE3mnG
LfJXD4kjmsEBT3EgM+WpoBlJM/x8E7apG70a6mOPupGqkbFQCGWscG9T0xb8WbaIrOAbZY1dsnZC4y+YSYv6aekaTa18l/cvIruZ
+sWZK5lned/7et7/HXpy32NfOCDjJiXJL5oDNSOxpMHQtMbArIUN9k170B5j2IxBAMYIG4ShOa3LkpW/TzYt4pfOisWiEKCX0uxL
szd+esW2mrbRXyKr1hjOSFD3Bq5b2JfmQJpDaV7KMh4M3EU9avN+pSeO4bRZcZk2Q5qZmJHHY5+BNvV87lA3hGyzaSY+vXbToo6A
y5G78VADIwQhdODRG3szGbV0suaHZU0Zs3zpraV9b0n5Rr+5aVGn44BDfSimN/SM3m98ENvYxULkHfozOjFIPsqJyXq0dw2uuXl5
bXZtOfvFAw4A/KDgjgKhYzSv1Es0bkxAyToM8vqEaN1dd4TAnTvHh5qFIMluAU3pNvoGjHhw3aGMWlD/pkDiug3hpNCO6wzp5S9I
wnHiLSIoJMotek89dLb+lnhNAg0c9535aFVP6C0FxQ5rDtCvAAq0ek3m1lE/0Pe+fO/yCf6I8I6NFMGmuRJQSBAs08qldCaUXtWU
KELsK/0UJbmbWKfzI+U+Ia1Q/BsMUp8RjbpvyH2/do4NIeRziiLiY1+dqC8cihMKzRF/B3UyhYXROVYbP6C4wFpCysXw9lc0JIHf
vdzmBI9NPqfjGLPJInOI9mYtG1w4CYs6eeECTCQlwegwNorIPHmxV2/JMOS+X6nPZDS6kJM3LCIvScALVYrEOi2AN3EkqefAQEiG
OgQxoQ3Rb9d5Dy9jzVkC1SAjVuoAFvqukSWT0OarjKyiLOYpAcNstnmXr9E59dHGxl1JZLFZVvht0Lt+AqKNCZOIbx1MhDBfhjib
NAwT4sXZl+HdhT7ev8OWBsdWg07eY43IsEVk+A1EkPg/O3WIXEbN1OscxBoS4gDBMkj4XWO18hdrOtYTb0Ds+l+Mms991Hz+pahp
RFt0g4ofLWENrbDq3MmafcFMTheVsxbL9mLc5NAGlnCdG2kTfpCEi5g923mzWJpFd1YvOknQuBT4SOsuHNrTN/O2zaFDvZI4F9hm
iMhd5UieTyULJAwNhCMXEJ73wo5LXti/b+BEgudXrpSzwJ1M9D8wDO0rROPKXjrTfoadhS/brJ92LqL5yvuI7+fJ66Nb28tpLXf3
ZX2XtzbUn3X0YDzs9gkfIDb5TPqYBctQODU8saR4ohMHcvy0I6CP8TsCe/g8rFmoDDsabF6dn0ROlPQo2FyRqyRJGwN7zeM0gdMP
bB4MTUaCEKf+Tqo75IPOwRD9SHgZIuYSsaZx9AQNIB5aItJPNPoekeNv336xZu61qRfYpbKQNEWBR7PtTuYF7QYUM7q9E7PKQi8A
thbpxDBOwBAgzLqZRliI4/EgXVCoGNIXR9TVvFDmmtbK4Xj9ttxZ8MmHPZP1Iuts5diIxlEzvxJJNmygrs1ylmxKuUGKjTskWbkt
/YiQGvawxwIf1fEgfcRvBRgamNcyG1pgPBt7n82Ac7qQ+r3MkaAslouAB6Kroh+IroR6PWV6Q693Sz3xMdDDjTRGbq/h+JMUZzjL
1Cp0aE39O4LYaj8zRQdWtPYRnnmLnuPGzcIbsfCGnvCYFOGw8+DPn4qS3HyEOzYyE+2P6rO7BKKfaio8JYcUNv2ayqBFRXJyT1Lx
P0IFyYPxwQYqllRN5dNfO5igyiZZYICsmMbYV62b5RWGAhZkkt3VlUeSwn4mnQykLFmSL4Wp40fnGdg8fkSxAhsngPOo48dx1E+a
lZwwcQOdYg07HSEpmRHdHY8Xk5RwLLE4eO/pGoLHaz5hruPbeaWWaVxhC5qvqI7nA+5GwmuX5qqheW9oervsBVUyUV48wPBd4mGb
kPBtxQdSMx3LBp0rzdEGLHCxDNeuOeKPEhRstP3bgzB74uyk8uCRbjEw6u6GeWKEB7754DnS8aaeYschsWISq4bE33LmrdPqbqjd
RA7u1U6X107oR5h8b0OQzhWOH98ks9+ElgUWOoOxR+ixHvKRtnlG8wBWNcCqBqDTTXuw8ziimzz7vPxYVLRLQKPBVS07Mjj3p2cs
78hAS9KVpec9JVMrV088nZONvSMTe0cm9o5M7N3Kg2BREFfzob8wzpvgzi/yYIHRFRiV5CDS8bi9jxc0X3p2TpZ8DvP3r4nu385m
hu6MzpF1SQdkwNiEQL6Lgi0f9T+zhiUqsOlxGNrZGCRyReIR25MpZlTTIsu58oxLF6WIByVYmSqXN1SUiDJSuB2dumEr7RZXx0+G
k7VvZsBasbUbYV33TUwvaRsc3CGYc78wy04gX6LoD6fhBRWOBjiMqxs6jcN7zVGiI4WKNwWtag4UUU0Jl6zddXmnH3NVF6Xl2UOw
55SFyeke6ebQGdw5/c8zljChkZTppi3U/YMOw4Jtou5hUC2b8mvguric89YKsU5Vle0iPS7Ps6V5fsWaGcM4sO6JIdKV1vP8+XvK
EolZXIDF/8w8/mj10LS6NQkqoMPQ7OUN8q6/cPPVGlKJYMFHapTGaY8jrmzEDSCsLSrnVKZKyhKFVnNQvS24bDlDJDzlZ3RS8bIn
tBRNemQ+bIwOD15zxv/777FeX5NGxm5MY1Jsj7LW4QmO249oPu9Wmx7lFDLk5CE0eYicPIRerUFxlCFgqxrssQ02satTrL586HHy
xgmnMByUOWk6Gg07naw0AiWm+jS6zxTrR54zN5XDTRPi2LLuXZXlKGKHau7lgA9nc8TFjFIdTjmvUqrpVDQpsrJsNOeoJyOmJvaI
+O7RNZhs5T3zPGxBEm7ybt3me6PhIKd5Zo/sMurvcCWYKb6vpN9+fw2anXrHH/hkth0y2w6ZbYfM9mYyVnBXOqZS6CYDiyhA7DjN
UG+YoHqTq3KpzB6y1anrf3L2PmwqeW1RuSeR/F0N8q4G8YVWRpdkcWVkfei2yQF1VeUHfo+/06oBeJeGNoNyQrBrQzCMZ5nJeUyK
sUZMVM7hBoSZwSmeVh9jeAOt2gOtnhhoVQ+0emqglT+QN/XoCqaq5VAactmvG6d48c60JJskEXQNmv+UrJL4bp5aFTvFD5JHSWkH
DsRFYcNZZUtFJaoo3Hjw1DtFWTzztkec4ySp+y8bHWHTPmAV4Y/vh6e3qo40+iItumMhZ4FKkPG12WfsdoSJId/Bg3UJV7y2t8kA
bd9eH2GmLXDy1xvBGwnUaZzgTutcFv08K+I/MlyGJP7bBrSKqFK6wIOzU08eRlsigLtQlLpNOVqj3rm3G2oJ+zkebII2XplrnYJn
htg9sVLmQXQ9iJY/PnTXciTZI2M8pBsvAUL2c0WxdEmr0Y7EMZoHZ6LMNRArTcoLx9WSjoUJrVXUlqd4yWYFYSE/Bwdj3vWAA0QU
4ORwXFHem8DRshqYbDOYFpr8Pai4g4Oq0ciPX+4TswFxILkNknWYCpIe6HliRgMO4lT8lUDVLSqV8q4ZPRdbMuEm70FS4XUp7o5r
2dmjEVJPXJp8baIZg3KhGpTmmN4/Tzz+1GSo3POz6V0w8jnxTHM0/JLzt6XL7TQntGNfvgnq93EQb1HQNuN1At1U0e6w0zmiyLP1
Tg696mPeaHFJImpmlXqv5Mj7O+svaO1QqVF/qm8LjTTIgm4a5WWOnVYAUXy0PqIiWVbkkCsSZbXadLEHPoSaeakEM/USNyDX5ZK2
11wXcBAO9g/dHW8TwRu9guly3ZUwXLZ45JpAMYeIpEdpJDtQzxmn046OlpxpAChHcIeU9a4oXEOP3KK24Vfr8KuN8E1F4QVQ5Fcg
miXHsoQVOr/wil2fvCl+OjxebDJKzhNuC+EuWd22pT5lh3FFa6LHOw1/GTRZismy4DdIeM2zmbSDRT6cCiMiPYebCT9j94m/x+qL
PhjVvPRlDX4WJUk/m802ZxZpZYhLSvCCiwq4UhgmjIMgXsOi3Q9Bzk1WVdmisybrRtAVxFut5EzVWVNK2gA2cg3Xcow89j8kTe+w
6IQFlPbhI0ZaMrRDgD7tcfqk8SjktHxJXxz4Ty1VTFMu0awC+IV0zW4ryatFN2UwTTtijftkjYSxNjXyY0QFhgqyRzAaf6Kg9spM
kwm7z6mIHp3WtTWmaS2zIt8/pczetvIs0DwI5cHK6xxetw1LzrJmN93gabYaIVl1w5FR/gmbxGXebHtIgi4L72DROrbWt3ATNuWh
PYjLreTmHMC9jhOKxugu7givjdWBGtxsEa1wVJlQmgKVDCqJK5h7vQXwZWB9VETEg9LeV0zHtSk7pZQCWhPR/6EDmuK6+cpba1b7
v3+g8hgqBnlJBuAqP6z9xZHtD/18eJv0Tag8BvjoRYOgmKazAZz3QwfoJlwzVZyxh09HmaN2lMnxkmiWpLHtXn92mRbCjU2B5941
eVJMYHtjoGkeDzvekZQ0JHtPe4umMnFYPiqrS5Q9LWzKG2nuFw9ZkUzx5TJ3eY6Lz8G3tElJXbkKhJHK67X0YjW/nQzc4zofwZeH
KppOS7lXddIV5n3pZinVl42/8OlXLh2769eC8sSavr1M79ZpcL628teCHQPF1QvkhLDHBy/kTdMj3HJky9s5quUxTbry6NbrTZh5
6iLJFOP/7MvRc5vurZmU4Nf77KetT1v/D+1Pj7c=""")
TAG_LOGIC = _unpack("""eNrFWntv20YS/5+fYo9FELInE3ZyvSvUuoBsy6nvHMuQlKYHQxAocikx4evIlR8N8t3vN7PLlyS3Ca7AGUhM7s7Mzntmh7Zt+1eZ
5ed+KpS/FuJIiPsT77U1ShJRbwR5pso8qUQS30uRZ0Jt4orBnXeVLMWFr3zXE/ON5MWHMlYS+xuZijhTuYWnhtZkdi2qjR8CjQlJ
MQmUn0mBTVn6RGAgVL6W2CrFQ6w2DBTw7svKivLAT0Qis7XaDEQlsyonsBBwfhYKbG8rEcYVaAbSs6xvmS3AVyLY+KUfKJCN8iTJ
H6oeZdGlLBxfBIlfVXEgghjcFWWcSkvgQDUQJ6+OXh8fizSF0GPwnOb3Wl7xsMkTSUAiKnMoLpF+hm1IC1lzcQ91+Guw9a24JEaH
fQ7yh0yvi8nqgwwU5MqqRq8A6G3CBNtKhmAqz5InHC2zDjmx8SuR5ZkcsF7iSGQyZp0Cj6W47KkKy6BEBAUQ1VMhQ8+ybduK0yIv
lQj+FlrWN2xf4w7i6KfaknFWbJV1e3WzvJxMxan4BFJC2JdHlcoLe4inGT0M8NA/1AlSl/dp+cKs2gODzrCrUvrwt2xNcGfNC9GK
q418koxvHg3meW1p2mtfgEPmco6NSQbi2PuutjPMWtuHWQKkZrhMfUULo8xP87LYxEF9TLsiqv9spfyNeZmZxxqokKXallKsEuiq
otNPRZlvs5CPOeNVOomf9E4mq4o2p80L9s99dWTExeO4lfYs/yg3Ag4qnCMRQEPp00D8VVS5X4jVdrVKtEAMNo3TGu0NQoDW+Tfo
/+xr/vk33mcPcZmwQPxAygvXcO48UjV/tDCr3w1ZsiIcJs4zgui8NdYvEop3FSdKOKFcM3NzvDV2L2FgY/DmGdi327JAdEWdbb3U
BfolXmdSKZakeTaE3/tlqja0Y55qmYI8ybclIqdStVjn9DywPluzn0cX4+kSzj2D4RLI4xhH9+79ZCsrx3Wh7Tv7fQxDqtrcRlw/
ueaEwgrlZPWecpW9sC6vprP5QFyPZnPQbSOkC2VdTyb/Wl6ML0fvruezNrC6/n3iHX+NX2Pnixzz+4Meeez947ueK9LpX+OFx8yt
cT3NuvE7/VI7nZFqx+Ha03pepoGfdS59ZserNPy+O7XkO16kgRvXOW4Z63sNI3+2bibz8fLdBZm0cQXrcnL+bmZWezncQV4+kLNd
25qN58v3Vxdj9o5X3jGxJb7RwKYwUZnJC6psKC3zVz8IX0CvSMc671Ki90UE7rDEBTDXh1U4jJCts/nN8nzy9vbqejwQ9DId41hi
8jxPi5gqGed3csuppOOSPP9oG7zbf2uk8a+3k6nBKp7qkhDAE9md/fuaDLHpU+3Fs+d5tmUtAz8AQ/Drz5ZlhTISywz51qncIduh
lNBfJmzb+5DHmRNsgA3SGxQcUXksrONSbQs2Xlz5SbZNEY01qQLV08nh+IYaqtmFrIKri0YTdVOi+UOB5UKGUKDNVZIHH3Ud5+Ak
9jvB6XpUHYnuR/lUkQya98IdioL5LIjNTvr4zND5FrUXnCFbsOAoxH5SSd4jrBUitojDgViuCZ/4995IRZyXcUEe76AWe/CM88vr
0ZvZkp6WN5ObsRGTfjKQ1uysgrsafHkzejteCJxh224DSp1BrkTWItMP1fg428pdMMM4tRQ4oz6Ec5nbp9CIOC/7ZPRGH/jeLwFJ
ivTQ+TmZ2ycVMUBcMQs3CBBmgNY0T6TUPkGj6TvALEAZCt2l2GGfcrC7j0+dx8euH4IgYbK05lRmBMHl4NkVP52K74WENbVDazcs
1XKDsHHQLEhziiqf2uNMg/UIX0QaWJZbaB4BilQA1AbKsADt+EqVDrYodaI8zBBlnz67Wm90BKPIx0AWSlwx7XFZ5uVwlxTpseYx
irNwmVfJEt7mgAvD5yZW5EgcpXxAHPKuPgOqIADSAH7fHS+8q2pEVwTEZGcRzquzHZahcuA3uyeLPa6w3IQCmxbwRGLur1Fph11H
UryOTtUQhpvPiye1wb2CkbGWF3/g1pQjSETOFaoXFbTUx9aKuDNKIL9y1IDh+v5qRDF71o7OBz3NI6tyjtKwA3Jq+g+NhREWrssO
nOnQwH6jfdpCUHBAQGLGqhd2FcuvwZbCrE4pt2giUonq4HC+6WeVN6g/nFQOOGwk/FXlREnuKwckXVwa9Yvm2xU/ihN59PfhAaV0
ndMh27FvDsQvhMnPHRsXqHO1rHEFDfD1gI4ciFWeJx1QLfspLxs29FHJAVx0QwdQsepwr+P0hKnpVHIfpQuokzupdranWobY1fCs
0bBxhW3YeLhxl0972XuIu1PIwRES4VXAeaggc9JVnG7i5/BxH3dWlMamqlJi4avxMteh2MY40aKUQoQc+xyHTEeTs3+Oz+dLblv0
M19Aunvz0RQuYja7NmN3rdMUmB8wde30O/EV7jvrwSDteR+refVBcCa5A5FFs2X8asy/UCgPIXHsdatR6xsA0DY68yupU5Z7yIeJ
kvVcIqUW5LFvRcd+4Z1EtnghHl2vrBTKuGMf2+2zZ3MT80hxc6zrh/0iJATtj4+NizzwHcOJqralmSD4TcNXJdguh1A42kFOsv4K
owludbgBjKu9BpIQC6mrY0gDCIeHFtQyomi5P4iVRJ9F9GL1stNQ3suygooHNHuR3IY2/ZARO0XHFiGjtZ1s6+lF6CuJ4quksw2N
LNBA3Tybqr4NuVkxY4R29WBui6omIPPibhve1XiLRZMwAfNjhx/kLbTz37XklHykgmfPX1StXEMRbTEMa6ZHA2oXE91p63GT2vh6
9AItQadkOO0IUdXJQjj8p+7h39KV4fDhw9os2iTcg85f4eBc2xKWIVsaSx06r5utGsKvnhfKrlWkdWcMsViIv5wyfkttF0DvWzQc
Ovpff0SKxMUuQg91MqSO4dQkubqTqNmlvd+reG1ppSq/1+Y0UtNc6/fobCmr6QxtWfoqpm2v8ynNwqK90RZSX5Jna7bZfSwfhP8Y
Gwspv0SO1M3VgdTcb0S/+YIxYS2JIVy3BZQEmtvnTvA0PGiT1mCLxYGaq2H30iPTPzjU2z0sXeuMTUZ8u3baSkBo2Er9R8ecUoN4
eRQhRNM1PbjeRa4cPN+/pv0bGssl8W8yxIVvQJHUUozIVpwADvC12G1jIHwULnAOwaGFp9bl9U7l0CCnDMI7uxms9onOeLRq56NN
naX+fKDvMpmop0gYlqe7rS0B7mqQzz3YLmr7EU4n1zVpc4fMHon9wVVTZg5nU9MS7RPqz7uoPJO76LZBNxOL51C7U69dVNNxjG7H
0/m76Xjh/jnJ5ghjKaVyhI5ukfTIw2kr61Qe4TLGsVckW8yIXvLk/GhbNN9AdEwOURuRLKI4SXSBNfMOBIcpiPDAUum9a/qG8guy
AVWSB8yONxSsDxsU7dT/iDmc+R5i+BHmhpXEGXK+MnGuxxQl6oq/wuwfXyvqiU2Bw2iIzzUD437KGxmqv6/7gFRsMyIlw3Z+8Wx+
jXiMUN9fbci+LexDqZfKNID3EijZcL2NvbfgCfPHixj5cO3Yc1JdJmVY9aYwWsmCc06S4PtDZ0rRLfS4bDOvFwjvVKJrd9lj3Pq+
TZOqJdXI2pbd5L0bignFR2/M+lUB2Q09HAJ6Vi34+B68jcLQ2W177pFXV3ESq6fnGOTw1R8e/qDr2egZSx2jGodYORXHjaxfclXo
Sbs/NDo9Pfi5g12T71xdlJ/R4Cxcah02e5OePTihoXa0SpeofS6NIJ0b05JUT+tt2N6QqcyAr/k8KWCL8gntq54AigLzREQQgs6p
Z4J+KbOXimawG5+m1U189C+/4SMXgvAO//RgrlAbh+7AJwvPjJmev4h0rwyNeZZfYZ29uxDMFS7vwuUBXshq4Hd/smW42DPzF96k
mnv5gQvQ7qgLSjzTaZbaZMVh30mplNJkEmEQDs1jMtzLnxXG68GzhviisRmnsD9jaMaEGrNRO/9/zHcUAGfv5vMJf5P61JnjD5tC
1pnoD7tJcdA1ZT3JH4rET1chKpnJ9QFG+bbbHfDvgchHUpPdDBlSLbSTVuslfT8eiJD+LmB4cIBUA9WDu7ezNzzInl7dzq8mLM7b
0c2F/nbdtqFEEXTjvZs5m8eohK3a5gag8Iodh3bdu3Q4ibL9+IDKWzi+vP0Rv7eT2Ryavh1NEUfz8XSnbTuQ+Q8mCnLfjj/hrw5g
7u4faAzhuMZbTfDxeP2/NHDoQQ==""")

# Fallback only (if the XenoCam tag type can't be registered): a Python tag that
# carries just this stub; the logic runs inside the plugin either way.
TAG_CODE = '''"""XenoCam camera tag. The controls are on the XenoCam tab; the logic lives
in the XenoCam plugin, so this tag needs the plugin installed."""
try:
    import xenocam_runtime as _xc
except ImportError:
    _xc = None


def main():
    if _xc is not None:
        _xc.run(op, doc)


def message(msg_type, data):
    if _xc is not None:
        return _xc.message(op, msg_type, data)
    return True
'''

RUNTIME_SRC = r'''
import c4d

_spaces = {}


def _key(op):
    try:
        return ("guid", op.GetGUID())
    except Exception:
        obj = op.GetObject()
        return ("name", obj.GetName() if obj else "", op.GetName())


def _space(op):
    k = _key(op)
    ns = _spaces.get(k)
    if ns is None:
        ns = {"__name__": "xenocam_tag"}
        exec(compile(TAG_LOGIC, "XenoCam tag", "exec"), ns)
        _spaces[k] = ns
    return ns


def run(op, doc):
    ns = _space(op)
    ns["op"], ns["doc"] = op, doc
    ns["main"]()


def message(op, msg_type, data):
    ns = _space(op)
    ns["op"], ns["doc"] = op, op.GetDocument()
    return ns["message"](msg_type, data)
'''


def _install_runtime():
    import types
    mod = types.ModuleType("xenocam_runtime")
    mod.TAG_LOGIC = TAG_LOGIC
    exec(RUNTIME_SRC, mod.__dict__)
    sys.modules["xenocam_runtime"] = mod
    return mod


_xc_runtime = _install_runtime()


# --------------------------------------------------------------- helpers
def _find(node, name):
    for bc, pid, _g in node.GetDescription(c4d.DESCFLAGS_DESC_NONE):
        if bc[c4d.DESC_NAME] == name:
            return bc, pid
    return None, None


def _octane_camera_tag(cam):
    for t in cam.GetTags():
        n = t.GetTypeName().lower()
        if "octane" in n and "camera" in n:
            return t
    try:
        t = c4d.BaseTag(OCTANE_CAMERA_TAG_ID)
        if t:
            cam.InsertTag(t)
            return t
    except Exception:
        pass
    return None


# ------------------------------------------------------ the tag's controls
def _add(tag, name, dtype, parent=None, default=None, mn=None, mx=None, smin=None, smax=None,
         step=None, gui_=None, cycle=None, hide=False, open_=True):
    bc = c4d.GetCustomDataTypeDefault(dtype)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = name
    if parent is not None:
        bc[c4d.DESC_PARENTGROUP] = parent
    if dtype == c4d.DTYPE_GROUP:
        bc[c4d.DESC_COLUMNS] = 1
        bc[c4d.DESC_DEFAULT] = bool(open_)
    for key, val in ((c4d.DESC_MIN, mn), (c4d.DESC_MAX, mx), (c4d.DESC_MINSLIDER, smin),
                     (c4d.DESC_MAXSLIDER, smax), (c4d.DESC_STEP, step)):
        if val is not None:
            bc[key] = val
    if gui_ is not None:
        bc[c4d.DESC_CUSTOMGUI] = gui_
    if cycle is not None:
        cyc = c4d.BaseContainer()
        for k, v in cycle:
            cyc.SetString(k, v)
        bc.SetContainer(c4d.DESC_CYCLE, cyc)
    if hide:
        bc[c4d.DESC_HIDE] = True
    did = tag.AddUserData(bc)
    if default is not None:
        try:
            tag[did] = default
        except Exception:
            pass
    return did


def _old_values(ptag):
    out = {}
    for did, bc in ptag.GetUserDataContainer():
        try:
            dt = did[did.GetDepth() - 1].dtype
        except Exception:
            dt = None
        if dt in (c4d.DTYPE_GROUP, c4d.DTYPE_BUTTON):
            continue
        try:
            out[bc[c4d.DESC_NAME]] = ptag[did]
        except Exception:
            pass
    return out


def build_tag_ui(ptag, old=None):
    """(Re)build the XenoCam controls, keeping any values the tag already had
    (or those of a replaced tag, passed as `old`)."""
    if old is None:
        old = _old_values(ptag)
    for did, _bc in list(ptag.GetUserDataContainer()):
        ptag.RemoveUserData(did)
    # wipe the stored values too: Cinema 4D keeps them by slot number, so a
    # reordered control would otherwise inherit an old value of the wrong type
    try:
        ptag.GetDataInstance().RemoveData(c4d.ID_USERDATA)
    except Exception:
        pass
    R, L, G = c4d.DTYPE_REAL, c4d.DTYPE_LONG, c4d.DTYPE_GROUP
    SL, LSL, BTN = c4d.CUSTOMGUI_REALSLIDER, c4d.CUSTOMGUI_LONGSLIDER, c4d.CUSTOMGUI_BUTTON

    def real(name, parent, d, mn, mx, smin, smax, step=0.01):
        _add(ptag, name, R, parent, d, mn=mn, mx=mx, smin=smin, smax=smax, step=step, gui_=SL)

    top = _add(ptag, "XenoCam", G, c4d.DescID(0))      # its own tab, not "User Data"
    g = _add(ptag, "Lens & focus", G, top)
    _add(ptag, "Fisheye", c4d.DTYPE_BOOL, g, False)
    real("F-stop", g, 2.0, 0.5, 64.0, 1.0, 22.0, 0.1)
    _add(ptag, "Aperture", c4d.DTYPE_STRING, g, "", gui_=getattr(c4d, "CUSTOMGUI_STATICTEXT", None))
    _add(ptag, "Focus Object (if the camera has none)", c4d.DTYPE_BASELISTLINK, g)
    _add(ptag, "Focus distance (cm)", R, g, 200.0, mn=1.0, mx=1000000.0, step=1.0)
    real("Focus breathing", g, 0.0, -3.0, 3.0, 0.0, 1.5)

    g = _add(ptag, "Look", G, top)
    real("Character", g, 1.0, 0.0, 3.0, 0.0, 2.0)
    real("Era (0 modern, 0.5 classic, 1 vintage)", g, 0.5, 0.0, 1.0, 0.0, 1.0)
    _add(ptag, "Format", L, g, 0, gui_=c4d.CUSTOMGUI_CYCLE, cycle=[(0, "Spherical"), (1, "Anamorphic")])
    real("Anamorphic squeeze", g, 2.0, 1.0, 3.0, 1.0, 2.0)
    _add(ptag, "Reset look", c4d.DTYPE_BUTTON, g, gui_=BTN)

    g = _add(ptag, "Bokeh", G, top)
    _add(ptag, "Aperture blades (0 = round)", L, g, 8, mn=0, mx=32, smin=0, smax=16, step=1, gui_=LSL)
    real("Blade roundness", g, 0.75, 0.0, 1.0, 0.0, 1.0)
    real("Cat-eye", g, 1.0, 0.0, 3.0, 0.0, 2.0)
    real("Bokeh rim (- creamy, + soap bubble)", g, 0.0, -1.0, 1.0, -1.0, 1.0)

    g = _add(ptag, "Glow & edges", G, top)
    real("Glow", g, 1.0, 0.0, 5.0, 0.0, 3.0)
    real("Haze", g, 1.0, 0.0, 5.0, 0.0, 3.0)
    real("Swirl", g, 1.0, 0.0, 5.0, 0.0, 3.0)
    real("Edge softness", g, 1.0, 0.0, 5.0, 0.0, 3.0)
    real("Distortion", g, 1.0, -3.0, 5.0, 0.0, 3.0)
    real("Focus plane tilt (deg)", g, 0.0, -45.0, 45.0, -10.0, 10.0, 0.1)

    g = _add(ptag, "Colour", G, top)
    real("Fringing", g, 1.0, 0.0, 10.0, 0.0, 3.0)
    real("Purple fringing", g, 1.0, 0.0, 10.0, 0.0, 3.0)
    real("Vignette", g, 1.0, 0.0, 3.0, 0.0, 2.0)
    real("Warmth", g, 0.0, -1.0, 1.0, -1.0, 1.0)
    real("Edge colour cast", g, 1.0, 0.0, 5.0, 0.0, 3.0)

    g = _add(ptag, "Tools", G, top)
    _add(ptag, "Compile shader", c4d.DTYPE_BUTTON, g, gui_=BTN)
    _add(ptag, "Copy shader code", c4d.DTYPE_BUTTON, g, gui_=BTN)
    _add(ptag, "Save shader to a folder...", c4d.DTYPE_BUTTON, g, gui_=BTN)

    if "Focus Object" in old:                    # renamed in 1.3
        old.setdefault("Focus Object (if the camera has none)", old.pop("Focus Object"))
    for gone in ("Full character at", "Aperture", "Widest aperture"):
        old.pop(gone, None)
    anamorphic = bool(old.get("Format", 0))
    for did, bc in ptag.GetUserDataContainer():
        name = bc[c4d.DESC_NAME]
        if name in old and old[name] is not None:
            try:
                ptag[did] = old[name]
            except Exception:
                pass
        if name == "Anamorphic squeeze" and not anamorphic:
            bc[c4d.DESC_HIDE] = True
            ptag.SetUserDataContainer(did, bc)


def _cam_focus_object(cam):
    """The Focus Object set in the camera's own Object settings, if any."""
    for attr in ("CAMERAOBJECT_FOCUSOBJECT", "CAMERAOBJECT_TARGETOBJECT"):
        pid = getattr(c4d, attr, None)
        if pid is None:
            continue
        try:
            obj = cam[pid]
        except Exception:
            obj = None
        if isinstance(obj, c4d.BaseObject):
            return obj
    return None


def _run_before_octane(doc, cam, ptag):
    """The XenoCam tag must run before the Octane Camera tag, or Octane reads
    the focus distance from the previous update. First on the camera, early in
    the expression pass (still after animation)."""
    if cam.GetFirstTag() is not ptag:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, cam)
        ptag.Remove()
        cam.InsertTag(ptag)
    if ptag.GetType() != c4d.Tpython:
        return                                   # the XenoCam tag sets its own priority
    try:
        pd = ptag[c4d.EXPRESSION_PRIORITY]
        pd.SetPriorityValue(c4d.PRIORITYVALUE_MODE, c4d.CYCLE_EXPRESSION)
        pd.SetPriorityValue(c4d.PRIORITYVALUE_PRIORITY, -100)
        ptag[c4d.EXPRESSION_PRIORITY] = pd
    except Exception:
        pass


# ------------------------------------------------------ set up a camera
def _status(text):
    print("XenoCam: " + text.replace("\n", " "))
    try:
        (getattr(c4d.gui, "StatusSetText", None) or c4d.StatusSetText)("XenoCam: " + text.split("\n")[0])
    except Exception:
        pass


def _camera_from_view(doc):
    """A new camera where the viewport is looking from."""
    cam = c4d.BaseObject(c4d.Ocamera)
    cam.SetName("Octane Camera")
    bd = doc.GetActiveBaseDraw()
    view = bd.GetSceneCamera(doc) if bd is not None else None
    if view is not None:
        cam.SetMg(view.GetMg())
        try:
            cam[c4d.CAMERA_FOCUS] = view[c4d.CAMERA_FOCUS]
        except Exception:
            pass
    doc.InsertObject(cam)
    doc.AddUndo(c4d.UNDOTYPE_NEW, cam)
    return cam


def _selected_camera(doc):
    cam = doc.GetActiveObject()
    if cam is not None and cam.CheckType(c4d.Ocamera):
        return cam
    tag = doc.GetActiveTag()
    obj = tag.GetObject() if tag is not None else None
    if obj is not None and obj.CheckType(c4d.Ocamera):
        return obj
    return None


def setup_camera(doc, cam=None):
    """One click: set up the selected camera, or make a new one from the view."""
    doc.StartUndo()
    report = []
    if cam is None:
        cam = _selected_camera(doc)
    if cam is None:
        cam = _camera_from_view(doc)
        report.append("new camera '%s' made from the view" % cam.GetName())
    otag = _octane_camera_tag(cam)
    if otag is None:
        doc.EndUndo()
        _status("no Octane Camera tag could be added to '%s' - is Octane installed?" % cam.GetName())
        return
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, otag)

    bc, pid = _find(otag, "Camera type")
    if pid is not None:
        for k, v in bc.GetContainer(c4d.DESC_CYCLE):
            if isinstance(v, str) and v.strip().lower() == "osl":
                otag[pid] = k
    otag.Message(c4d.MSG_UPDATE)

    ok = False
    _b, code_pid = _find(otag, "Code")
    if code_pid is not None:
        try:
            otag.SetParameter(code_pid, OSL_SOURCE, c4d.DESCFLAGS_SET_NONE)
            got = otag.GetParameter(code_pid, c4d.DESCFLAGS_GET_NONE)
            ok = isinstance(got, str) and got.strip()[:40] == OSL_SOURCE.strip()[:40]
        except Exception:
            ok = False
    if ok:
        bd = doc.GetActiveBaseDraw()
        if bd is not None:
            bd.SetSceneCamera(cam)
        _b, comp_pid = _find(otag, "Compile")
        if comp_pid is not None:
            try:
                c4d.CallButton(otag, comp_pid[comp_pid.GetDepth() - 1].id)
            except Exception as e:
                print("XenoCam: Compile button failed:", e)
        report.append("shader set; Live Viewer restarted to compile it")
    else:
        c4d.CopyStringToClipboard(OSL_SOURCE)
        report.append("could not fill the OSL Code field - the shader is on your clipboard: paste it into "
                      "the OSL Camera's Code field and press Compile")

    # the XenoCam tag: the plugin's own tag type, or a Python tag if that type
    # couldn't be registered; an old Python XenoCam tag is replaced (settings kept)
    ptag, old_py = None, None
    for t in cam.GetTags():
        if t.GetType() == TAG_ID:
            ptag = t
        elif t.GetType() == c4d.Tpython and t.GetName() == "XenoCam":
            old_py = t
    old_values = None
    if ptag is None and _TAG_OK:
        ptag = c4d.BaseTag(TAG_ID)
        ptag.SetName("XenoCam")
        cam.InsertTag(ptag)
        doc.AddUndo(c4d.UNDOTYPE_NEW, ptag)
        if old_py is not None:
            old_values = _old_values(old_py)
            doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ, old_py)
            old_py.Remove()
            report.append("old Python XenoCam tag replaced (settings kept)")
        else:
            report.append("XenoCam tag added")
    elif ptag is None:
        ptag = old_py
        if ptag is None:
            ptag = c4d.BaseTag(c4d.Tpython)
            ptag.SetName("XenoCam")
            cam.InsertTag(ptag)
            doc.AddUndo(c4d.UNDOTYPE_NEW, ptag)
            report.append("XenoCam tag added")
        else:
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, ptag)
            report.append("XenoCam tag updated (settings kept)")
        ptag[c4d.TPYTHON_CODE] = TAG_CODE
        icon_pid = getattr(c4d, "ID_BASELIST_ICON_FILE", None)
        if icon_pid is not None:
            try:
                ptag[icon_pid] = str(PLUGIN_ID)
            except Exception:
                pass
    else:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, ptag)
        report.append("XenoCam tag updated (settings kept)" if _has_controls(ptag) else "XenoCam tag added")
    build_tag_ui(ptag, old_values)
    focus = _cam_focus_object(cam)
    if focus is not None:
        report.append("focusing on the camera's Focus Object '%s'" % focus.GetName())
    _run_before_octane(doc, cam, ptag)
    doc.SetActiveTag(ptag)
    doc.EndUndo()
    c4d.EventAdd()
    if ok and not _restart_live_viewer():
        report.append("start the Live Viewer to compile the shader")
    _status("set up on '%s': %s." % (cam.GetName(), "; ".join(report)))


def export_shader(folder):
    path = os.path.join(folder, "XenoCam.osl")
    with open(path, "w", encoding="utf-8") as f:
        f.write(OSL_SOURCE)
    return path


# --------------------------------------------- start / restart the Live Viewer
OCTANE_START = 1033873    # Octane's "Start OctaneRender" (restarts it if it's running)


def _restart_live_viewer():
    """Octane compiles a new OSL camera, and links its inputs, reliably only when
    the Live Viewer (re)starts through it - pressing Compile from a plugin can
    leave the inputs unlinked. So set-up ends with Octane's own start command."""
    try:
        if c4d.plugins.FindPlugin(OCTANE_START, c4d.PLUGINTYPE_COMMAND) is not None:
            c4d.CallCommand(OCTANE_START)
            return True
    except Exception as e:
        print("XenoCam: could not restart the Live Viewer:", e)
    return False


def _hook_setup(doc, cam=None):
    setup_camera(doc, cam)


def _hook_copy(doc):
    c4d.CopyStringToClipboard(OSL_SOURCE)
    _status("shader code copied - paste it into the OSL Camera's Code field and press Compile")


def _hook_export(doc):
    folder = c4d.storage.LoadDialog(title="Folder for XenoCam.osl", flags=c4d.FILESELECT_DIRECTORY)
    if folder:
        _status("saved " + export_shader(folder))


class XenoCamCommand(c4d.plugins.CommandData):
    def Execute(self, doc):
        setup_camera(doc)
        return True


# ------------------------------------------------------ the XenoCam tag type
TAG_ID = 1000006          # Maxon test-range ID
AUTO_ID = 1000004         # Maxon test-range ID, for the auto set-up message
_TAG_OK = False
_AUTO_ASKED = set()

_RES_FILES = {
    "res/c4d_symbols.h": "enum\n{\n\t_DUMMY_ELEMENT_\n};\n",
    "res/description/Txenocam.h":
        "#ifndef _Txenocam_H_\n#define _Txenocam_H_\n\nenum\n{\n\tXENOCAM_DUMMY = 1000\n};\n\n#endif\n",
    "res/description/Txenocam.res": "CONTAINER Txenocam\n{\n\tNAME Txenocam;\n\tINCLUDE Tbase;\n}\n",
    "res/strings_en-US/description/Txenocam.str": "STRINGTABLE Txenocam\n{\n\tTxenocam \"XenoCam\";\n}\n",
    "res/strings_en-US/c4d_strings.str": "STRINGTABLE\n{\n}\n",
}


def _write_res():
    """The tag type needs a description resource; write it next to the plugin so
    XenoCam stays a single .pyp file."""
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "xenocam_res")
    for rel, text in _RES_FILES.items():
        path = os.path.join(base, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path) or open(path).read() != text:
            with open(path, "w") as f:
                f.write(text)
    return base


def _guid(node):
    try:
        return node.GetGUID()
    except Exception:
        return id(node)


def _has_controls(tag):
    for _did, bc in tag.GetUserDataContainer():
        if bc[c4d.DESC_NAME] == "Character":
            return True
    return False


def _walk(obj):
    while obj is not None:
        yield obj
        for o in _walk(obj.GetDown()):
            yield o
        obj = obj.GetNext()


class XenoCamTag(c4d.plugins.TagData):
    """Runs the XenoCam logic with no code tab."""

    def Init(self, node, *args):
        return True

    def AddToExecution(self, tag, prio_list):
        # early in the expression pass: after animation, before the Octane Camera tag
        prio_list.Add(tag, c4d.EXECUTIONPRIORITY_EXPRESSION - 100, 0)
        return True

    def Execute(self, tag, doc, op, bt, priority, flags):
        if not _has_controls(tag):
            # added from the Tags menu: set its camera up (on the main thread)
            key = _guid(tag)
            if key not in _AUTO_ASKED:
                _AUTO_ASKED.add(key)
                c4d.SpecialEventAdd(AUTO_ID)
            return c4d.EXECUTIONRESULT_OK
        try:
            _xc_runtime.run(tag, doc)
        except Exception as e:
            print("XenoCam tag:", e)
        return c4d.EXECUTIONRESULT_OK

    def Message(self, node, msg_type, data):
        if msg_type in (c4d.MSG_DESCRIPTION_COMMAND, c4d.MSG_DESCRIPTION_POSTSETPARAMETER):
            try:
                _xc_runtime.message(node, msg_type, data)
            except Exception as e:
                print("XenoCam tag:", e)
        return True


class XenoCamAutoSetup(c4d.plugins.MessageData):
    """A XenoCam tag added by hand sets up its own camera."""

    def CoreMessage(self, mid, bc):
        if mid != AUTO_ID:
            return True
        doc = c4d.documents.GetActiveDocument()
        for obj in list(_walk(doc.GetFirstObject())):
            for t in list(obj.GetTags()):
                if t.GetType() == TAG_ID and not _has_controls(t):
                    if obj.CheckType(c4d.Ocamera):
                        setup_camera(doc, obj)
                    else:
                        # a stray tag on a non-camera: take it off again (undoable) and say why, once
                        doc.StartUndo()
                        doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ, t)
                        t.Remove()
                        doc.EndUndo()
                        c4d.EventAdd()
                        _status("the XenoCam tag only works on a camera - removed it from '%s'" % obj.GetName())
        return True


def _register_tag(icon):
    global _TAG_OK
    try:
        base = _write_res()
        res = c4d.plugins.GeResource()
        if not res.Init(base):
            print("XenoCam: tag resource not loaded; using a Python tag instead")
            return
        _TAG_OK = bool(c4d.plugins.RegisterTagPlugin(
            id=TAG_ID, str="XenoCam", info=c4d.TAG_VISIBLE | c4d.TAG_EXPRESSION,
            g=XenoCamTag, description="Txenocam", icon=icon, res=res))
    except Exception as e:
        print("XenoCam: tag type not registered (%s); using a Python tag instead" % e)
        _TAG_OK = False


# ------------------------------------------------------------------ icon
ICON_PNG = """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
5BRO4RTqwn8Bu2XBvqHbwhYAAAAASUVORK5CYII="""


def _load_icon():
    data = base64.b64decode("".join(ICON_PNG.split()))
    for folder in (os.path.join(os.path.dirname(os.path.abspath(__file__)), "xenocam_res"),
                   os.path.join(tempfile.gettempdir(), "xenocam_res")):
        try:
            os.makedirs(folder, exist_ok=True)
            path = os.path.join(folder, "xenocam_icon.png")
            if not os.path.exists(path) or os.path.getsize(path) != len(data):
                with open(path, "wb") as f:
                    f.write(data)
            bmp = c4d.bitmaps.BaseBitmap()
            res = bmp.InitWith(path)
            if (res[0] if isinstance(res, tuple) else res) == c4d.IMAGERESULT_OK:
                return bmp
        except Exception:
            pass
    return None


if __name__ == "__main__":
    _icon = _load_icon()
    if _icon is not None:
        try:
            gui.RegisterIcon(PLUGIN_ID, _icon)
        except Exception:
            pass
    _register_tag(_icon)
    _xc_runtime.HOOKS = {"copy": _hook_copy, "export": _hook_export, "setup": _hook_setup}
    c4d.plugins.RegisterCommandPlugin(PLUGIN_ID, "XenoCam %s" % VERSION, 0, _icon,
                                      "Add XenoCam to the selected camera (or a new camera from the view)",
                                      XenoCamCommand())
    if _TAG_OK:
        c4d.plugins.RegisterMessagePlugin(AUTO_ID, "XenoCam auto set-up", 0, XenoCamAutoSetup())
