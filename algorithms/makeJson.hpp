#ifndef __Make_Json__
#define __Make_Json__

#include <iostream>
#include <fstream>
#include <string>
#include <stdio.h>
#include <algorithm>
#include <map>
#include <vector>

using namespace std;

class CJson {
private:
	typedef struct tagEDGE {
		string source, target;
		int val;
	}EDGE;
	typedef struct tagFEATURE {
		double weight;
		string word,type, cate;
		tagFEATURE(double w,string n,string t,string NER) {
			weight = w;
			word = n;
			type = t;
			cate = NER;
			return;
		}
	}feature;
	map<string, double> weight;
	vector<feature> v;
	inline string fresh(string s) {
		string s2;
		for (auto f : s) {
			if (f >= 'A' && f <= 'Z') s2.push_back(f - 'A' + 'a');
			else if (f >= 'a' && f <= 'z') s2.push_back(f);
			else if (f == '\'' || f == '-') s2.push_back(f);
		}
		return s2;
	}
	inline void readFile() {
		fstream fin;
		string s;
		double w;
		fin.open("algorithms/resultWeight.txt", ios::in);
		while (fin >> s >> w) {
			weight[s] = w;
		}
		fin.close();
		fin.open("algorithms/NER.txt", ios::in);
		while (getline(fin, s)) {

			string nowNER,nowType,nowWord;

			if (s.empty()) continue;
			if (s.size() < 3) continue;
			if ((!(s[2] != '(' && s.back() != ')')) && (!(s[2] == '(' && s.back() == ')'))) 
				continue;
			int lgcnt = 0,rgcnt=0;
			for (int i = 0; i < s[i]; i++) {
				if (s[i] == '(') lgcnt++;
				if (s[i] == ')') rgcnt++;
			}
			if (lgcnt > 1) 
				continue;
			if (rgcnt > 1) 
				continue;
			if (s[0] != ' ' || s[1] != ' ') {
				continue;
			}
			if (s[2] != '(' && s.back() == ')') s.pop_back();
			if (s[2] == '(') {
				int i;
				nowNER.clear();
				for (i = 3; s[i] != ' '; i++) {
					nowNER.push_back(s[i]);
				}
				
				while (1) {
					nowWord.clear();
					nowType.clear();
					for (i++; s[i] != '/'; i++) {
						nowWord.push_back(s[i]);
					}

					for (i++; s[i] != ')' && s[i] != ' '; i++) {
						nowType.push_back(s[i]);
					}
					if (weight.find(fresh(nowWord)) == weight.end()) {
						v.push_back(feature(0, nowWord, nowType, nowNER));
					}
					else {
						v.push_back(feature(weight[fresh(nowWord)], nowWord, nowType, nowNER));
					}
					if (s[i] == ')') break;
				}
			}
			else {
				int i;
				nowNER = "None";
				nowWord.clear();
				nowType.clear();
				for (i=2; s[i] != '/'; i++) {
					nowWord.push_back(s[i]);
				}

				for (i++; i<s.size() ; i++) {
					nowType.push_back(s[i]);
				}
				if (weight.find(fresh(nowWord)) == weight.end()) {
					v.push_back(feature(0, nowWord, nowType, nowNER));
				}
				else {
					v.push_back(feature(weight[fresh(nowWord)], nowWord, nowType, nowNER));
				}
			}
			
			
		}
		fin.close();
	}
	map<pair<string,string>, int> num;
	vector<EDGE> vEdge;
	inline int word2Num(pair<string,string> s) {
		if (num.find(s) != num.end()) return num[s];
		else {
			num[s] = num.size();
			return num[s];
		}
	}
	inline void addEdge(feature fa, feature fb) {
		int a, b;
		a = word2Num(make_pair(fa.word, fa.cate));
		b = word2Num(make_pair(fb.word, fb.cate));
		if (a == b) return;
		EDGE e;
		e.source = fa.word;
		e.target = fb.word;
		e.val = 1;
		vEdge.push_back(e);
	}
	inline void findConnect() {
		vector<feature> isPerson, isCate;
		for (int i = 0; i < v.size(); i++) {
			feature f = v[i];
			if (f.word == "." || f.word == "?" || f.word == "!") {
				if (isPerson.empty()) {
					for (int i = 0; i < isCate.size(); i++) {
						for (int j = i + 1; j < isCate.size(); j++) {
							addEdge(isCate[i], isCate[j]);
							addEdge(isCate[j], isCate[i]);
						}
					}
				}
				else {
					for (auto p : isPerson) {
						for (auto c : isCate) {
							addEdge(p, c);
						}
					}
					for (int i = 0; i < isPerson.size(); i++) {
						for (int j = i + 1; j < isPerson.size(); j++) {
							addEdge(isPerson[i], isPerson[j]);
							addEdge(isPerson[j], isPerson[i]);
						}
					}
				}
				isPerson.clear();
				isCate.clear();
			}
			else {
				if (f.cate != "None") {
					if (f.cate == "per") {
						isPerson.push_back(f);
					}
					else {
						isCate.push_back(f);
					}
				}
			}
		}
	}
	map<string, int> cateMap;
	inline int class2Num(string s) {
		if (s == "None") return 0;
		else {
			if (cateMap.find(s) != cateMap.end()) return cateMap[s];
			else {
				cateMap[s] = cateMap.size();
				return cateMap[s];
			}
		}
	}
public:
	inline CJson() {
		return;
	}
	inline ~CJson() {
		return;
	}
	

	inline void makeJson() {
		readFile();
		findConnect();
		
		// Json.txt

		fstream fout;
		fout.open("algorithms/Json.txt",ios::out);
		fout.close();
		fout.open("algorithms/Json.txt", ios::out | ios::app);
		fout << '['<<endl;
		for (int i = 0; i < v.size();i++) {
			feature f = v[i];
			fout << '{';
			fout << "\"word\"" << ":" << "\"" << f.word << "\"" << ',';
			fout << "\"weight\"" << ":" << "\"" << to_string(f.weight) << "\"" << ',';
			fout << "\"type\"" << ":" << "\"" << f.type << "\"" << ',';
			fout << "\"cate\"" << ":" << "\"" << f.cate << "\"" << '}';
			if (i < v.size() - 1) fout << ',';
			fout << endl;
		}
		fout << ']';
		fout.close();
		

		// graph.js

		// fstream fout;
		fout.open("public/graph.js", ios::out);
		fout.close();
		fout.open("public/graph.js", ios::out | ios::app);
		fout << "var graph = {" << endl;
		fout << "  \"nodes\": [" << endl;
		int cnt = 0;
		for (auto f : num) {
			fout << "    {\"id\": \"" << f.first.first << "\", \"group\" : " << class2Num(f.first.second)<<"}";
			if (cnt < num.size() - 1) fout << ",";
			fout << endl;
			cnt++;
		}
		fout << "  ]," << endl << "  \"links\": [" << endl;
		cnt = 0;
		for (auto f : vEdge) {
			fout << "    {\"source\": \"" << f.source << "\", \"target\" : \"" << f.target << "\", \"value\" : " << f.val << "}";
			if (cnt < vEdge.size() - 1) fout << ",";
			fout << endl;
			cnt++;
		}
		fout << "  ]" << endl << "}";
		fout.close();
	}
};
#endif 
