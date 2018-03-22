#ifndef __inputQuery__
#define __inputQuery__
#include <iostream>
#include <algorithm>
#include <fstream>
#include <stdio.h>
#include <math.h>
#include <string>
#include <map>
#include <vector>


using namespace std;

class CInputQuery {
private:
	int m_fileNum = 300;
	map<string, int> inputCnt,total,appearTime;
	int wordsNum;
	vector< pair<double, string> >inputV;
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
		bool operator()(const pair<double, string> &a, const pair<double, string> &b) {
			return a.first > b.first;
		}
	};
public:
	inline CInputQuery() {
		
	}
	inline ~CInputQuery() {

	}
	inline void readFile(string s) {
		string fileName = s;
		fstream fin;
		int x;
		this->wordsNum = 0;
		fin.open(fileName.c_str(), ios::in);
		while (fin >> s) {
			s = fresh(s);
			if (s.empty()) continue;
			wordsNum++;
			inputCnt[s]++;
		}
		fin.close();
		this->total.clear();
		fin.open("./wordsTimes.txt", ios::in);
		while (fin >> s>>x) {
			total[s] = x;
		}
		fin.close();
		fin.open("./appearTimes.txt", ios::in);
		while (fin >> s >> x) {
			appearTime[s] = x;
		}
		fin.close();
	}
	inline void askWeight() {
		inputV.clear();
		for (auto f : inputCnt) {
			
			double tf, idf;
			tf = (double)(f.second) / wordsNum;
			idf = log((double)(m_fileNum+1) / (appearTime[f.first]+1));
			//cout << f.first << ' ' << f.second << endl;
			//cout << tf << ' ' << idf << ' ' << appearTime[f.first]+1 << endl;
			inputV.push_back(make_pair(tf*idf, f.first));
		}
		sort(inputV.begin(), inputV.end(),srt());
		string outFile = "./resultWeight.txt";
		fstream fout;
		fout.open(outFile.c_str(), ios::out);
		fout.close();
		fout.open(outFile.c_str(), ios::out | ios::app);
		for (auto f : inputV) {
			fout << f.second << ' ' << std::to_string(f.first) << endl;
		}
		fout.close();
	}
	inline void askSize() {

	}

};
#endif