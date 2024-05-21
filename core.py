#########################################################################
# File Name: core.py
# > Author: CaoYinghao
# > Mail: caoyinghao@gmail.com 
# Created Time: Thu May 16 10:05:37 2024
#########################################################################
#! /usr/bin/python

import collections
from numpy import log2,sqrt
class SearchModel(object):
    IONS = {
    "H_mass": 1.00782503224,  # 1.0078250319,
    "E_mass": 0.00054857990943
    }
    def __init__(self):

        self.codes,self.codes1 = self.readCodes()
        # print("hello")
        self.tag = {0:"Unknown",
                    1:"HMDB",
                    2:"chEMBL",
                    3:"H/E",
                    4:"PubChem",
                    5:"H/P",
                    6:"E/P",
                    7:"H/E/P"
                    }
        pass

    @staticmethod
    def getIon(mz, polarity):
        func = 1 if polarity == "+" else -1
        newmz = mz - (SearchModel.IONS['H_mass'] - SearchModel.IONS['E_mass']) * func
        return newmz


    def readCodes(self):
        codes = {}
        codes1 = {}
        cstr = """0	Ac
1	Ag
2	Al
3	Am
4	Ar
5	As
6	At
7	Au
8	B
9	Ba
10	Be
11	Bh
12	Bi
13	Bk
14	Br
15	C
16	Ca
17	Cd
18	Ce
19	Cf
20	Cl
21	Cm
22	Co
23	Cr
24	Cs
25	Cu
26	Db
27	Dy
28	Er
29	Es
30	Eu
31	F
32	Fe
33	Fm
34	Fr
35	Ga
36	Gd
37	Ge
38	H
39	He
40	Hf
41	Hg
42	Ho
43	Hs
44	I
45	In
46	Ir
47	K
48	Kr
49	La
50	Li
51	Lr
52	Lu
53	Md
54	Mg
55	Mn
56	Mo
57	Mt
58	N
59	Na
60	Nb
61	Nd
62	Ne
63	Ni
64	No
65	Np
66	O
67	Os
68	P
69	Pa
70	Pb
71	Pd
72	Pm
73	Po
74	Pr
75	Pt
76	Pu
77	Ra
78	Rb
79	Re
80	Rf
81	Rh
82	Rn
83	Ru
84	S
85	Sb
86	Sc
87	Se
88	Sg
89	Si
90	Sm
91	Sn
92	Sr
93	Ta
94	Tb
95	Tc
96	Te
97	Th
98	Ti
99	Tl
100	Tm
101	U
102	V
103	W
104	Xe
105	Y
106	Yb
107	Zn
108	Zr"""
        for i in cstr.split("\n"):
            parts = i.split("\t")
            codes[parts[1]] = parts[0]
            codes1[parts[0]] = parts[1]
        return codes, codes1

    def convertCodeToAtom(self,form, codes):
        a, b = form.split("_")
        s = ""
        a1 = []
        for j, k in zip(a.split("-"), b.split("-")):
            a1.append(codes[j])
            if int(k) > 1:
                s += codes[j] + k
            else:
                s += codes[j]
        return "-".join(a1) + "_" + b, s

    def search(self,mz,iontag,cur,exttag,ppm_error=5,verbose=False):
        mz = float(mz)
        ppm_error = float(ppm_error)
        if iontag == 1:
            mz = SearchModel.getIon(mz,"-")
        elif iontag == 0:
            mz = SearchModel.getIon(mz,"+")
        res = self.search_detail(mz,cur,exttag,ppm_error,verbose)
        if len(res) == 0:
            return [""]
        res1 = []
        for i in sorted(res,key=lambda x:-int(x[-1])):
            s, s1 = self.convertCodeToAtom(i[3], self.codes1)
            tag = self.tag[i[4]]
            res1.append([i[0],s1,i[7],i[-2],round(i[-1],3),tag])
        return res1
        pass

    # a simple version to search against the coreset in smart-database.
    def search_detail(self,mz,cur,exttag,ppm,verbose):
        mzl = mz - ppm / 1e6 * mz
        mzh = mz + ppm / 1e6 * mz
        sql1 = "select node from dbindex as a where a.start <= {0:.5f} and a.end >= {1:.5f};".format(mzh,mzl)
        if verbose:
            print("sql1",sql1)
        cur.execute(sql1)
        res = cur.fetchone()
        nodefile = ""
        isref = {}
        istargetref = {}
        used = {}
        used_all = {}
        dicts = collections.defaultdict(dict)
        edges = collections.defaultdict(dict)
        used_de = collections.defaultdict(int)
        used_3 = collections.defaultdict(int)
        used_4 = collections.defaultdict(int)

        if verbose:
            print(nodefile,mzl,mzh)


        codes = {0: 0, 1: 1, 2: 1, 3: 2, 4: 1, 5: 2, 6: 2, 7: 3}
        for i in res:
            nodefile = i

        sql2 = ("select id,name,mz,isref from {0:s} as a where a.mz between"
                " {1:.5f} and {2:.5f} and isref != '0';").format(nodefile, mzl, mzh)
        if exttag:
            sql2 = ("select id,name,mz,isref from {0:s} as a where a.mz between"
                    " {1:.5f} and {2:.5f};").format(nodefile, mzl, mzh)
        # sql2 = ("select distinct isref from {0:s} as a where a.mz between"
        #         " {1:.5f} and {2:.5f};").format(nodefile, mzl, mzh)
        # sql2 = "select * from node0 where mz between 103.06 and 103.07";

        if verbose:
            print("sql2",sql2,mz)
        cur.execute(sql2)
        res = cur.fetchall()
        nodes = []
        for i in res:
            nodes.append(i[0])
            istargetref[i[0]] = i[3]
            used_all[i[0]] = float(i[2])
            used[i[0]] = i[1]
            # print("hello",i)
        if verbose:
            print("nodes",nodes)
        if len(nodes) == 0:
            return []
        mins = min(nodes)
        maxs = max(nodes)
        startedge = -1
        endedge = -1

        sql3 = "select * from node_edge as a where a.nodestartid <= {0:d} and a.nodeendid >= {0:d}".format(mins)
        if verbose:
            print("sql3",sql3)
        cur.execute(sql3)
        res = cur.fetchall()
        for i in res:
            if verbose:
                print('start', i)
            startedge = i[0]
        sql4 = "select * from node_edge as a where a.nodestartid <= {0:d} and a.nodeendid >= {0:d}".format(maxs)
        if verbose:
            print("sql4",sql4)
        cur.execute(sql4)
        res = cur.fetchall()
        for i in res:
            if verbose:
                print('end', i)
            endedge = i[0]
        if startedge != endedge:
            if verbose:
                print("Error")
        if verbose:
            print("start end",startedge,endedge)
        sql5 = "select * from link{0:d} as b,  shift as c where b.nodeid between {1:d} and {2:d} and c.id = b.linkid;".format(
            startedge, mins, maxs)
        if verbose:
            print("sql5",sql5)
        cur.execute(sql5)
        res = cur.fetchall()
        c = 0
        for i in res:
            if c < 1:
                if verbose:
                    print(i)
            c += 1
            dicts[i[0]][i[3]] = [i[8],i[7],i[4]]

            isref[i[0]] = i[1]

        for i in dicts:
            vlen = len(dicts[i])
            for j in dicts[i]:
                tag = dicts[i][j][0]
                if vlen > 1:
                    edges[i][j] = tag
                used_de[j] += codes[isref[i]]
                if tag != -1:
                    used_3[j] += 1
                else:
                    used_4[j] += 1
        lists = []
        for i in used_all:
            if i in used:
                if i not in used_3:
                    used_3[i] = 0
                if i not in used_4:
                    used_4[i] = 0
                if i not in used_de:
                    used_de[i] = 0
                ppm = round(abs(used_all[i]-mz)/mz * 1e6,3)
                lists.append([i,used_de[i],used[i],istargetref[i],used_3[i],used_4[i],used_all[i],ppm])
        res = []
        sup = 0.01
        if exttag:
            sup = sqrt(mz/100)
        c = 0
        for i in sorted(lists,key=lambda x:-(int(x[1])/(x[-1] + sup) + x[3] + x[4]/10 + x[5]/50)):
            if c < 15:
                score = log2(int(i[1])/(i[-1] + sup) + i[3] + i[4]/10 + i[5]/50 + 0.5)
                res.append([c,i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],score])
            else:
                break
            c += 1
        return res
        pass

if __name__ == "__main__":
    sm = SearchModel()
    pass
