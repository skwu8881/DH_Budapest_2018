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
		fin.open("./resultWeight.txt", ios::in);
		while (fin >> s >> w) {
			weight[s] = w;
		}
		fin.close();
		fin.open("./NER.txt", ios::in);
		while (getline(fin, s)) {
			string nowNER,nowType,nowWord;

			if (s.empty()) continue;
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
			}
			
			if (weight.find(fresh(nowWord)) == weight.end()) {
				v.push_back(feature(0, nowWord, nowType, nowNER));
			}
			else {
				v.push_back(feature(weight[fresh(nowWord)], nowWord, nowType, nowNER));
			}
		}
		fin.close();
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
		fstream fout;
		fout.open("./Json.txt",ios::out);
		fout.close();
		fout.open("./Json.txt", ios::out | ios::app);
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
	}
};
#endif 