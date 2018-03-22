#ifndef __Make_DataBase__
#define __Make_DataBase__

#include <iostream>
#include <algorithm>
#include <fstream>
#include <stdio.h>
#include <math.h>
#include <string>
#include <map>
#include <vector>

using namespace std;



class CDataBase {
private:
	int wordsNum;
	map<string, int>  mxCnt,appearCnt;
	vector< pair<double, string> > v;
	inline string fresh(string s) {
		string s2;
		for (auto f : s) {
			if (f >= 'A' && f <= 'Z') s2.push_back(f - 'A' + 'a');
			else if (f >= 'a' && f <= 'z') s2.push_back(f);
		}
		return s2;
	}
	inline string i2s(int x) {
		if (x == 0) return "0";
		string s;
		while (x) {
			s.push_back(x % 10 + '0');
			x /= 10;
		}
		reverse(s.begin(), s.end());
		return s;
	}
	struct srt {
		bool operator()(pair<double, string> const &a, pair<double, string> const &b) {
			return a.first > b.first;
		}
	};
public:
	map<string, int> cnt[1000], total;
	int m_fileNum = 300;
	inline CDataBase() {
		this -> wordsNum = 0;
		return;
	}
	inline ~CDataBase() {
		return;
	}
	inline void build() {
		string outName = ".\\wordsWeight.txt";
		string outName2 = ".\\wordsTimes.txt";
		string outName3 = ".\\appearTimes.txt";
		fstream fout;
		fout.open(outName,ios::out);
		fout.close();
		fout.open(outName2,ios::out);
		fout.close();
		fout.open(outName3, ios::out);
		fout.close();

		for (int i = 1; i <= m_fileNum; i++) {
			string fileName = ".\\data\\report" + i2s(i) + ".txt";
			string s;
			fstream fin;
			fin.open(fileName.c_str(), ios::in);
			while (fin >> s) {
				s = fresh(s);
				if (s.empty()) continue;
				if (cnt[i].find(s) == cnt[i].end()) {
					appearCnt[s]++;
				}
				wordsNum++;
				total[s]++;
				cnt[i][s]++;
				mxCnt[s] = max(mxCnt[s], cnt[i][s]);
			}
			fin.close();
		}
		fout.open(outName3.c_str(), ios::out | ios::app);
		for (auto f : appearCnt) {
			fout << f.first << ' ' << f.second<<endl;
		}
		fout.close();
		fout.open(outName2.c_str(), ios::out | ios::app);
		v.clear();
		for (auto f : total) {
			v.push_back(make_pair(f.second, f.first));
		}
		sort(v.begin(), v.end(),srt());
		for (auto f : v) {
			fout << f.second << ' ' << f.first << endl;
		}
		fout.close();
		
		fout.open(outName.c_str(), ios::out | ios::app);
		v.clear();
		for (auto f : total){
			v.push_back(make_pair(mxCnt[f.first], f.first));
		}
		sort(v.begin(), v.end(), srt());
		for (auto &f : v) {

			int appearTime = 0;
			for (int j = 1; j <= m_fileNum; j++)
				if (cnt[j].find(f.second) != cnt[j].end()) appearTime++;

			double tf, idf;
			tf = (double)(f.first) / wordsNum;
			idf = log((double)(m_fileNum) / appearTime);
			f.first = tf*idf*sqrt(idf);

		}
		sort(v.begin(), v.end(), srt());
		for (auto f : v) {
			//cout << f.second << ' ' << f.first << endl;
			
			fout << f.second << ' ' << std::to_string(f.first) << endl;
		}
		fout.close();
		return;
	}

};


#endif