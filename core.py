#########################################################################
# File Name: core.py
# > Author: CaoYinghao
# > Mail: caoyinghao@gmail.com 
# Created Time: Thu May 16 10:05:37 2024
#########################################################################
#! /usr/bin/python

import collections
from numpy import log2,sqrt,nan_to_num

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
                    3:"H/E", # 1 and 2
                    4:"PubChem",
                    5:"H/P", # 1 and 4
                    6:"E/P", # 2 and 4
                    7:"H/E/P" # 1 and 2 and 4
                    }
        pass

    ### get molecular weight by polarity
    @staticmethod
    def getIon(mz, polarity):
        func = 1 if polarity == "+" else -1
        newmz = mz - (SearchModel.IONS['H_mass'] - SearchModel.IONS['E_mass']) * func
        return newmz


    ### ac atom
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

    ### convert symbol to atom from database
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

    ### main interface for smart, return candidate list 
    def search(self,mz,iontag,cur,ppm_error=5,lr=None,verbose=False):
        mz = float(mz)
        ppm_error = float(ppm_error)
        if iontag == 1:
            mz = SearchModel.getIon(mz,"-")
        elif iontag == 0:
            mz = SearchModel.getIon(mz,"+")

        ### search in coreset
        res = self.search_detail(mz,cur,False,ppm_error,lr,verbose)
        #print(res,mz)
        #exit()
        ### search in bioextensionset from coreset
        #extres = self.search_detail(mz,cur,True,ppm_error,lr,verbose)
        #print(res[0])
        #print(extres[0])

        ### result merge by weight
        #lastres = self.merge(res,extres)
        lastres = res
        #exit()
        if len(lastres) == 0:
            return [""]
        res1 = []
        #for i in sorted(lastres,key=lambda x:-int(x[-1])):
        #for i in sorted(res,key=lambda x:-int(x[-1])):
        for i in lastres:
            s, s1 = self.convertCodeToAtom(i[2], self.codes1)
            tag = self.tag[i[3]]
            res1.append([i[0],s1,i[6],i[7],round(i[-1],3),tag])
            #break
        return res1
        pass


    ### main function for formula assignment, 5 sqls should be performed
    def search_detail(self,mz,cur,exttag,ppm,lr,verbose):
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
        hmzs = {}
        dicts = collections.defaultdict(dict)
        hweight = collections.defaultdict(int)
        hbiofreqweight = collections.defaultdict(float)
        hfreqweight = collections.defaultdict(float)

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
            hmzs[i[0]] = float(i[2])
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
        sql5 = "select * from link{0:d} as b,  shift as c where b.nodeid between {1:d} and {2:d} and c.id = b.linkid;".format(startedge, mins, maxs)
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

        #w = collections.defaultdict(dict)
        for fromid in dicts:
            vlen = len(dicts[fromid])
            for toid in dicts[fromid]:
                #if toid not in w:
                #    w[toid] = collections.defaultdict(int)
                #w[toid][codes[isref[fromid]]] += 1
                tag = dicts[fromid][toid][0]
                hweight[toid] += codes[isref[fromid]]
                if tag != -1:
                    hbiofreqweight[toid] += 1
                else:
                    hfreqweight[toid] += 1
        lists = []
        maxsn = -1
        maxsc = -1
        maxbio = -1
        maxdb = -1
        maxppm = -1
        for i in hmzs:
            #if i in used:
            #    if i not in used_3:
            #        used_3[i] = 0
            #    if i not in used_4:
            #        used_4[i] = 0
            #    if i not in used_de:
            #        used_de[i] = 0
            ppm = round(abs(hmzs[i]-mz)/mz * 1e6,3)
            if maxsn <= hweight[i]:
                maxsn = hweight[i]
            if maxsc <= istargetref[i]:
                maxsc = istargetref[i]
            if maxbio <= hbiofreqweight[i]:
                maxbio = hbiofreqweight[i]
            if maxdb <= hfreqweight[i]:
                maxdb = hfreqweight[i]
            if maxppm <= ppm:
                maxppm = ppm
            lists.append([i,hweight[i],used[i],istargetref[i],hbiofreqweight[i],hfreqweight[i],hmzs[i],ppm])
        c = 0
        lists = sorted(lists,key = lambda x:-(int(x[1]) + x[3] +  x[4] + x[5]))
        forms = []
        used = {}
        #print(maxsn,maxsc,maxbio,maxdb)
        for target in lists[:10000]:
            hid = target[0]
            if hid in used:continue
            used[hid] = ""
            xs = []
            if maxsn != 0:
                xs.append(target[1]/maxsn)
            else:
                xs.append(0)
            #if maxsc != 0:
            #    xs.append(target[3]/maxsc)
            #else:
            #    xs.append(0)
            if maxbio != 0:
                xs.append(target[4]/maxbio)
            else:
                xs.append(0)
            if maxdb != 0:
                xs.append(target[5]/maxdb)
            else:
                xs.append(0)
            if maxppm != 0:
                xs.append(target[-1]/maxppm)
            else:
                xs.append(0)
            xs = nan_to_num(xs)
            y_pred = lr.predict([xs])
            target.extend(xs)
            target.append(float(y_pred[0]))
            forms.append(target)
        forms = sorted(forms,key=lambda x:-float(x[-1]))
        return forms[:3]
        pass

    ### merge all results with weight
    ### Only coreset and bioextension from coreset were included, since other sets were huge for review.
    def merge(self,res,extres):
        weight = [8,0.1]
        dicts = collections.defaultdict(float)
        vals = collections.defaultdict(list)
        tempdict = collections.defaultdict(int)
        lists = []
        for i in res:
            dicts[i[2]] += weight[0] * float(i[-1])
            vals[i[2]] = i[:-1]
        for i in extres:
            dicts[i[2]] += weight[1] * float(i[-1])
            vals[i[2]] = i[:-1]
        c = 0
        #print(vals)
        #print(extres)
        for i in sorted(dicts,key=lambda x:-dicts[x]):
        #    print(i)
            vals[i].append(dicts[i])
            lists.append(vals[i])
            c += 1
        return lists

        pass

if __name__ == "__main__":
    sm = SearchModel()
    pass
